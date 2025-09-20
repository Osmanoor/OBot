from fastapi import FastAPI, Request, Form, Depends, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio
import queue
from sqlalchemy.orm import Session
from typing import Optional
from contextlib import asynccontextmanager
from datetime import datetime

from . import database, auth
from .workflows import trade_initiator, price_updater, peak_alerter
from .scheduler import setup_scheduler
from .websocket import manager
from .workflows.weekly_reporter import run_weekly_report
from .workflows.monthly_reporter import run_monthly_report
from .workflows.yearly_reporter import run_yearly_report


# Create a shared queue for communication between the producer and consumer
peak_queue = queue.Queue()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("Application startup...")
    database.init_db()
    print("Database initialized.")
    
    scheduler = setup_scheduler()
    scheduler.start()
    print("Scheduler started.")

    # Start the background tasks
    db_session = database.SessionLocal()
    
    # Start the background tasks and keep a reference to them
    tasks = [
        asyncio.create_task(price_updater.run_price_updater(peak_queue)),
        asyncio.create_task(peak_alerter.run_peak_alerter(db_session, peak_queue))
    ]
    print("Background tasks (price_updater, peak_alerter) started.")
    
    # # It's better to run one-off tasks like this without blocking startup
    # asyncio.create_task(run_weekly_report())
    # asyncio.create_task(run_monthly_report())
    # asyncio.create_task(run_yearly_report())
    
    yield
    
    # Code to run on shutdown
    print("Application shutdown...")
    
    # Cancel all background tasks
    for task in tasks:
        task.cancel()
    
    # Wait for tasks to be cancelled
    await asyncio.gather(*tasks, return_exceptions=True)
    print("Background tasks cancelled.")
    
    scheduler.shutdown()
    db_session.close()
    print("Scheduler and DB session closed.")

app = FastAPI(title="Option Trading Bot", lifespan=lifespan)

# Mount static files directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup for HTML templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(database.get_db), user: str = Depends(auth.get_current_user)):
    """
    Serves the main dashboard, protected by authentication.
    """
    active_trades = db.query(database.Trade).filter(database.Trade.status == database.TradeStatus.ACTIVE).all()
    return templates.TemplateResponse("index.html", {"request": request, "trades": active_trades})

# Endpoint to receive the new trade data from the form
@app.post("/trade", response_class=HTMLResponse)
async def create_trade(
    request: Request,
    db: Session = Depends(database.get_db),
    user: str = Depends(auth.get_current_user),
    trade_type: str = Form(...),
    symbol: str = Form(...),
    strike: Optional[str] = Form(None),
    expiration: Optional[str] = Form(None),
    min_volume: Optional[str] = Form(None),
    min_price: Optional[str] = Form(None),
    max_price: Optional[str] = Form(None)
):
    """
    Receives form data and triggers the trade initiation workflow.
    """
    form_data = {
        "trade_type": trade_type,
        "symbol": symbol,
        "strike": strike,
        "expiration": expiration,
        "min_volume": min_volume,
        "min_price": min_price,
        "max_price": max_price
    }
    
    # Await the result of the workflow to handle success or failure
    error_message = await trade_initiator.initiate_trade(form_data, db)
    
    if error_message:
        return templates.TemplateResponse("trade_error.html", {
            "request": request,
            "error_message": error_message
        })
    
    # If successful, show the success page
    return templates.TemplateResponse("trade_submitted.html", {
        "request": request,
        "data": form_data
    })

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/trade/{trade_id}/close", response_class=HTMLResponse)
async def close_trade(
    request: Request,
    trade_id: int,
    db: Session = Depends(database.get_db),
    user: str = Depends(auth.get_current_user)
):
    """
    Manually closes an active trade.
    """
    trade = db.query(database.Trade).filter(database.Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    if trade.status == database.TradeStatus.ACTIVE:
        trade.status = database.TradeStatus.CLOSED
        trade.exit_price = trade.current_price
        trade.closed_at = datetime.utcnow()
        trade.close_reason = f"Manually closed by user {user}"
        db.commit()

        # Notify clients to remove the trade from the active table
        await manager.broadcast({
            "type": "trade_closed",
            "trade_id": trade_id
        })

    # Redirect back to the main page
    return RedirectResponse(url="/", status_code=303)

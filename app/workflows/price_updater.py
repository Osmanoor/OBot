import asyncio
import queue
import random
from sqlalchemy.orm import Session
from datetime import datetime

from .. import database
from ..services.marketdata_service import marketdata_service
from ..websocket import manager

async def fetch_and_process_quote(trade: database.Trade):
    """
    Helper function to fetch a quote and apply randomization.
    Runs the synchronous API call in a separate thread to avoid blocking.
    """
    params = {
        "strike": trade.strike,
        "side": trade.trade_type.value.lower(),
        "expiration": trade.expiration_date.strftime('%Y-%m-%d')
    }
    
    # Run the synchronous requests call in a thread pool
    quote = await asyncio.to_thread(
        marketdata_service.get_option_quote, trade.underlying, params
    )

    if quote and quote.get("mid"):
        # --- FOR TESTING: Randomize the mid price ---
        original_mid = quote["mid"]
        randomized_mid = original_mid * random.uniform(0.7, 1.8) # +/- 2% change
        quote["mid"] = round(randomized_mid, 2)
        # --- END TESTING CODE ---
        return trade.id, quote
    
    return trade.id, None

async def run_price_updater(peak_queue: queue.Queue):
    """
    Continuously fetches price updates for all active trades concurrently.
    """
    print("Starting price updater...")
    while True:
        db_session = None
        try:
            db_session = database.SessionLocal()
            active_trades = db_session.query(database.Trade).filter(database.Trade.status == database.TradeStatus.ACTIVE).all()
            
            if not active_trades:
                await asyncio.sleep(1)
                continue

            # Create a list of concurrent tasks
            tasks = [fetch_and_process_quote(trade) for trade in active_trades]
            results = await asyncio.gather(*tasks)

            # Process results
            for trade_id, quote in results:
                if quote:
                    # Use get() for efficient lookup by primary key
                    trade = db_session.get(database.Trade, trade_id)
                    if not trade:
                        continue

                    new_price = quote["mid"]
                    print(f"{trade.symbol}: {new_price}")
                    if new_price != trade.current_price:
                        trade.current_price = new_price
                        is_new_peak = new_price > trade.peak_price_today
                        
                        if is_new_peak:
                            trade.peak_price_today = new_price
                        
                        await manager.broadcast({
                            "type": "price_update",
                            "trade_id": trade.id,
                            "current_price": new_price,
                            "peak_price": trade.peak_price_today
                        })

                        if is_new_peak:
                            print(f"New peak for {trade.symbol}: {new_price}")
                            peak_queue.put(trade.id)

            db_session.commit()

        except Exception as e:
            print(f"Error in price updater loop: {e}")
            if db_session:
                db_session.rollback()
        finally:
            if db_session:
                db_session.close()
        
        await asyncio.sleep(1)
import asyncio
import base64
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func

from .. import database
from ..services.telegram_service import telegram_service
from ..services.local_image_generator import image_generator
from ..services.report_templates import get_report_svg, wrap_svg_in_html
from ..config import settings

async def run_yearly_report():
    """
    Generates and sends a yearly report for all trades closed in the last year.
    """
    print("Running yearly report...")
    db = database.SessionLocal()
    try:
        today = date.today()
        first_day_of_year = today.replace(day=1, month=1)

        trades_this_year = db.query(database.Trade).filter(
            database.Trade.status == database.TradeStatus.CLOSED,
            func.date(database.Trade.closed_at) >= first_day_of_year,
            func.date(database.Trade.closed_at) <= today
        ).all()

        if not trades_this_year:
            print("No trades closed this year. Yearly report complete.")
            return

        # 1. Aggregate data and prepare trade rows
        summary = {
            "total_trades": len(trades_this_year),
            "winning_trades": 0,
            "losing_trades": 0,
            "total_profit": 0.0,
            "total_loss": 0.0,
        }
        trade_rows = []

        for trade in trades_this_year:
            profit = (trade.exit_price or 0) - trade.entry_price
            is_winner = profit > 0
            
            if is_winner:
                summary["winning_trades"] += 1
                summary["total_profit"] += profit
            else:
                summary["losing_trades"] += 1
                summary["total_loss"] += profit

            trade_rows.append({
                "symbol": trade.underlying,
                "entryPrice": f"{trade.entry_price:.2f}",
                "peakPrice": f"{trade.exit_price:.2f}",
                "isWinner": is_winner,
            })

        # 2. Prepare summary data for the template
        summary["total_profit"] *= 100
        summary["total_loss"] *= 100
        
        year = today.year

        try:
            with open(settings.BACKGROUND_IMAGE_PATH, "rb") as image_file:
                background_image_b64 = base64.b64encode(image_file.read()).decode("utf-8")
        except FileNotFoundError:
            print(f"Background image not found at {settings.BACKGROUND_IMAGE_PATH}. Using empty background.")
            background_image_b64 = ""

        summary_data_for_template = {
            **summary,
            "date_range": f"Year {year}",
            "bot_name": settings.BOT_NAME,
            "background_image_b64": background_image_b64
        }

        # 3. Generate the report SVG and render it
        report_svg = get_report_svg(summary_data_for_template, trade_rows, "التقرير السنوي")
        report_html = wrap_svg_in_html(report_svg)
        
        report_pdf = await image_generator.generate_pdf(report_html)

        # 4. Send the report to Telegram
        if report_pdf:
            today_str = datetime.now().strftime("%Y")
            file_name = f"yearly_report_{today_str}.pdf"
            telegram_service.send_document(
                document_data=report_pdf,
                filename=file_name,
                caption="التقرير السنوي"
            )
            print("Sent yearly report to Telegram.")

    except Exception as e:
        print(f"An error occurred during the yearly report: {e}")
    finally:
        db.close()
import asyncio
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func

from .. import database
from ..services.telegram_service import telegram_service
from ..services.local_image_generator import image_generator
from ..services.svg_templates import get_weekly_report_svg, wrap_svg_in_html
from ..config import settings

async def run_weekly_report():
    """
    Generates and sends a weekly report for all trades closed in the last 7 days.
    """
    print("Running weekly report...")
    db = database.SessionLocal()
    try:
        start_date = date.today() - timedelta(days=7)
        trades_last_week = db.query(database.Trade).filter(
            database.Trade.status == database.TradeStatus.CLOSED,
            func.date(database.Trade.closed_at) >= start_date
        ).all()

        if not trades_last_week:
            print("No trades closed in the last 7 days. Weekly report complete.")
            return

        # 1. Aggregate data and prepare trade rows
        summary = {
            "total_trades": len(trades_last_week),
            "winning_trades": 0,
            "losing_trades": 0,
            "total_profit": 0.0,
            "total_loss": 0.0,
        }
        trade_rows = []

        for trade in trades_last_week:
            profit = (trade.exit_price or 0) - trade.entry_price
            is_winner = profit > 0
            
            if is_winner:
                summary["winning_trades"] += 1
                summary["total_profit"] += profit * 100 # Assuming 100 shares per contract
            else:
                summary["losing_trades"] += 1
                summary["total_loss"] += profit * 100

            trade_rows.append({
                "symbol": trade.underlying,
                "entryPrice": f"{trade.entry_price:.2f}",
                "peakPrice": f"{trade.exit_price:.2f}",
                "isWinner": is_winner,
            })

        # 2. Prepare summary data for the template
        today = datetime.now()
        to_date = today.strftime('%B %d')
        from_date = (today - timedelta(days=6)).strftime('%d')
        summary_data_for_template = {
            **summary,
            "date_range": f"{from_date} - {to_date}, {today.year}",
            "bot_name": settings.BOT_NAME,
            "background_image_b64": settings.BACKGROUND_IMAGE_B64
        }

        # 3. Generate the report SVG and render it
        report_svg = get_weekly_report_svg(summary_data_for_template, trade_rows)
        report_html = wrap_svg_in_html(report_svg)
        
        report_image = await image_generator.generate_image(
            report_html, {'width': 830, 'height': 1000}
        )

        # 4. Send the report to Telegram
        if report_image:
            telegram_service.send_photo(
                photo_data=report_image, 
                caption="Weekly Performance Report"
            )
            print("Sent weekly report to Telegram.")

    except Exception as e:
        print(f"An error occurred during the weekly report: {e}")
    finally:
        db.close()
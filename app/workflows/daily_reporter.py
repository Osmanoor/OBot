import asyncio
import base64
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import func

from .. import database
from ..services.telegram_service import telegram_service
from ..services.local_image_generator import image_generator
from ..services.svg_templates import get_daily_report_html
from ..config import settings

async def run_daily_report():
    """
    Generates and sends a daily report for all trades closed today.
    """
    print("Running daily report...")
    db = database.SessionLocal()
    try:
        today = date.today()
        # Query for trades where the 'closed_at' date is today
        trades_closed_today = db.query(database.Trade).filter(
            database.Trade.status == database.TradeStatus.CLOSED,
            func.date(database.Trade.closed_at) == today
        ).all()

        if not trades_closed_today:
            print("No trades closed today. Daily report complete.")
            return

        print(f"Found {len(trades_closed_today)} trades closed today.")

        for trade in trades_closed_today:
            is_successful = (trade.exit_price or 0) > trade.entry_price
            
            # Decode hex strings from DB back to bytes, then encode to base64 for HTML
            try:
                entry_image_b64 = base64.b64encode(bytes.fromhex(trade.entry_image)).decode('utf-8')
                peak_image_b64 = base64.b64encode(bytes.fromhex(trade.peak_image)).decode('utf-8')
            except (ValueError, TypeError):
                print(f"Skipping trade {trade.id} due to invalid image data.")
                continue

            # Generate the report HTML
            report_html = get_daily_report_html(
                is_successful=is_successful,
                entry_image_b64=entry_image_b64,
                peak_image_b64=peak_image_b64,
                background_image_b64=settings.BACKGROUND_IMAGE_B64
            )

            # Render the HTML to a PNG
            report_image = await image_generator.generate_image(
                report_html, {'width': 632, 'height': 500}
            )

            if report_image:
                # Calculate profit percentage for the caption
                profit_percent = 0
                if trade.entry_price > 0:
                    profit_percent = ((trade.exit_price - trade.entry_price) / trade.entry_price) * 100
                
                status_text = "ناجحة" if is_successful else "خاسرة"
                caption = (
                    f"صفقة {trade.underlying} {status_text}\n"
                    f"سعر الدخول: {trade.entry_price:.2f}\n"
                    f"سعر الخروج: {trade.exit_price:.2f}\n"
                    f"النسبة: {profit_percent:.1f}%"
                )
                
                telegram_service.send_photo(photo_data=report_image, caption=caption)
                print(f"Sent daily report for trade {trade.id}")
            
            # Avoid overwhelming the APIs
            await asyncio.sleep(1)

    except Exception as e:
        print(f"An error occurred during the daily report: {e}")
    finally:
        db.close()

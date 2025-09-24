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
            # New success criteria: Did the peak price reach the first goal?
            first_goal_price = trade.entry_price * (1 + settings.GOAL_1_PERCENT / 100)
            is_successful = trade.peak_price_today >= first_goal_price

            # Decode hex strings from DB back to bytes, then encode to base64 for HTML
            try:
                entry_image_b64 = base64.b64encode(bytes.fromhex(trade.entry_image)).decode('utf-8')
                peak_image_b64 = base64.b64encode(bytes.fromhex(trade.peak_image)).decode('utf-8')
            except (ValueError, TypeError):
                print(f"Skipping trade {trade.id} due to invalid image data.")
                continue

            # Read and encode the background image
            try:
                with open(settings.BACKGROUND_IMAGE_PATH, "rb") as image_file:
                    background_image_b64 = base64.b64encode(image_file.read()).decode("utf-8")
            except FileNotFoundError:
                print(f"Background image not found at {settings.BACKGROUND_IMAGE_PATH}. Using empty background.")
                background_image_b64 = ""

            # Generate the report HTML
            report_html = get_daily_report_html(
                is_successful=is_successful,
                entry_image_b64=entry_image_b64,
                peak_image_b64=peak_image_b64,
                background_image_b64=background_image_b64
            )

            # Render the HTML to a PNG
            report_image = await image_generator.generate_image(
                report_html, {'width': 632, 'height': 500}
            )

            if report_image:
                # Calculate profit percentage for the caption
                profit_percent = 0
                price_for_calculation = trade.peak_price_today if is_successful else trade.exit_price
                price_type_text = "الأعلى" if is_successful else "الخروج"

                if trade.entry_price > 0:
                    profit_percent = ((price_for_calculation - trade.entry_price) / trade.entry_price) * 100
                
                status_text = "ناجحة" if is_successful else "خاسرة"
                caption = (
                    f"صفقة {trade.underlying} {status_text}\n"
                    f"سعر الدخول: {trade.entry_price:.2f}\n"
                    f"سعر {price_type_text}: {price_for_calculation:.2f}\n"
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

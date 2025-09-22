import asyncio
import queue
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Tuple

from .. import database
from ..services.telegram_service import telegram_service
from ..services.local_image_generator import image_generator
from ..config import settings

def check_for_new_goal(trade: database.Trade) -> Tuple[int, str]:
    """
    Checks if a new profit goal has been reached and returns the new goal level and a caption.
    """
    entry_price = trade.entry_price
    new_price = trade.peak_price_today
    last_goal = trade.last_goal_achieved
    new_goal = last_goal
    # New default caption for price updates
    caption = f"⚪️ تحديث السعر (${trade.strike} ، {trade.underlying}) ⚪️"

    goals = {
        1: settings.GOAL_1_PERCENT, 2: settings.GOAL_2_PERCENT,
        3: settings.GOAL_3_PERCENT, 4: settings.GOAL_4_PERCENT,
        5: settings.GOAL_5_PERCENT
    }
    # New goal achievement captions
    goal_captions = {
        1: "✅ تم تحقيق الهدف الاول .. نقطة خروج اساسية .. اذا حاب تكمل أمن الصفقة ✅",
        2: "✅تم تحقيق الهدف الثاني أمن صفقة✅",
        3: "✅تم تحقيق الهدف الثالث أمن صفقة✅",
        4: "✅تم تحقيق الهدف الرابع أمن صفقة✅",
        5: "✅تم تحقيق الهدف الخامس أمن صفقة اذا بتكمل على مسؤليتك الشخصية✅"
    }

    # Check goals in descending order
    for i in range(5, 0, -1):
        goal_price = entry_price * (1 + goals[i] / 100)
        if round(new_price, 2) >= round(goal_price, 2) and last_goal < i:
            new_goal = i
            caption = goal_captions[i]
            break # Found the highest new goal, no need to check lower ones
    
    return new_goal, caption

async def run_peak_alerter(db: Session, peak_queue: queue.Queue):
    """
    Listens to a queue for trade IDs that have hit a new peak price,
    then generates and sends the alert.
    """
    print("Starting peak alerter...")
    while True:
        try:
            if not peak_queue.empty():
                trade_id = peak_queue.get()
                
                # Use a new session to get the most up-to-date trade data
                db_session = database.SessionLocal()
                trade = db_session.query(database.Trade).filter(database.Trade.id == trade_id).first()

                if not trade:
                    continue

                # 1. Check for goal achievement
                new_goal, caption = check_for_new_goal(trade)
                should_update_goal = new_goal > trade.last_goal_achieved
                
                if should_update_goal:
                    trade.last_goal_achieved = new_goal

                # 2. Prepare data for image generation
                price_change_value = trade.peak_price_today - trade.entry_price
                price_change_percent = (price_change_value / trade.entry_price) * 100 if trade.entry_price != 0 else 0

                image_data = {
                    "underlying": trade.underlying,
                    "strike_price": trade.strike,
                    "expiration_date": trade.expiration_date,
                    "type": trade.trade_type.value,
                    "last_price": trade.peak_price_today,
                    "mid_price": trade.current_price, # Show current mid, not peak
                    "open_interest": 0, # Not available in quote, can be omitted
                    "volume": 0, # Not available in quote, can be omitted
                    "status": "Update",
                    "time": datetime.now().strftime('%H:%M %d/%m'),
                    "price_change_value": price_change_value,
                    "price_change_percent": price_change_percent,
                    "underlying_price": 0, # Not available in quote
                    "underlying_change_value": 0,
                    "underlying_change_percent": 0,
                }

                # 3. Generate the image
                image_bytes = await image_generator.generate_trade_alert(image_data)
                
                if image_bytes:
                    # 4. Save the peak image and new goal to the database
                    trade.peak_image = image_bytes.hex()
                    db_session.commit()
                    
                    # 5. Send the alert to Telegram
                    telegram_service.send_photo(photo_data=image_bytes, caption=caption)
                    print(f"Sent peak alert for trade {trade.id}")
                
                db_session.close()
            
            await asyncio.sleep(0.1) # Small delay to prevent busy-waiting

        except Exception as e:
            print(f"Error in peak alerter loop: {e}")
            if 'db_session' in locals():
                db_session.rollback()
                db_session.close()
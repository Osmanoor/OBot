import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session

from .. import database
from ..services.marketdata_service import marketdata_service
from ..services.telegram_service import telegram_service
from ..services.local_image_generator import image_generator
from ..config import settings

async def initiate_trade(form_data: Dict[str, Any], db: Session):
    """
    Orchestrates the entire process of initiating a new trade.
    """
    # 1. Parse and prepare API parameters from form data
    api_params = {
        "side": form_data.get("trade_type").lower(),
        "inTheMoney": False,
        "dte_gte": 1
    }
    
    strike = form_data.get("strike")
    expiration = form_data.get("expiration")
    min_price = form_data.get("min_price")
    max_price = form_data.get("max_price")
    min_volume = form_data.get("min_volume")

    if strike:
        api_params["strike"] = float(strike)
    else:
        if min_price and max_price:
            api_params["minBid"] = float(min_price)
            api_params["maxAsk"] = float(max_price)

    if expiration:
        api_params["expiration"] = expiration

    if min_volume and min_volume.isdigit():
        api_params["minVolume"] = int(min_volume)

    # 2. Find the option contract
    underlying_symbol = form_data.get("symbol").upper()
    contract = marketdata_service.find_option_contract(underlying_symbol, api_params)

    if not contract:
        error_message = f"Could not find an option contract for {underlying_symbol} with the specified criteria."
        print(error_message)
        # The Telegram message will be sent from the main endpoint now
        return error_message

    # 3. Calculate profit goals
    entry_price = contract["mid"]
    goals = {
        "goal1": entry_price * (1 + settings.GOAL_1_PERCENT / 100),
        "goal2": entry_price * (1 + settings.GOAL_2_PERCENT / 100),
        "goal3": entry_price * (1 + settings.GOAL_3_PERCENT / 100),
        "goal4": entry_price * (1 + settings.GOAL_4_PERCENT / 100),
        "goal5": entry_price * (1 + settings.GOAL_5_PERCENT / 100),
    }

    # 4. Prepare data for image generation
    image_data = {
        "underlying": contract["underlying"],
        "strike_price": contract["strike_price"],
        "expiration_date": datetime.fromtimestamp(contract["expiration_date"]),
        "type": contract["type"],
        "last_price": entry_price,
        "mid_price": entry_price,
        "open_interest": contract["open_interest"],
        "volume": contract["volume"],
        "status": "Open",
        "time": datetime.now().strftime('%H:%M %d/%m'),
        "price_change_value": 0,
        "price_change_percent": 0,
        "underlying_price": contract["underlying_price"],
        "underlying_change_value": 0,
        "underlying_change_percent": 0,
    }

    # 5. Generate the image
    image_bytes = await image_generator.generate_trade_alert(image_data)
    if not image_bytes:
        error_message = "Failed to generate trade alert image."
        print(error_message)
        return error_message

    # 6. Save the new trade to the database
    new_trade = database.Trade(
        symbol=contract["symbol"],
        trade_type=contract["type"],
        underlying=contract["underlying"],
        strike=contract["strike_price"],
        entry_price=entry_price,
        current_price=entry_price,
        peak_price_today=entry_price,
        expiration_date=datetime.fromtimestamp(contract["expiration_date"]),
        status=database.TradeStatus.ACTIVE,
        entry_image=image_bytes.hex(), # Store image bytes as hex string
        last_goal_achieved=0
    )
    db.add(new_trade)
    db.commit()
    db.refresh(new_trade)
    print(f"Successfully saved new trade {new_trade.id} to the database.")

    # 7. Send the alert to Telegram
    header = ""
    if contract['type'] == 'CALL':
        header = f"🟢 دخول عقد جديد CALL 🟢"
    else:
        header = f"🔴 دخول عقد جديد PUT 🔴"

    stop_loss_price = entry_price * 0.5
    caption = (
        f"{header}\n"
        f"({contract['underlying']}, ${contract['strike_price']})\n"
        f"(الهدف الاول: {goals['goal1']:.2f})\n"
        f"(الهدف الثاني: {goals['goal2']:.2f})\n"
        f"(الهدف الثالث: {goals['goal3']:.2f})\n"
        f"(الهدف الرابع: {goals['goal4']:.2f})\n"
        f"(الهدف الخامس: {goals['goal5']:.2f})\n"
        f"وقف الخسارة: {stop_loss_price:.2f}"
    )
    telegram_service.send_photo(photo_data=image_bytes, caption=caption)
    print("Sent trade alert to Telegram.")
    
    return None # Return None on success

from typing import Dict, Any

def get_trade_alert_svg(data: Dict[str, Any]) -> str:
    """
    Generates the SVG for a new trade or a peak price update.
    This is a direct translation of the original n8n workflow's template.
    """
    # --- Data Preparation & Formatting ---
    is_price_profit = data.get("price_change_value", 0) >= 0
    price_change_color = "#26A69A" if is_price_profit else "#F5426C"
    price_change_icon = "▲" if is_price_profit else "▼"

    is_underlying_profit = data.get("underlying_change_value", 0) >= 0
    underlying_change_color = "#26A69A" if is_underlying_profit else "#F5426C"

    # Format expiration date
    exp_date = data.get("expiration_date", "N/A")
    try:
        formatted_exp_date = exp_date.strftime('%d %b %y')
    except AttributeError:
        formatted_exp_date = "Invalid Date"

    # --- Formatted Strings ---
    header_sub_text = f"{formatted_exp_date} (W) {data.get('type', 'N/A')} 100"
    price_change_value_display = f"{'+' if is_price_profit else ''}{data.get('price_change_value', 0):.2f}"
    price_change_percent_display = f"{'+' if is_price_profit else ''}{data.get('price_change_percent', 0):.2f}%"
    price_change_string = f"{price_change_icon}{price_change_value_display} {price_change_percent_display}"
    underlying_price_string = f"{data.get('underlying_price', 0):.2f}"
    underlying_percent_string = f"{'+' if is_underlying_profit else ''}{data.get('underlying_change_percent', 0):.2f}%"
    footer_status_string = f"{data.get('status', 'N/A')}, {data.get('time', 'N/A')} ET"
    formatted_open_interest = f"{data.get('open_interest', 0):,}"
    formatted_volume = f"{data.get('volume', 0):,}"
    formatted_underlying_symbol = str(data.get('underlying', 'N/A')).replace('W', '')

    svg_template = f"""
    <svg width="632" height="216" viewBox="0 0 632 216" xmlns="http://www.w3.org/2000/svg">
        <style>
            .text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
            .header-main {{ font-size: 20px; font-weight: 400; fill: #FFFFFF; }}
            .header-sub {{ font-size: 12px; font-weight: 400; fill: #9DB2CE; }}
            .price-large {{ font-size: 60px; font-weight: 700; fill: {price_change_color}; }}
            .price-change {{ font-size: 18px; font-weight: 600; fill: {price_change_color}; }}
            .stat-label {{ font-size: 18px; font-weight: 400; fill: #9DB2CE; }}
            .stat-value {{ font-size: 18px; font-weight: 400; fill: #c7d9f0; text-anchor: end; }}
            .footer-text {{ font-size: 15px; font-weight: 500; fill: #c7d9f0; }}
            .footer-change {{ fill: {underlying_change_color}; }}
        </style>
        <rect width="100%" height="100%" fill="#131722" />
        <g transform="translate(0, -10)">
            <g transform="translate(0, 10)">
                <path d="M 35 54 L 25 42 L 35 30" stroke="#FFFFFF" fill="none" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            </g>
            <text x="55" y="48" class="text header-main">{data.get('underlying', 'N/A')} ${data.get('strike_price', 0)}</text>
            <text x="55" y="70" class="text header-sub">{header_sub_text}</text>
            <g transform="translate(580, 28) scale(1.2)">
                <path d="M19 14v3h3v2h-3.001L19 22h-2l-.001-3H14v-2h3v-3h2zm1.243-9.243c2.262 2.268 2.34 5.88.236 8.235l-1.42-1.418c1.331-1.524 1.261-3.914-.232-5.404-1.503-1.499-3.92-1.563-5.49-.153l-1.335 1.198-1.336-1.197c-1.575-1.412-3.991-1.35-5.494.154-1.49 1.49-1.565 3.875-.192 5.451l8.432 8.446L12 21.485 3.52 12.993c-2.104-2.356-2.025-5.974.236-8.236 2.265-2.264 5.888-2.34 8.244-.228 2.349-2.109 5.979-2.039 8.242.228z" fill="#FFFFFF"/>
            </g>
        </g>
        <g id="main-price" transform="translate(25, 0)">
            <text x="-6" y="136" class="text price-large">{data.get('last_price', 0):.2f}</text>
            <text x="0" y="165" class="text price-change">{price_change_string}</text>
        </g>
        <g id="stats">
            <text x="420" y="100" class="text stat-label">Mid</text>
            <text x="575" y="100" class="text stat-value">{data.get('mid_price', 0):.2f}</text>
            <text x="420" y="130" class="text stat-label">Open Int.</text>
            <text x="575" y="130" class="text stat-value">{formatted_open_interest}</text>
            <text x="420" y="160" class="text stat-label">Vol.</text>
            <text x="575" y="160" class="text stat-value">{formatted_volume}</text>
            <rect x="585" y="85" width="25" height="80" rx="5" fill="#1E2A38" />
            <polygon points="592,124 602,124 597,129" fill="#FFFFFF"/>
        </g>
        <g id="footer">
            <text x="25" y="202" class="text footer-text">
                {formatted_underlying_symbol}
                <tspan class="footer-change">{underlying_price_string}</tspan> 
                <tspan class="footer-change">{underlying_percent_string}</tspan>
            </text>
            <text x="570" y="202" class="text footer-text" text-anchor="end">{footer_status_string}</text>
            <rect x="580" y="186" width="30" height="22" rx="5" fill="#15294A" />
            <g transform="translate(588, 188) rotate(10)">
                <path fill="#448AFF" d="M9.5 6.5L10 0H9L2 9.5h4.5L6 16h1l7-9.5z"/>
            </g>
        </g>
    </svg>
    """
    return svg_template

def wrap_svg_in_html(svg_content: str) -> str:
    """
    Wraps the given SVG content in a basic HTML document to ensure correct rendering.
    """
    return f"""
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          html, body {{
            margin: 0;
            padding: 0;
          }}
        </style>
      </head>
      <body>
        {svg_content}
      </body>
    </html>
    """

def get_daily_report_html(
    is_successful: bool,
    entry_image_b64: str,
    peak_image_b64: str,
    background_image_b64: str
) -> str:
    """
    Generates the HTML for the daily "before and after" report image.
    Adapted from the 'Daily_Reporting.json' workflow.
    """
    # The image B64 strings from the DB are just the raw data,
    # they need the data URL prefix to be used in HTML.
    entry_image_data_url = f"data:image/png;base64,{entry_image_b64}"
    peak_image_data_url = f"data:image/png;base64,{peak_image_b64}"
    background_image_data_url = f"data:image/jpeg;base64,{background_image_b64}"

    if is_successful:
        content_html = f"""
            <img class="trade-image" src="{entry_image_data_url}" />
            <img class="trade-image" src="{peak_image_data_url}" />
        """
    else:
        # For failed trades, we overlay a "FAILED" stamp.
        content_html = f"""
            <div style="position: relative; display: flex; justify-content: center; align-items: center;">
                <img class="trade-image" src="{entry_image_data_url}" />
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-15deg); font-size: 80px; font-weight: bold; color: rgba(245, 66, 108, 0.8); border: 5px solid rgba(245, 66, 108, 0.8); padding: 10px 20px; border-radius: 10px;">FAILED</div>
            </div>
        """

    composite_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            width: 632px;
            height: 500px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        .container {{
            width: 100%;
            height: 100%;
            position: relative;
            background-color: #131722;
        }}
        .background-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 1; 
            z-index: 1;
        }}
        .content {{
            position: relative;
            width: 100%;
            height: 100%;
            z-index: 2;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            box-sizing: border-box;
            gap: 20px; /* Add some space between images */
        }}
        .trade-image {{
            width: 632px;
            height: 216px;
            opacity: 0.75;
        }}
    </style>
    </head>
    <body>
        <div class="container">
            <img class="background-overlay" src="{background_image_data_url}" />
            <div class="content">
                {content_html}
            </div>
        </div>
    </body>
    </html>
    """
    return composite_html

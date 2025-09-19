from typing import Dict, Any

def get_trade_alert_svg(data: Dict[str, Any]) -> str:
    """
    Generates the SVG for a new trade or a peak price update.
    This is adapted from the 'Image_Generator.json' workflow.
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
        # Assuming it's a datetime object
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
        </g>
        <g id="main-price" transform="translate(25, 0)">
            <text x="-6" y="136" class="text price-large">{data.get('last_price', 0):.2f}</text>
            <text x="0" y="165" class="text price-change">{price_change_string}</text>
        </g>
        <g id="stats">
            <text x="420" y="100" class="text stat-label">Mid</text>
            <text x="575" y="100" class="text stat-value">{data.get('mid_price', 0):.2f}</text>
            <text x="420" y="130" class="text stat-label">Open Int.</text>
            <text x="575" y="130" class="text stat-value">{data.get('open_interest', 0):,}</text>
            <text x="420" y="160" class="text stat-label">Vol.</text>
            <text x="575" y="160" class="text stat-value">{data.get('volume', 0):,}</text>
        </g>
        <g id="footer">
            <text x="25" y="202" class="text footer-text">
                {data.get('underlying', 'N/A')}
                <tspan class="footer-change">{underlying_price_string}</tspan> 
                <tspan class="footer-change">{underlying_percent_string}</tspan>
            </text>
            <text x="570" y="202" class="text footer-text" text-anchor="end">{footer_status_string}</text>
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
                <img class="trade-image" src="{peak_image_data_url}" style="opacity: 0.6;" />
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
            opacity: 0.5; /* Background is more subtle */
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

def get_weekly_report_svg(summary_data: Dict[str, Any], trade_rows: list) -> str:
    """
    Generates the SVG for the weekly summary report.
    Adapted from 'Weekly_Reporting.json'.
    """
    # Dynamically build the SVG table rows
    table_rows_svg = ''
    row_height = 45
    start_y = 320
    mid_point = (len(trade_rows) + 1) // 2
    for i in range(mid_point):
        y_pos = start_y + (i * row_height)
        
        # Left column trade
        left_trade = trade_rows[i]
        peak_price_display_left = f'<tspan fill="#4CAF50">{left_trade["peakPrice"]}</tspan>' if left_trade["isWinner"] else f'<tspan fill="#F44336">{left_trade["peakPrice"]}</tspan>'
        table_rows_svg += f'<text x="75" y="{y_pos}" class="text table-text" text-anchor="middle">{left_trade["symbol"]}</text>'
        table_rows_svg += f'<text x="210" y="{y_pos}" class="text table-text" text-anchor="middle">{left_trade["entryPrice"]}</text>'
        table_rows_svg += f'<text x="345" y="{y_pos}" class="text table-text" text-anchor="middle">{peak_price_display_left}</text>'
        table_rows_svg += f'<line x1="10" y1="{y_pos + 15}" x2="410" y2="{y_pos + 15}" stroke="#FFFFFF" stroke-opacity="0.2" />'

        # Right column trade (if it exists)
        if i + mid_point < len(trade_rows):
            right_trade = trade_rows[i + mid_point]
            peak_price_display_right = f'<tspan fill="#4CAF50">{right_trade["peakPrice"]}</tspan>' if right_trade["isWinner"] else f'<tspan fill="#F44336">{right_trade["peakPrice"]}</tspan>'
            table_rows_svg += f'<text x="485" y="{y_pos}" class="text table-text" text-anchor="middle">{right_trade["symbol"]}</text>'
            table_rows_svg += f'<text x="620" y="{y_pos}" class="text table-text" text-anchor="middle">{right_trade["entryPrice"]}</text>'
            table_rows_svg += f'<text x="755" y="{y_pos}" class="text table-text" text-anchor="middle">{peak_price_display_right}</text>'
            table_rows_svg += f'<line x1="420" y1="{y_pos + 15}" x2="820" y2="{y_pos + 15}" stroke="#FFFFFF" stroke-opacity="0.2" />'

    # Main SVG template
    svg_template = f"""
    <svg width="830" height="1000" viewBox="0 0 830 1000" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
        <style>
            .text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; fill: #FFFFFF; }}
            .title {{ font-size: 48px; font-weight: bold; text-anchor: middle; }}
            .date {{ font-size: 24px; text-anchor: middle; }}
            .subtitle {{ font-size: 40px; font-weight: bold; text-anchor: middle; }}
            .table-header {{ font-size: 20px; font-weight: bold; text-anchor: middle; fill: #000000; }}
            .table-text {{ font-size: 22px; font-weight: 500; }}
            .summary-label {{ font-size: 28px; font-weight: bold; text-anchor: end; }}
            .summary-value {{ font-size: 28px; font-weight: bold; text-anchor: start; }}
            .footer-text {{ font-size: 16px; text-anchor: end; fill: #A0A0A0; }}
        </style>

        <rect width="100%" height="100%" fill="#131722" />
        <image xlink:href="data:image/jpeg;base64,{summary_data['background_image_b64']}" x="0" y="0" width="100%" height="100%" opacity="0.5" preserveAspectRatio="xMidYMid slice" />

        <g>
            <text x="415" y="80" class="text title">التقرير الأسبوعي</text>
            <text x="415" y="120" class="text date">{summary_data['date_range']}</text>
            <text x="415" y="200" class="text subtitle">{summary_data['bot_name']}</text>

            <rect x="10" y="250" width="810" height="40" fill="#E0E0E0" />
            <text x="75" y="278" class="text table-header">الشركه</text>
            <text x="210" y="278" class="text table-header">سعر العقد</text>
            <text x="345" y="278" class="text table-header">اعلى سعر وصل له</text>
            <text x="485" y="278" class="text table-header">الشركه</text>
            <text x="620" y="278" class="text table-header">سعر العقد</text>
            <text x="755" y="278" class="text table-header">اعلى سعر وصل له</text>
            
            {table_rows_svg}
            
            <g transform="translate(0, {start_y + (mid_point * row_height) + 40})">
                <text x="780" y="50" class="text summary-label">إجمالي عدد الصفقات:</text>
                <text x="450" y="50" class="text summary-value">{summary_data['total_trades']}</text>
                <text x="780" y="100" class="text summary-label">الصفقات الناجحه:</text>
                <text x="450" y="100" class="text summary-value">{summary_data['winning_trades']}</text>
                <text x="780" y="150" class="text summary-label">الصفقات الخاسره:</text>
                <text x="450" y="150" class="text summary-value">{summary_data['losing_trades']}</text>
                <text x="780" y="200" class="text summary-label">أرباح الأسبوع ✅:</text>
                <text x="450" y="200" class="text summary-value" fill="#4CAF50">$ {summary_data['total_profit']:,.2f}</text>
                <text x="780" y="250" class="text summary-label">خسائر الأسبوع ❌:</text>
                <text x="450" y="250" class="text summary-value" fill="#F44336">$ {abs(summary_data['total_loss']):,.2f}</text>
            </g>
        </g>
    </svg>
    """
    return svg_template
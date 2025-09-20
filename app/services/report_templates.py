from typing import Dict, Any

def get_report_svg(summary_data: Dict[str, Any], trade_rows: list, title: str) -> str:
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

    # Calculate dynamic height
    header_height = 300
    table_height = mid_point * row_height
    summary_height = 300
    footer_height = 200
    total_height = header_height + table_height + summary_height + footer_height

    # Main SVG template
    svg_template = f"""
    <svg width="830" height="{total_height}" viewBox="0 0 830 {total_height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
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
    
        <rect width="100%" height="100%" />
        <image xlink:href="data:image/jpeg;base64,{summary_data['background_image_b64']}" x="0" y="0" width="100%" height="100%" opacity="1" preserveAspectRatio="xMidYMid slice" />
    
        <g opacity="0.7">
            <text x="415" y="80" class="text title">{title}</text>
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
            <g transform="translate(0, {start_y + (mid_point * row_height) + 320})">
                <text x="800" y="50" class="text footer-text">ـ التنفيذ يكون بنفس العقد او عقود قريبه جدا.</text>
                <text x="800" y="80" class="text footer-text">ـ يعتبر العقد ناجح بتحقيق ربح ٣٠٪ أو أكثر.</text>
                <text x="800" y="110" class="text footer-text">ـ يتم تسجيل أقصى ربح وأقصى خساره للعقد لقياس جودة الطرح.</text>
                <text x="800" y="140" class="text footer-text">ـ مايتم طرحه لا يعتبر توصيه للشراء أو البيع بأموال حقيقيه بل لغرض التدريب على التداول.</text>
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
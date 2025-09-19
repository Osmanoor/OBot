import asyncio
from pyppeteer import launch
from typing import Dict, Any, Optional

from .svg_templates import get_trade_alert_svg, wrap_svg_in_html
from ..config import settings

class LocalImageGenerator:
    """
    Generates PNG images from HTML/SVG content using a local headless browser.
    """
    async def generate_image(self, html_content: str, viewport: Dict[str, int]) -> Optional[bytes]:
        """
        Renders HTML content to a PNG image.

        Args:
            html_content: The HTML string to render.
            viewport: A dictionary with 'width' and 'height' for the browser viewport.

        Returns:
            The PNG image data as bytes, or None if an error occurs.
        """
        browser = None
        try:
            launch_options = {
                'headless': True,
                'args': ['--no-sandbox', '--disable-setuid-sandbox']
            }
            if settings.CHROME_EXECUTABLE_PATH:
                launch_options['executablePath'] = settings.CHROME_EXECUTABLE_PATH
            
            browser = await launch(**launch_options)
            page = await browser.newPage()
            await page.setViewport(viewport)
            await page.setContent(html_content)
            
            # Add a small delay to ensure fonts and SVG elements are fully rendered
            await asyncio.sleep(0.1)

            screenshot = await page.screenshot({
                'type': 'png',
                'omitBackground': True,
            })
            return screenshot
        except Exception as e:
            print(f"Error generating image with pyppeteer: {e}")
            return None
        finally:
            if browser:
                await browser.close()

    async def generate_trade_alert(self, trade_data: Dict[str, Any]) -> Optional[bytes]:
        """
        Generates a standard trade alert image.
        """
        svg_content = get_trade_alert_svg(trade_data)
        html_content = wrap_svg_in_html(svg_content)
        viewport = {'width': 632, 'height': 216}
        return await self.generate_image(html_content, viewport)

# Create a single instance of the service
image_generator = LocalImageGenerator()
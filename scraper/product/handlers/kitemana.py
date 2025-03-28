import traceback
from bs4 import BeautifulSoup


async def kitemana(url, playwright_context):
    page = None
    try:
        page = await playwright_context.new_page()
        await page.goto(url)
        product = await page.evaluate('() => window.product')
        # Get the HTML content
        html = await page.content()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        
        # Find the target div
        description_div = soup.select_one("#pdp-content")
        
        if description_div:
            product["html_description"] = description_div.prettify()  # Keeps HTML formatting
            if description_div.text is not None:
                product["description"] = description_div.text.strip()

        return product, 'KITEMANA_PRODUCT'
    except Exception as e:
        raise e
    finally:
        if page is not None:
            await page.close()

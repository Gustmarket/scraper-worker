import traceback


async def kitemana(url, user_data, playwright_context):
    page = None
    try:
        page = await playwright_context.new_page()
        await page.goto(url)
        product = await page.evaluate('() => window.product')

        return product, 'KITEMANA_PRODUCT'
    except Exception as e:
        traceback.print_exc()
    finally:
        if page is not None:
            await page.close()
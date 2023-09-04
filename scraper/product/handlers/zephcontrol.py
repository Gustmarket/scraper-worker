
async def zephcontrol(url, playwright_context):
    page = None
    try:
        page = await playwright_context.new_page()
        await page.goto(url)
        product = await page.evaluate("() => Object.keys(window.__NUXT__.data).map(key => key.startsWith('prefetch-') ? window.__NUXT__.data[key] : undefined).find(Boolean)?.product")

        return product, 'ZEPHCONTROL_PRODUCT'
    except Exception as e:
        raise e
    finally:
        if page is not None:
            await page.close()


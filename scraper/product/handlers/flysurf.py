import asyncio

from scraper.product.mapping import extract_product


from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

async def flysurf(url, playwright_context):
    page = None
    try:
        page = await playwright_context.new_page()
        await page.goto(url)
        base = extract_product(await page.content(), url)
        variant_selectors = await page.query_selector_all('.dp-product-size .dp-checklist li label')
        variants = []
        for variant_selector in variant_selectors:
            await variant_selector.click()

            # todo: await price change or smth
            await asyncio.sleep(1)

            variant_input = await variant_selector.query_selector('input')
            size = await variant_input.get_attribute('title')
            price = await (await page.query_selector('.dp-product-price .priceWithDiscount')).text_content()
            input_class = await variant_input.get_attribute('class')
            in_stock = input_class is None or 'disabled' not in input_class
            logger.debug(f'flysurf data: {in_stock} {size} {price}')
            variants.append({
                'in_stock': in_stock,
                'size': size,
                'price': price
            })

        return {
            **base,
            'extra_data': {
                'variants': variants
            }
        }, 'MICRODATA_ITEM'
    except Exception as e:
        raise e
    finally:
        if page is not None:
            await page.close()

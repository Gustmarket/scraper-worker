import asyncio

from scraper.product.mapping import extract_product


from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

async def flysurf(url, playwright_context):
    page = None
    try:
        page = await playwright_context.new_page()
        await page.goto(url)
        
        # Handle cookie consent modal first
        try:
            # coockie_handler_button = await page.wait_for_selector('button.cookiesplus-reject')
            coockie_handler_button = await page.wait_for_selector('button.cookiesplus-accept')
            await coockie_handler_button.click()
            # Wait for modal to disappear
            await page.wait_for_selector('#cookiesplus-modal-container', state='hidden')
        except Exception as e:
            logger.warning(f"Cookie consent handling failed: {e}")
        
        base = extract_product(await page.content(), url)
        variant_selector_labels = [(await label.inner_text()).strip() for label in await page.query_selector_all('.ng--product--variants--item:not(.ng--product--variants--item--disabled) label')]
        logger.debug(f"flysurf variant_selector_labels: {variant_selector_labels}")
        variants = []
        for variant_selector_label in variant_selector_labels:
            variant_selectors = await page.query_selector_all('.ng--product--variants--item:not(.ng--product--variants--item--disabled)')
            variant_selector = None
            for selector in variant_selectors:
                label = await selector.query_selector('label')
                if label:
                    text = (await label.inner_text()).strip()
                    if text == variant_selector_label:
                        variant_selector = selector
                        break
            if not variant_selector:
                logger.warning(f"Could not find variant selector for label: {variant_selector_label}")
                continue
            logger.debug(f"flysurf variant_selector: clicking variant")
            await (await variant_selector.query_selector('label')).click()
            logger.debug(f"flysurf variant_selector: clicked")

            # todo: await price change or smth
            await asyncio.sleep(1)
            logger.debug(f"flysurf variant_selector: getting size")
            variant_input = await variant_selector.query_selector('input')
            logger.debug(f"flysurf variant_selector: getting size 2")
            size = await variant_input.get_attribute('title')
            logger.debug(f"flysurf variant_selector: getting price")
            price = await (await page.query_selector('#hiddenPriceForAlma')).text_content()
            logger.debug(f'flysurf data: {size} {price}')
            variants.append({
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

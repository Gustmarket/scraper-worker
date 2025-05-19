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
            # Re-query selectors for each iteration
            await page.wait_for_selector('.ng--product--variants--item:not(.ng--product--variants--item--disabled)')
            
            # Click the variant using label text directly
            await page.evaluate('''(label) => {
                const selectors = document.querySelectorAll('.ng--product--variants--item:not(.ng--product--variants--item--disabled) label');
                for (const selector of selectors) {
                    if (selector.innerText.trim() === label) {
                        selector.click();
                        return;
                    }
                }
            }''', variant_selector_label)
            
            logger.debug(f"flysurf variant_selector: clicked")

            # Wait for any updates to complete
            await page.wait_for_timeout(1000)  # 1 second wait

            # Get size and price
            size = await page.evaluate('''(label) => {
                const selector = document.querySelector(`.ng--product--variants--item:not(.ng--product--variants--item--disabled) input[title="${label}"]`);
                return selector ? selector.getAttribute('title') : null;
            }''', variant_selector_label)
            
            price = await page.evaluate('''() => {
                const priceElement = document.querySelector('#hiddenPriceForAlma');
                return priceElement ? priceElement.textContent : null;
            }''')
            
            logger.debug(f'flysurf data: {size} {price}')
            if size and price:
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

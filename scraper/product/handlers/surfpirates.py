import asyncio
from itertools import product

from bs4 import BeautifulSoup

from scraper.product.mapping import extract_product

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

def generate_combinations(attribute_options):
    return list(product(*attribute_options))


async def surfpirates(url, playwright_context):
    page = None
    try:
        page = await playwright_context.new_page()
        product_url = url
        await page.goto(product_url)
        variations = await page.query_selector_all('.select-variation-section .vaiation-wrapper')

        attributes = []
        for variation in variations:
            variation_selectors = []
            for label in await variation.query_selector_all('label'):
                forAttr = await label.evaluate("l => l.getAttribute('for')")
                variation_selectors.append(f"[for=\"{forAttr}\"]")
            attributes.append(variation_selectors)

        combos = generate_combinations(attributes)

        def page_has_diff_url():
            return page.url != product_url

        async def wait_for_diff_url():
            tries = 0
            while tries < 20:
                tries = tries + 1
                await asyncio.sleep(0.5)
                if page_has_diff_url():
                    break

        variants = []
        for combo in combos:
            variant_labels = []
            in_stock = True
            for combo_variant in combo:
                variant_selector_handle = await page.query_selector(combo_variant)
                variant_label = await variant_selector_handle.evaluate('x => x.getAttribute("data-title")')
                variant_labels.append(variant_label)

                logger.debug(f'clicking: {variant_label}')
                if 'not available' in variant_label:
                    in_stock = False
                    break
                await variant_selector_handle.click()

            if in_stock:
                await wait_for_diff_url()
                if not page_has_diff_url():
                    raise Exception('could not load different url')
                soup = BeautifulSoup(await page.content(), 'html.parser')
                extracted = extract_product(soup, url)
                product_url = page.url
                variants.append({
                    **extracted,
                    'extra_data': {
                        'url': product_url,
                        'variant_labels': variant_labels
                    }
                })

        return ({
                    'variants': variants
                }, 'MICRODATA_VARIANTS_ITEM')
    except Exception as e:
        raise e
    finally:
        if page is not None:
            await page.close()

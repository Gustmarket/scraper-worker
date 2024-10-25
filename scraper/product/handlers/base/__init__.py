import asyncio

from processing.data.utils import uniq_filter_none
from scraper.product.mapping import extract_product

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

def combination_to_url_hash_path(combo):
    return f"{combo['id_attribute']}-{combo['group']}-{combo['attribute']}"


async def attributes_combinations_product_scraper(url,
                                                  playwright_context,
                                                  product_size_group_keys,
                                                  get_initial_url,
                                                  get_product_node_content):
    page = None
    try:
        page = await playwright_context.new_page()
        await page.goto(url)

        attributes_combinations = await page.evaluate('() => window.attributesCombinations')

        initial_url = get_initial_url(url, attributes_combinations)
        if initial_url is None:
            logger.debug('no initial url')
            return
        sizes = [c for c in attributes_combinations if c['group'] in product_size_group_keys]
        variants = []

        await page.goto(url.split('#')[0])
        last_price = None
        for sizeCombo in sizes:
            url = f"{initial_url}/{combination_to_url_hash_path(sizeCombo)}"
            logger.debug(f"getting product: {url}")
            await page.goto(url)
            logger.debug(page.url)

            tries = 0
            while tries < 10:
                tries = tries + 1
                await asyncio.sleep(1)
                data = await get_product_node_content(page)
                ui_price = await page.query_selector('#our_price_display')
                availability = None
                availability_element = await page.query_selector('#availability_value')
                if availability_element is not None:
                    availability = await availability_element.evaluate('x => x.innerText')

                item = extract_product(data, url)
                new_price = await ui_price.evaluate('x => x.innerText')
                item['extra_data'] = {
                    'price': new_price,
                    'size': sizeCombo['attribute'],
                    'url': url,
                    'availability': availability
                }
                logger.debug(f"pricecompare: {last_price}, {new_price}")
                if last_price != new_price:
                    last_price = new_price
                    variants.append(item)
                    break

        result = {
            'id': await page.evaluate('() => window.id_product'),
            'variants': variants,
        }
        return result, 'MICRODATA_VARIANTS_ITEM'
    except Exception as e:
        raise e
    finally:
        if page is not None:
            await page.close()

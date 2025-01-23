import requests
from bs4 import BeautifulSoup


from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

from scraper.product.mapping import extract_product


async def kiteworldshop(url, playwright_context):
    page = None
    try:
        page = await playwright_context.new_page()
        await page.goto(url)
        logger.info(f"kiteworldshop: requested_url: {url} current_url: {page.url}")

        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        extracted = extract_product(soup, url)
        attributes_combinations = await page.evaluate('() => window.attributesCombinations')
        combinations = await page.evaluate(
            '() => (window.combinations || []).map(x => ({idsAttributes: x.idsAttributes, reference: x.reference}))')
        product = next(filter(lambda x: x['@type'] == 'Product', extracted['json-ld']), None)
        if product is None:
            raise Exception('No product found')

        def map_offer(offer):
            combination = next(filter(lambda x: x['reference'] == offer['sku'], combinations))
            extra_data = None
            if combination is not None:
                ids_attributes = list(map(lambda x: str(x), combination.get('idsAttributes', [])))
                if len(ids_attributes) > 0:
                    size = next((x['attribute'] for x in attributes_combinations if
                                 x['id_attribute'] in ids_attributes and x['group'] == "kite_size"), None)
                    color = next((x['attribute'] for x in attributes_combinations if
                                  x['id_attribute'] in ids_attributes and x['group'] == "kite_color"), None)

                    extra_data = {
                        'size': size,
                        'color': color
                    }
            return {
                **offer,
                "extra_data": extra_data
            }

        product['offers'] = list(map(map_offer, product.get('offers', [])))

        extracted['json-ld'] = [product]

        return extracted, 'MICRODATA_ITEM'
    except Exception as e:
        logger.exception(f"kiteworldshop: error: {url}")
        raise e
    finally:
        if page is not None:
            await page.close()

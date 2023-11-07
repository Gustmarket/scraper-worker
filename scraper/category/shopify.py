import hashlib

import requests

import database
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


def shopify_category_scraper(source):
    async def cat_s(url):
        base_url = f"{url}/products.json"
        logger.debug(f"shopify scraper: {base_url}")
        current_page = 0
        while current_page < 20:
            current_page = current_page + 1
            page_url = f"{base_url}?page={current_page}"
            logger.debug(f"shopify scraper next page: {page_url}")
            response = requests.get(page_url)
            products = response.json().get('products', [])
            if len(products) == 0:
                break

            for product in products:
                url_hash = hashlib.sha256(url.encode("UTF-8")).hexdigest()
                database.get_model('raw_items').update_one({'hash': url_hash}, {'$set': {
                    'source': source,
                    'hash': url_hash,
                    'url': f'{url}/products/{product["handle"]}',
                    'loaded_url': f'{url}/products/{product["handle"]}',
                    'type': 'SHOPIFY_PRODUCT',
                    'item': {
                        **product,
                        'url': f'{url}/products/{product["handle"]}'
                    },
                    'processed': False
                }}, upsert=True)

    return lambda url, enqueue_link, playwright_context, user_data: cat_s(url)

import hashlib
import traceback

import database


async def add_product(product, product_type, url, source, url_hash):
    if product is None:
        return

    print({
        'source': source,
        'hash': url_hash,
        'url': url,
        'loaded_url': url,
        'item': product,
        'type': product_type})


def route_scraper(source, handler):
    async def internal_handler(url, user_data, playwright_context):
        url_hash = user_data.get('hash')
        result = None
        try:
            data = await handler(url=url, user_data=user_data, playwright_context=playwright_context)
            if data is None:
                result = {
                    'source': source,
                    'hash': url_hash,
                    'url': url,
                    'loaded_url': url,
                    'type': "OUT_OF_STOCK"}
            else:
                (product, product_type) = data
                result = {
                    'source': source,
                    'hash': url_hash,
                    'url': url,
                    'loaded_url': url,
                    'item': product,
                    'type': product_type}
        except Exception as e:
            traceback.print_exc()
            result = {
                'source': source,
                'hash': url_hash,
                'url': url,
                'loaded_url': url,
                'error': str(e),
                'type': "ERROR"}
        finally:
            if result.get('hash') is None:
                result['hash'] = hashlib.sha256(url.encode("UTF-8")).hexdigest()
            database.get_model('raw_items').update_one({'hash': result['hash']}, {'$set': result}, upsert=True)

    return lambda url, user_data, playwright_context: internal_handler(url, user_data, playwright_context)

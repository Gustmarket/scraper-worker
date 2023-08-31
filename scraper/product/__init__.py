import hashlib
import traceback
from datetime import datetime, timedelta

import pymongo
from pymongo import ReturnDocument

import database
from scraper.product.handlers.coronation_industries import coronation_industries
from scraper.product.handlers.flysurf import flysurf
from scraper.product.handlers.glissattitude import glissattitude
from scraper.product.handlers.kitemana import kitemana
from scraper.product.handlers.magasin_glissevolution import magasin_glissevolution
from scraper.product.handlers.side_shore import side_shore
from scraper.product.handlers.surfpirates import surfpirates
from scraper.product.handlers.you_love_it import you_love_it
from scraper.product.handlers.zephcontrol import zephcontrol
from scraper.utils import get_main_domain

product_route_handlers = {
    'you-love-it.eu': you_love_it,
    'coronation-industries.de': coronation_industries,
    'kitemana.com': kitemana,
    'glissattitude.com': glissattitude,
    'surfpirates.de': surfpirates,
    'magasin-glissevolution.com': magasin_glissevolution,
    'zephcontrol.com': zephcontrol,
    'side-shore.com': side_shore,
    'flysurf.com': flysurf
}


async def product_route(product_url, playwright_context):
    url = product_url['url']
    user_data = {"hash": product_url['hash']}
    print(f'Scraping {url} ...')
    if user_data is None or user_data.get('hash') is None:
        print('no hash present on product')
        return
    source = get_main_domain(url)
    domain_handler = product_route_handlers.get(source)
    if domain_handler is None:
        print('no domain handler for', source)
        return
    url_hash = user_data.get('hash')
    result = None
    try:
        data = await domain_handler(url=url, user_data=user_data, playwright_context=playwright_context)
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


async def get_one_expired_product_url_and_update(playwright_context):
    product_urls_model = database.get_model("product_urls")
    product_url = product_urls_model.find_one_and_update({
        'disabled': {'$ne': True},
        '$or': [
            {'next_update': {'$exists': False}},
            {'next_update': {'$lt': datetime.now()}}
        ]
    }, [{
        '$set': {
            'next_update': {'$add': [
                datetime.now(),
                48 * 60 * 60000.0,
            ]}}
    }], sort=[("next_update", pymongo.ASCENDING)], return_document=ReturnDocument.AFTER)

    if product_url is None:
        return None

    try:
        await product_route(product_url, playwright_context)
    except Exception as e:
        traceback.print_exc()
        product_urls_model.update_one({'_id': product_url['_id']},
                                      {'$set': {
                                          'next_update': datetime.now() + timedelta(hours=1)
                                      }},
                                      upsert=False)

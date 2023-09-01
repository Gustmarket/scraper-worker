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


async def scrape_and_save_product(product_url, playwright_context):
    url = product_url['url']
    url_hash = product_url['hash']
    print(f'Scraping {url} ...')
    if url_hash is None:
        print('no hash present on product')
        return
    source = get_main_domain(url)
    domain_handler = product_route_handlers.get(source)
    if domain_handler is None:
        print('no domain handler for', source)
        return

    data = await domain_handler(url=url, playwright_context=playwright_context)
    if data is None:
        result = {
            'type': "OUT_OF_STOCK"
        }
    else:
        (product, product_type) = data
        result = {
            'item': product,
            'type': product_type
        }
    database.get_model('raw_items').update_one({'hash': url_hash}, {'$set': {
        'source': source,
        'hash': url_hash,
        'url': url,
        'loaded_url': url,
        **result
    }}, upsert=True)


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
        await scrape_and_save_product(product_url, playwright_context)
    except Exception as e:
        traceback.print_exc()
        product_urls_model.update_one({'_id': product_url['_id']},
                                      {'$set': {
                                          'last_error': str(e),
                                          'last_error_date': datetime.now(),
                                          'next_update': datetime.now() + timedelta(hours=1)
                                      }},
                                      upsert=False)

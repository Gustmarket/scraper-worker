from datetime import datetime, timedelta

import pymongo
from celery.utils.log import get_task_logger
from pymongo import ReturnDocument

import database
from scraper.product.handlers.coronation_industries import coronation_industries
from scraper.product.handlers.flysurf import flysurf
from scraper.product.handlers.glissattitude import glissattitude
from scraper.product.handlers.kitemana import kitemana
from scraper.product.handlers.kiteworldshop import kiteworldshop
from scraper.product.handlers.magasin_glissevolution import magasin_glissevolution
from scraper.product.handlers.side_shore import side_shore
from scraper.product.handlers.surfpirates import surfpirates
from scraper.product.handlers.you_love_it import you_love_it
from scraper.product.handlers.zephcontrol import zephcontrol
from scraper.utils import get_main_domain

logger = get_task_logger(__name__)

product_route_handlers = {
    'you-love-it.eu': you_love_it,
    'coronation-industries.de': coronation_industries,
    'kitemana.com': kitemana,
    'kiteworldshop.com': kiteworldshop,
    'glissattitude.com': glissattitude,
    'surfpirates.de': surfpirates,
    'magasin-glissevolution.com': magasin_glissevolution,
    'zephcontrol.com': zephcontrol,
    'side-shore.com': side_shore,
    'flysurf.com': flysurf,
}


async def scrape_and_save_product(product_url, playwright_context):
    url = product_url['url']
    url_hash = product_url['hash']
    logger.info(f'Scraping {url} ...')
    if url_hash is None:
        logger.info(f'no hash present on product: {url}')
        return
    source = get_main_domain(url)
    domain_handler = product_route_handlers.get(source)
    if domain_handler is None:
        logger.debug(f'no domain handler for: {source} -> {url}')
        return

    data = await domain_handler(url=url, playwright_context=playwright_context)
    if data is None:
        data = (None, None)

    (product, product_type) = data

    if product is None or product_type == 'OUT_OF_STOCK':
        result = {
            'type': "OUT_OF_STOCK"
        }
    else:
        result = {
            'item': product,
            'type': product_type
        }
    database.get_model('raw_items').update_one({'hash': url_hash}, {'$set': {
        'source': source,
        'hash': url_hash,
        'url': url,
        'loaded_url': url,
        'processed': False,
        'category': product_url['category'],
        'condition': product_url['condition'],
        **result
    }}, upsert=True)

async def get_one_expired_product_url_and_update_with_query(playwright_context, query):
    product_urls_model = database.get_model("product_urls")
    product_url = product_urls_model.find_one_and_update(query, [{
        '$set': {
            'next_update': {'$add': [
                datetime.now(),
                48 * 60 * 60000.0,
            ]}}
    }], sort=[("next_update", pymongo.ASCENDING)], return_document=ReturnDocument.AFTER)

    logger.info(f"product_url: {product_url}")
    if product_url is None:
        return None

    try:
        await scrape_and_save_product(product_url, playwright_context)
        product_urls_model.update_one({'_id': product_url['_id']},
                                      {'$set': {
                                          'updated_at': datetime.utcnow(),
                                          'error_count': 0,
                                          'last_error': None,
                                          'last_error_date': None,
                                      }},
                                      upsert=False)
    except Exception as e:
        logger.exception('error while scraping product')
        error_msg = str(e).lower()
        if "target page, context or browser has been closed" in error_msg or "page closed" in error_msg:
            logger.info("Page was closed during scraping")
            product_urls_model.update_one({'_id': product_url['_id']},
                                      {'$set': {
                                          'updated_at': datetime.utcnow(),
                                          'last_error': str(e),
                                          'last_error_date': datetime.now(),
                                          'next_update': datetime.now() + timedelta(hours=1)
                                      },
                                          '$inc': {
                                              'playwright_context_error_count': 1
                                          }},
                                      upsert=False)
        else:
            product_urls_model.update_one({'_id': product_url['_id']},
                                      {'$set': {
                                          'updated_at': datetime.utcnow(),
                                          'last_error': str(e),
                                          'last_error_date': datetime.now(),
                                          'next_update': datetime.now() + timedelta(hours=1)
                                      },
                                          '$inc': {
                                              'error_count': 1
                                          }},
                                      upsert=False)


async def get_one_expired_product_url_and_update(playwright_context):
   await get_one_expired_product_url_and_update_with_query(playwright_context, {
        'out_of_stock': {'$ne': True},
        'disabled': {'$ne': True},
        '$and': [
            {'$or': [
                {'error_count': {'$lt': 5}, },
                {'error_count': {'$exists': False}, }
            ]},
            {
                '$or': [
                    {'next_update': {'$exists': False}},
                    {'next_update': {'$lt': datetime.now()}}
                ]
            }]
    })
   
async def get_one_expired_product_url_and_update_test(playwright_context):
   await get_one_expired_product_url_and_update_with_query(playwright_context, {
        # 'last_error': "could not load different url"
         'hash': '9975eb45135c4d71b85d35c175c6ad3bc578185f7f5890e2a78d8a4547d15c54'  
    })
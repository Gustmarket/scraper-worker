import datetime

from celery.utils.log import get_task_logger

import database
from processing.raw_items_processor.mapping.normalization import normalize_pre_processed_item, \
    map_and_normalize_pre_processed_items
from processing.raw_items_processor.mapping.pre_processing import PreProcessor

logger = get_task_logger(__name__)


def process_raw_items():
    raw_items = database.get_unprocessed_raw_items()

    (raw_item_ids, items) = PreProcessor.process_items(raw_items)

    nr_of_items = len(items)
    logger.info(f'got {nr_of_items} mapped items out of {len(raw_item_ids)} items')

    database.bulk_upsert_items(items=items, id_key='raw_item_id', model_name='pre_processed_items', upsert=True)
    database.get_model('raw_items').update_many({
        '_id': {
            '$in': raw_item_ids
        }
    }, {
        '$set': {
            'processed': True
        }
    })
    return nr_of_items


def normalize_pre_processed_items():
    pre_processed_items = database.get_pre_processed_items()
    (item_ids, normalized_items) = map_and_normalize_pre_processed_items(pre_processed_items)
    logger.info(f'got {len(normalized_items)} normalized items out of {len(item_ids)} items')

    database.bulk_upsert_normalized_items(items=normalized_items)
    database.get_model('pre_processed_items').update_many({
        '_id': {
            '$in': item_ids
        }
    }, {
        '$set': {
            'processed': True
        }
    })


def upsert_products_from_normalized_items():
    normalized_items = database.get_normalized_items({
        "type": {'$in': ["KITEMANA_PRODUCT", 'MICRODATA_VARIANTS_ITEM', 'MICRODATA_ITEM', 'SHOPIFY_PRODUCT']},
        '$or': [
            {
                'products_processed': False
            },
            {
                'products_processed': {
                    '$exists': False
                }
            }
        ]
    })

    products = []
    item_ids = []
    for normalized_item in normalized_items:
        item = normalized_item['item']
        item_ids.append(normalized_item['_id'])
        products.append({
            "internal_sku": item['internal_sku'],
            "name": item['name'],
            "is_standardised": item.get('is_standardised'),
            "unique_model_identifier": item.get('unique_model_identifier'),
            "brand": item['brand'],
            "brand_slug": item['brand_slug'],
            "category": item['category'],
            "images": list(set(item['images'])),
            "attributes": {
                "year": item['attributes']['year'],
                "sizes": list(set(list(map(lambda v: v["size"], item['variants'])))),
            }
        })

    logger.info(f'got {len(products)} products out of {len(item_ids)} items')
    database.bulk_upsert_products(products)
    database.get_model('normalized_items').update_many({
        '_id': {
            '$in': item_ids
        }
    }, {
        '$set': {
            'products_processed': True
        }
    })


def upsert_product_offers():
    normalized_items = database.get_normalized_items({
        '$or': [
            {
                'offers_processed': False
            },
            {
                'offers_processed': {
                    '$exists': False
                }
            }
        ]
    })

    offers = []
    item_ids = []
    for normalized_item in normalized_items:
        item = normalized_item['item']
        item_ids.append(normalized_item['_id'])
        base_offer = {
            "normalized_item_id": normalized_item['_id'],
            "internal_sku": item['internal_sku'],
            "offer_url": item['url'],
            "offer_source": normalized_item['source'],
            "name": item['name'],
            "unique_model_identifier": item.get('unique_model_identifier'),
            "brand": item['brand'],
            "brand_slug": item['brand_slug'],
            "category": item['category'],
            "images": item['images'],
            "condition": item['condition'],
            "attributes": item['attributes']
        }

        def map_offer(variant):
            return {
                **base_offer,
                "attributes": {
                    **base_offer['attributes'],
                    "size": variant.get("size"),
                },
                "offer_url": variant.get("url"),
                "offer_hash": normalized_item.get("hash"),
                "in_stock": variant.get("in_stock"),
                "price": variant.get("price"),
            }

        product_offers = list(map(map_offer, item['variants']))
        offers.extend(product_offers)

    logger.info(f'got {len(offers)} offers items out of {len(item_ids)} items')
    chunks = chunk_array(offers, 500)
    logger.info(f'got {len(chunks)} chunks of offers')
    index = 1
    for chunk in chunks:
        logger.info(f'processing chunk {index} of {len(chunks)}')
        index = index + 1
        item_ids = list(map(lambda o: o['normalized_item_id'], chunk))
        offer_hashes = list(map(lambda o: o['offer_hash'], chunk))
        database.set_out_of_stock_offers(offer_hashes)
        database.bulk_upsert_product_offers(chunk)
        database.get_model('normalized_items').update_many({
            '_id': {
                '$in': item_ids
            }},
            {
                '$set': {
                    'offers_processed': True
                }
            })


def process_out_of_stock_raw_items():
    out_of_stock = database.get_out_of_stock_raw_items()

    item_ids = []
    item_urls = []
    for item in out_of_stock:
        item_ids.append(item['_id'])
        item_urls.append(item['url'])

    database.get_model('product_urls').update_many({
        'url': {
            '$in': item_urls
        }
    }, {
        '$set': {
            'next_update': datetime.datetime.now()
        }
    })

    database.get_model('raw_items').delete_many({
        '_id': {
            '$in': item_ids
        }
    })


def cleanup_inexsistent_items():
    unlinked_items = database.get_model('pre_processed_items').aggregate([
        {'$match': {}},
        {
            '$lookup': {
                'from': 'raw_items',
                'localField': 'raw_item_id',
                'foreignField': '_id',
                'as': 'raw_item'
            }
        }, {
            '$unwind': {
                'path': '$raw_item',
                'preserveNullAndEmptyArrays': True
            }
        },
        {'$match': {
            '$or': [{'raw_item': None}, {'raw_item': {'$exists': False}}]
        }}, ])

    item_ids = []
    item_hashes = []
    for item in unlinked_items:
        item_ids.append(item['_id'])
        item_hashes.append(item['hash'])

    logger.info(f'got {len(item_hashes)} unlinked pre processed items')
    if len(item_hashes) > 0:
        database.get_model('pre_processed_items').delete_many({
            '_id': {
                '$in': item_ids
            }
        })

        database.get_model('normalized_items').delete_many({
            'hash': {
                '$in': item_hashes
            }
        })

        database.get_model('product_offers').delete_many({
            'offer_hash': {
                '$in': item_hashes
            }
        })




def chunk_array(array, chunk_size):
    return [array[i:i + chunk_size] for i in range(0, len(array), chunk_size)]

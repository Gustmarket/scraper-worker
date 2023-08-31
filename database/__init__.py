import os

from pymongo import MongoClient, operations

# client = MongoClient(os.getenv("DB_URL"))
# db_name = os.getenv("DB_NAME")
client = MongoClient("mongodb+srv://victorbalan:bG4WJtcxYJBMXFrD@gustmarket-cluster.eu50bsg.mongodb.net/")
db_name = "gustmarket_dev"
db = client[db_name]


def get_model(model):
    return db[model]


def get_processing_apify_runs():
    return get_model('apify_runs').find({
        'status': {'$in': ['READY', 'RUNNING']}
    })


def set_apify_run_status(run_id, status):
    return get_model('apify_runs').update_one({
        'id': run_id
    }, {
        '$set': {
            'status': status
        }
    })


def get_succeeded_apify_runs():
    return get_model('apify_runs').find({
        'status': 'SUCCEEDED'
    })


def upsert_apify_run(run):
    return get_model('apify_runs').find_one_and_update(
        {
            'id': run['id']
        },
        {
            '$set': run
        },
        upsert=True)


def get_unprocessed_raw_items():
    return get_model('raw_items').find({
        '$or': [
            {
                'processed': False
            },
            {
                'processed': {
                    '$exists': False
                }
            }
        ]
    })


def get_pre_processed_items():
    return get_model('pre_processed_items').find({
        '$or': [
            {
                'processed': False
            },
            {
                'processed': {
                    '$exists': False
                }
            }
        ]
    })


def get_normalized_items(filters):
    return get_model('normalized_items').find(filters)


def perform_bulk_operations(bulk_operations, model_name):
    model = get_model(model_name)
    if len(bulk_operations) > 0:
        model.bulk_write(bulk_operations)


def bulk_upsert_items(items, id_key, model_name, upsert=False):
    bulk_operations = []
    for item in items:
        bulk_operations.append(operations.UpdateOne({id_key: item[id_key]},
                                                    {
                                                        "$set": item
                                                    }, upsert=upsert))
    perform_bulk_operations(bulk_operations=bulk_operations, model_name=model_name)


def bulk_upsert_raw_items(items):
    bulk_operations = []
    for item in items:
        bulk_operations.append(operations.UpdateOne({
            "hash": item["hash"],
        },
            {
                "$set": item
            }, upsert=True))

    perform_bulk_operations(bulk_operations=bulk_operations, model_name="raw_items")


def bulk_upsert_products(items):
    bulk_operations = []
    for item in items:
        bulk_operations.append(operations.UpdateOne({
            "internal_sku": item["internal_sku"],
        },
            {
                "$setOnInsert": {
                    "internal_sku": item['internal_sku'],
                    "name": item['name'],
                    "brand": item['brand'],
                    "brand_slug": item['brand_slug'],
                    "category": item['category'],
                    "attributes.year": item['attributes']['year']},
                "$addToSet": {
                    "images": {'$each': item.get("images", [])},
                    "attributes.sizes": {'$each': item.get("attributes", {}).get("sizes", [])},
                }
            }, upsert=True))

    perform_bulk_operations(bulk_operations=bulk_operations, model_name="products")


def bulk_upsert_normalized_items(items):
    bulk_operations = []
    for item in items:
        bulk_operations.append(operations.UpdateOne({
            "pre_processed_item_id": item["pre_processed_item_id"],
            "normalization_key": item.get("normalization_key")
        },
            {
                "$set": item
            }, upsert=True))

    perform_bulk_operations(bulk_operations=bulk_operations, model_name="normalized_items")


def set_out_of_stock_offers(sku_source_tuples):
    get_model("product_offers").update_many({
        '$or': list(map(lambda t: {
            "internal_sku": t[0],
            "offer_source": t[1],
        }, sku_source_tuples))
    }, {
        "$set": {
            "in_stock": False
        }
    })


def bulk_upsert_product_offers(offers):
    bulk_operations = []
    for offer in offers:
        bulk_operations.append(operations.UpdateOne({
            "internal_sku": offer["internal_sku"],
            "offer_source": offer["offer_source"],
            "attributes.size": offer.get("attributes", {}).get("size"),
            "attributes.condition": offer.get("attributes", {}).get("condition"),
        },
            {
                "$set": offer
            }, upsert=True))

    perform_bulk_operations(bulk_operations=bulk_operations, model_name="product_offers")

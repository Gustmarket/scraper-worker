from processing.entitites.pre_processed_item import PreProcessedItem

from celery.utils.log import get_task_logger

from processing.processors.pre_processed_items.processor import normalize_pre_processed_product

logger = get_task_logger(__name__)
def normalize_pre_processed_item(item):
    crawled_item_type = item['type']

    normalized_items = None

    if crawled_item_type == 'FACEBOOK_GROUP_POST':
        normalized_items = None
    else:
        mapped = normalize_pre_processed_product(PreProcessedItem.from_json(item['item']), {
            'condition': item.get('condition'),
            'category': item.get('category'),
        })
        if mapped is not None:
            normalized_items = [mapped.to_json()]

    def map_test(normalized_item):
        return {
            **item,
            "pre_processed_item_id": item["_id"],
            "normalization_key": item.get("normalization_key"),
            "item": normalized_item
        }

    if normalized_items is not None:
        normalized_items = list(filter(lambda x: x is not None, normalized_items))

    if normalized_items is not None and len(normalized_items) > 0:
        return list(map(map_test, normalized_items))
    else:
        return None


def map_and_normalize_pre_processed_items(pre_processed_items):
    normalized_items = []
    item_ids = []
    for item in pre_processed_items:
        item_ids.append(item['_id'])
        normalized_item = normalize_pre_processed_item(item)
        if normalized_item is not None:
            normalized_items = normalized_items + normalized_item

    return item_ids, normalized_items

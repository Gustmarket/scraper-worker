from processing.raw_items_processor.mapping.normalization.pre_processed_product import \
    normalize_pre_processed_product
from processing.raw_items_processor.mapping.pre_processing.base import PreProcessedProduct


def normalize_pre_processed_item(item):
    crawled_item_type = item['type']

    normalized_items = None

    if crawled_item_type == 'FACEBOOK_GROUP_POST':
        normalized_items = None
    elif (crawled_item_type in ['MICRODATA_VARIANTS_ITEM',
                                'MICRODATA_ITEM',
                                'SHOPIFY_PRODUCT',
                                'KITEMANA_PRODUCT']):
        mapped = normalize_pre_processed_product(PreProcessedProduct.from_json(item['item']))
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

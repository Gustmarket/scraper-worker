from processing.raw_items_processor.mapping.base import DataProcessor
from processing.raw_items_processor.mapping.pre_processing.facebook import FacebookPreProcessedItem
from processing.raw_items_processor.mapping.pre_processing.kitemana import from_raw_item_kitemana
from processing.raw_items_processor.mapping.pre_processing.microdata import map_microdata_variants_item, \
    map_microdata_item
from processing.raw_items_processor.mapping.pre_processing.shopify import from_raw_item_shopify
from processing.raw_items_processor.mapping.pre_processing.zephcontrol import from_raw_item_zephcontrol


class PreProcessor(DataProcessor):

    @staticmethod
    def process_item(item):
        if item.get('item') is None:
            return None

        crawled_item_type = item['type']

        pre_processed = None
        if crawled_item_type == 'KITEMANA_PRODUCT':
            pre_processed = from_raw_item_kitemana({
                **item['item'],
                'url': item['url'],
            })
        elif crawled_item_type == 'MICRODATA_VARIANTS_ITEM':
            pre_processed = map_microdata_variants_item({
                **item['item'],
                'url': item['url'],
            })
        elif crawled_item_type == 'MICRODATA_ITEM':
            pre_processed = map_microdata_item({
                **item['item'],
                'url': item['url'],
            })
        elif crawled_item_type == 'SHOPIFY_PRODUCT':
            pre_processed = from_raw_item_shopify({
                **item['item'],
                'url': item['url'],
            })
        elif crawled_item_type == 'FACEBOOK_GROUP_POST':
            pre_processed = FacebookPreProcessedItem.from_raw_item(item['item'])
        elif crawled_item_type == 'ZEPHCONTROL_PRODUCT':
            pre_processed = from_raw_item_zephcontrol({
                **item['item'],
                'url': item['url'], }
            )

        if pre_processed is not None:
            return {
                **item,
                'raw_item_id': item['_id'],
                "item": pre_processed.to_json()
            }
        else:
            return None

    @staticmethod
    def process_items(raw_items):
        items = []
        raw_item_ids = []

        for item in raw_items:
            raw_item_ids.append(item['_id'])
            mapped_item = PreProcessor.process_item(item)
            if mapped_item is not None:
                items.append({
                    **mapped_item,
                    'processed': False
                })

        return raw_item_ids, items

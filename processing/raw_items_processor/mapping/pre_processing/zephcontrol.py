from processing.raw_items_processor.mapping.entitites.price import GustmarketPrice
from processing.raw_items_processor.mapping.pre_processing.base import PreProcessedProduct, PreProcessedProductVariant
from processing.raw_items_processor.mapping.utils import uniq_filter_none


def from_raw_item_zephcontrol(crawled_item):
    base_price = crawled_item['price']
    tax_rate = crawled_item['taxRate']

    def map_variant(variant):
        price = round(base_price + variant['price'] + (variant['price'] * (tax_rate  / 100)))
        return PreProcessedProductVariant(
            id=str(variant["id"]),
            url=crawled_item['url'],
            price=GustmarketPrice.from_price_string(str(price), 'EUR'),
            name=None,
            name_variants=[],
            in_stock=True,
            images=[],
            attributes={
                'size': variant['attributes'][0]['name']
            }
        )


    return PreProcessedProduct(
        id=crawled_item['id'],
        name=crawled_item['name'],
        name_variants=[],
        url=crawled_item['url'],
        brand=crawled_item.get('brand', {}).get('name'),
        category='HARDCODED_KITE',
        variants=list(map(map_variant, crawled_item.get('productAttributes', []))),
        images=uniq_filter_none(list(map(lambda x: x.get('url'), crawled_item.get('images', [])))),
        condition=None,
    )




from processing.entitites.price import GustmarketPrice
from processing.entitites.pre_processed_item import PreProcessedItem, \
    PreProcessedItemVariant
from processing.data.utils import uniq_filter_none

def from_raw_item_zephcontrol(crawled_item):
    base_price = crawled_item['price']
    tax_rate = crawled_item['taxRate']

    def map_variant(variant):
        price = round(base_price + variant['price'] + (variant['price'] * (tax_rate  / 100)))
        quantity = variant.get('quantity')
        in_stock = True if quantity is None else quantity > 0
        return PreProcessedItemVariant(
            id=str(variant["id"]),
            url=crawled_item['url'],
            price=GustmarketPrice.from_price_string(str(price), 'EUR'),
            name=None,
            name_variants=[],
            in_stock=in_stock,
            images=[],
            attributes={
                'size': variant['attributes'][0]['name']
            }
        )


    return PreProcessedItem(
        id=crawled_item['id'],
        name=crawled_item['name'],
        name_variants=[],
        url=crawled_item['url'],
        brand=crawled_item.get('brand', {}).get('name'),
        variants=list(map(map_variant, crawled_item.get('productAttributes', []))),
        images=uniq_filter_none(list(map(lambda x: x.get('url'), crawled_item.get('images', [])))),
        category=None,
        condition=None,
        subcategories=[]
    )




from processing.entitites.price import GustmarketPrice
from processing.entitites.pre_processed_item import PreProcessedItem, \
    PreProcessedItemVariant
from processing.data.utils import uniq_filter_none

def try_to_get_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except:
        return None

def _map_shopify_variant(variant, options_config):
    price = try_to_get_float(variant.get('price'))
    image = variant.get('featured_image')
    if image is not None:
        image = image.get('src')

    attributes = {}

    for option in options_config:
        option_name = option.get('name')
        option_position = option.get('position')
        if option_name is None or option_position is None:
            continue
        option_name = option_name.lower()

        option_value = variant.get(f"option{option_position}")
        if option_value is not None:
            attributes[option_name] = option_value

    return PreProcessedItemVariant(
        id=str(variant["id"]),
        url=str(variant["id"]),
        price=GustmarketPrice.from_price_string(price, 'EUR'),
        name=variant['title'],
        name_variants=[],
        in_stock=variant.get('available'),
        images=[] if image is None else [image],
        attributes=attributes
    )


def from_raw_item_shopify(crawled_item):
    variants = list(
        map(lambda variant: _map_shopify_variant(variant, crawled_item.get('options', {})),
            crawled_item['variants']))
    if variants is None or len(variants) == 0:
        return None

    def set_variant_url(variant):
        if variant is None:
            return variant
        variant.url = crawled_item['url'] + "?variant=" + variant.id
        return variant

    variants = list(map(set_variant_url, variants))

    title_ = crawled_item['title']
    category = crawled_item.get('product_type')
    condition = None
    if category is not None:
        category = category.lower()
        if 'used' in category:
            condition = 'USED'

    images = crawled_item.get('images')
    if images is not None:
        images = uniq_filter_none(list(map(lambda i: i.get('src'), images)))

    return PreProcessedItem(
        id=crawled_item['id'],
        name=title_,
        name_variants=[title_],
        url=crawled_item['url'],
        brand=crawled_item.get('vendor'),
        variants=variants,
        images=images,
        category=category,
        condition=condition,
    )

from processing.raw_items_processor.mapping.entitites.price import GustmarketPrice
from processing.raw_items_processor.mapping.pre_processing.base import PreProcessedProduct, \
    PreProcessedProductVariant
from processing.raw_items_processor.mapping.pre_processing.microdata.json_ld import map_json_ld
from processing.raw_items_processor.mapping.pre_processing.microdata.microdata import map_microdata
from processing.raw_items_processor.mapping.pre_processing.microdata.utils import better_map
from processing.raw_items_processor.mapping.utils import flatten_list, filter_none, uniq_filter_none


from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
def map_correct_price(price, price_currency, list_price):
    price_result = GustmarketPrice.from_price_string(price, price_currency)

    if list_price is not None:
        list_price = GustmarketPrice.from_price_string(list_price, price_currency)
        if list_price.amount is not None:
            price_result = list_price

    return price_result


def map_product_with_offers_from_crawled_item(crawled_item):
    extra_data = crawled_item.get('extra_data', {})

    all_microdata = crawled_item.get('microdata', [])
    microdata_products = filter_none(list(map(lambda x: map_microdata(x, extra_data, all_microdata), all_microdata)))
    ld_json_products = filter_none(list(map(lambda x: map_json_ld(x, extra_data), crawled_item.get('json-ld', []))))

    if len(microdata_products) > 1 or len(ld_json_products) > 1:
        logger.info('multiple products for item')
        return None

    products = filter_none(flatten_list(microdata_products + ld_json_products))
    return products


def extract_brands_and_names_from_products(products):
    brands = uniq_filter_none(flatten_list(list(map(lambda v: v.get('brand'), products))))
    names = uniq_filter_none(flatten_list(list(map(lambda v: v.get('name'), products))))

    brand = None
    if brands is not None and len(brands) > 0:
        brand = min(brands, key=len)

    name = None
    if names is not None and len(names) > 0:
        name = min(names, key=len)

    return {
        "brand": brand,
        "name": name,
        "name_variants": names
    }


def map_microdata_variants_item(crawled_item):
    raw_variants = crawled_item.get('variants')
    if raw_variants is None or len(raw_variants) == 0:
        return None

    products = filter_none(flatten_list(list(map(map_product_with_offers_from_crawled_item, raw_variants))))
    if len(products) == 0:
        return None

    # merge all products with offers
    all_offers = flatten_list(list(map(lambda p: p.get('offers', []), products)))

    product_images = flatten_list(list(map(lambda v: v.get('images', []), products)))
    offer_images = flatten_list(list(map(lambda o: o.get('images', []), all_offers)))
    images = uniq_filter_none(product_images + offer_images)

    variants = list(map(lambda x: PreProcessedProductVariant(
        id=x.get('id', x.get('sku')),
        url=x.get('url'),
        price=map_correct_price(x.get('price'), x.get('price_currency'), x.get('list_price')),
        name=x.get('name'),
        name_variants=x.get('name'),
        in_stock=x.get('availability') is None or "InStock" in x.get('availability',
                                                                     '') or "LimitedAvailability" in x.get(
            'availability', ''),
        images=x.get('images'),
        attributes=x.get('attributes')
    ), all_offers))

    mapped = extract_brands_and_names_from_products(products)

    return PreProcessedProduct(
        id=crawled_item.get('id'),
        name=mapped.get('name'),
        name_variants=mapped.get('name_variants'),
        brand=mapped.get('brand'),
        url=crawled_item['url'],
        category='HARDCODED_KITE',
        condition=None,
        variants=variants,
        images=images,
    )


# todo: improve this shit as well
def map_microdata_item(crawled_item):
    extra_data = crawled_item.get('extra_data', {})
    raw_variants = extra_data.get('variants')
    if raw_variants is None or len(raw_variants) == 0:
        return None

    products = filter_none(map_product_with_offers_from_crawled_item(crawled_item))
    if len(products) == 0:
        return None

    def map_variant(variant):
        return PreProcessedProductVariant(
            id=None,
            name=None,
            name_variants=[],
            images=[],
            url=variant.get('url'),
            in_stock=variant.get('in_stock', True),
            price=map_correct_price(variant.get('price'), variant.get('price_currency'), variant.get('list_price')),
            attributes={
                "size": variant.get('size'),
                "color": variant.get('color'),
                "variant_labels": variant.get('variant_labels'),  # todo
            }
        )

    variants = list(map(map_variant, raw_variants))

    mapped = extract_brands_and_names_from_products(products)

    return PreProcessedProduct(
        id=crawled_item.get('id'),
        name=mapped.get('name'),
        name_variants=mapped.get('name_variants'),
        brand=mapped.get('brand'),
        url=crawled_item['url'],
        category='HARDCODED_KITE',
        condition=None,
        variants=variants,
        images=[],
    )

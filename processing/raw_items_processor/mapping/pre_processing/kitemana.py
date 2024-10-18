from processing.raw_items_processor.mapping.entitites.price import GustmarketPrice
from processing.raw_items_processor.mapping.pre_processing.base import PreProcessedProduct, \
    PreProcessedProductVariant
from processing.raw_items_processor.mapping.utils import flatten_list, uniq_filter_none


def append_kitemana_domain(path):
    if path is None:
        return None
    return "https://www.kitemana.com" + path


def try_to_get_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except:
        return None


def is_variant_in_stock(variant):
    obsolete = variant.get('Obsolete')
    if obsolete is None or not isinstance(obsolete, bool):
        return True  # todo: check if this is ok

    return not variant['Obsolete']


def variant_from_item_cproduct(variant):
    price = try_to_get_float(variant.get('SalePriceWithTaxWithoutFormat'))
    if price is None:
        price = try_to_get_float(variant.get('price'))
        if price is None:
            price = try_to_get_float(variant.get('originalPrice'))
        tax = try_to_get_float(variant.get('tax'))
        if price is not None and tax is not None:
            price = price + tax * price
        else:
            price = None

    return PreProcessedProductVariant(
        id=str(variant["pId"]),
        url=str(variant["pId"]),
        price=GustmarketPrice.from_price_string(price, 'EUR'),
        name=variant['pname'],
        name_variants=[variant['fpname'], variant['VariantName']],
        in_stock=is_variant_in_stock(variant),
        images=[append_kitemana_domain(variant.get('Image'))],
        attributes={
            "size": variant['Size'],
            "color": variant.get('Color'),
        }
    )


def variant_from_item_variant(variant, base_image_path):
    price = try_to_get_float(variant.get('SalePriceWithTaxWithoutFormat'))
    if price is None:
        price = try_to_get_float(variant.get('FarmattedSalesPriceWithTax'))
    if price is None:
        price = try_to_get_float(variant.get('priceTaxed'))
    if price is None:
        price = try_to_get_float(variant.get('SalesPrice'))

    size = variant.get('Size')
    if size is None:
        size = variant.get('Value')

    image = None
    if base_image_path is not None and variant.get('ImagePath') is not None:
        image = append_kitemana_domain(base_image_path + variant['ImagePath'])

    return PreProcessedProductVariant(
        id=str(variant["pId"]),
        url=str(variant["pId"]),
        price=GustmarketPrice.from_price_string(price, 'EUR'),
        name=variant['fpname'],
        name_variants=[variant['fpname'], variant['VariantName']],
        in_stock=is_variant_in_stock(variant),
        images=[image],
        attributes={
            "size": size,
            "color": variant.get('Color'),
        }
    )


def from_raw_item_kitemana(crawled_item):
    category = None
    variants = None
    base_image_path = crawled_item['imgPath']

    if crawled_item['cproducts'] is not None and len(crawled_item['cproducts']) > 0:
        cproduct = crawled_item['cproducts'][0]
        category = cproduct['componentName']
        variants = list(map(variant_from_item_cproduct, cproduct['variants']))
    elif crawled_item['variants'] is not None and len(crawled_item['variants']) > 0:
        category = crawled_item['categoryName']
        variants = list(
            map(lambda variant: variant_from_item_variant(variant, base_image_path),
                crawled_item['variants']))
    if variants is None or len(variants) == 0:
        return None

    images = list(map(lambda i: append_kitemana_domain(base_image_path + i), crawled_item['images']))
    images = uniq_filter_none(images + flatten_list(list(map(lambda variant: variant.images, variants))))

    def set_variant_url(variant):
        if variant is None:
            return variant
        variant.url = crawled_item['url'] + "?vId=" + variant.id
        return variant

    variants = list(map(set_variant_url, variants))

    return PreProcessedProduct(
        id=crawled_item['id'],
        name=crawled_item['name'],
        name_variants=[crawled_item['name']],
        url=crawled_item['url'],
        brand=crawled_item['brand'],
        category=category,
        variants=variants,
        images=images,
        condition=None,
        defined_category=crawled_item['category'],
        defined_condition=crawled_item['condition'],
    )

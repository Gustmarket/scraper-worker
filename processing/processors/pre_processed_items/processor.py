
from celery.utils.log import get_task_logger

from processing.entitites.normalized_item import NormalizedItemVariant, NormalizedItem
from processing.entitites.pre_processed_item import PreProcessedItem
from processing.data.cleanup import replace_string_ignore_case, \
    replace_string_word_ignore_case
from processing.processors.pre_processed_items.data_extractor import extract_brand_model_info, guess_brand
from processing.processors.pre_processed_items.categoriser import categorise_pre_processed_item
from processing.data.utils import flatten_list, uniq_filter_none, format_float, \
    extract_floats
from processing.processors.pre_processed_items.data_extractor.kiteboards import map_kiteboard_size
from processing.processors.pre_processed_items.data_extractor.kites import map_kite_size

logger = get_task_logger(__name__)


def get_internal_sku(year, brand_slug, name):
    internal_sku = ''
    if year is not None:
        internal_sku = internal_sku + str(year)
    internal_sku = internal_sku + '-'
    if brand_slug is not None:
        internal_sku = internal_sku + brand_slug
    else:
        internal_sku = internal_sku + 'other'
    internal_sku = internal_sku + '-'
    # todo: get slug for model
    if name is not None:
        internal_sku = (internal_sku + name.lower().replace('  ', ' ')
                        .replace(' ', '_').replace('/', '_').replace('?', '').replace('!', ''))
    else:
        internal_sku = internal_sku + 'noname'
    return internal_sku


def cleanup_size(size):
    r = extract_floats(size)
    if len(r) == 0:
        return None
    return f"{format_float(r[0])}m"

def map_kite_variant_label_to_size_or_none(raw):
    mapped = replace_string_ignore_case(raw, "m²", "")
    mapped = replace_string_ignore_case(mapped, "sqm", "")
    mapped = replace_string_ignore_case(mapped, "m", "")
    mapped = mapped.lower().strip()
    return cleanup_size(mapped)


def normalize_pre_processed_product(item: PreProcessedItem, parentAttributes):
    if item.brand is None and item.name is None:
        logger.debug(f'none {item}')
        return None

    (category, subcategory) = categorise_pre_processed_item(item.get_all_name_variants(), parentAttributes.get('category'))
    item.category = category
    item.subcategories = [subcategory] if subcategory else []

    model_info = extract_brand_model_info(item.category, item.brand, item.get_clean_name())
    brand_slug = model_info["brand_slug"]
    brand_name = model_info["brand_name"]
    name = model_info["name"]
    year = model_info["year"]
    condition = model_info["condition"]

    def map_variant(kv):
        variant_name = kv.name
        size = None
        if type(variant_name) == "list" and len(variant_name) > 0:
            variant_name = variant_name[0]

        if item.category is "KITES" or item.category is None:
            size = map_kite_size(variant_name, kv)
        elif item.category is "KITEBOARDS":
            size = map_kiteboard_size(variant_name, kv)

        return NormalizedItemVariant(
            price=kv.price,
            size=size,
            color=kv.attributes.get('color', None),
            images=kv.images,
            in_stock=kv.in_stock,
            url=item.url if kv.url is None else kv.url,
            name=variant_name,
        )

    new_variants = list(map(map_variant, item.variants))

    if len(item.variants) != len(new_variants):
        raise "something wrong happened when mapping variants"

    return NormalizedItem(
        id=item.id,
        is_standardised=model_info.get('is_standardised', False),
        internal_sku=get_internal_sku(year=year, brand_slug=brand_slug, name=name),
        name=name,
        unique_model_identifier=model_info.get('unique_model_identifier', None),
        raw_name=item.name,
        brand=brand_name,
        brand_slug=brand_slug,
        category=item.category,
        condition=condition,
        images=item.images,
        url=item.url,
        variants=new_variants,
        attributes={
            "year": year,
        }
    )

import re

from celery.utils.log import get_task_logger

from processing.raw_items_processor.mapping.normalization.models.item import NormalizedItem, \
    NormalizedItemVariant
from processing.raw_items_processor.mapping.normalization.processing.cleanup import replace_string_word_ignore_case, \
    replace_string_ignore_case
from processing.raw_items_processor.mapping.normalization.processing.processing import extract_brand_model_info, \
    extract_and_cleanup_kite_size
from processing.raw_items_processor.mapping.pre_processing.base import PreProcessedProduct
from processing.raw_items_processor.mapping.utils import flatten_list, uniq_filter_none, filter_none

logger = get_task_logger(__name__)


def get_internal_sku(year, brand_slug, name):
    internal_sku = ''
    if year is not None:
        internal_sku = internal_sku + year
    else:
        internal_sku = internal_sku + 'noyear'
    internal_sku = internal_sku + '-'
    if brand_slug is not None:
        internal_sku = internal_sku + brand_slug
    else:
        internal_sku = internal_sku + 'nobrand'
    internal_sku = internal_sku + '-'
    # todo: get slug for model
    if name is not None:
        internal_sku = (internal_sku + name.lower().replace('  ', ' ')
                        .replace(' ', '_').replace('/', '_').replace('?', '').replace('!', ''))
    else:
        internal_sku = internal_sku + 'noname'
    return internal_sku


# todo:
def extract_floats(text):
    if text is None:
        return []
    pattern = r'[-+]?\d*\.\d+|\d+'  # Regular expression pattern for floats
    floats = re.findall(pattern, text.replace(',', '.').replace('_', '.'))
    return [float(num) for num in floats]


def format_float(value):
    if value == int(value):
        return str(int(value))
    else:
        return str(value)


def cleanup_size(size):
    r = extract_floats(size)
    if len(r) == 0:
        return None
    return f"{format_float(r[0])}m"


def normalize_pre_processed_product(item: PreProcessedProduct):
    if item.brand is None and item.name is None:
        logger.debug(f'none {item}')
        return None

    name = item.name
    if name is None:
        name = ''

    all_variant_labels = uniq_filter_none(
        flatten_list(list(map(lambda kv: kv.attributes.get('variant_labels', []), item.variants))))
    all_variant_labels = uniq_filter_none(
        flatten_list(list(map(lambda x: x.split(' '), all_variant_labels))))
    if len(all_variant_labels) > 0:
        for variant_label in all_variant_labels:
            name = replace_string_word_ignore_case(name, variant_label, '')

    model_info = extract_brand_model_info(item.brand, name)
    brand_slug = model_info["brand_slug"]
    brand_name = model_info["brand_name"]
    name = model_info["name"]
    year = model_info["year"]
    condition = model_info["condition"]

    def map_variant(kv):
        size = kv.attributes.get('size', None)
        if size is None:
            variant_labels = kv.attributes.get('variant_labels', [])
            if variant_labels is None:
                variant_labels = []
            # todo: extract common fn

            def map_variant_label_to_size_or_none(raw):
                mapped = replace_string_ignore_case(raw, "m²", "")
                mapped = replace_string_ignore_case(mapped, "sqm", "")
                mapped = replace_string_ignore_case(mapped, "m", "")
                mapped = mapped.lower().strip()
                return cleanup_size(mapped)

            size_variant_labels = filter_none(list(map(map_variant_label_to_size_or_none, variant_labels)))
            if len(size_variant_labels) > 0:
                size = size_variant_labels[0]
        size = cleanup_size(size)
        variant_name = kv.name
        if type(variant_name) == "list" and len(variant_name) > 0:
            variant_name = variant_name[0]

        if size is None:
            name_variants = kv.name_variants
            if name_variants is None:
                name_variants = []
            name_variants = uniq_filter_none(flatten_list(name_variants + [variant_name]))
            for name_variant in name_variants:
                _, size = extract_and_cleanup_kite_size(name_variant)
                if size is not None:
                    break

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
        category=item.category.lower(),
        condition=condition,
        images=item.images,
        url=item.url,
        variants=new_variants,
        attributes={
            "year": year,
        }
    )

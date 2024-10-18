
from processing.raw_items_processor.mapping.normalization.processing.cleanup import replace_string_word_ignore_case, \
    replace_string_ignore_case
from processing.raw_items_processor.mapping.utils import flatten_list, uniq_filter_none, filter_none, extract_floats, \
    format_float

from processing.raw_items_processor.mapping.normalization.processing.processing import extract_brand_model_info, \
    extract_and_cleanup_kite_size

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

def map_kite_size(variant_name, kv):
        size = kv.attributes.get('size', None)
        if size is None:
            variant_labels = kv.attributes.get('variant_labels', [])
            if variant_labels is None:
                variant_labels = []

            size_variant_labels = filter_none(list(map(map_kite_variant_label_to_size_or_none, variant_labels)))
            if len(size_variant_labels) > 0:
                size = size_variant_labels[0]
        size = cleanup_size(size)

        if size is None:
            name_variants = kv.name_variants
            if name_variants is None:
                name_variants = []
            name_variants = uniq_filter_none(flatten_list(name_variants + [variant_name]))
            for name_variant in name_variants:
                _, size = extract_and_cleanup_kite_size(name_variant)
                if size is not None:
                    break
        return size
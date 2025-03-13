import re

from processing.data.cleanup import replace_string_ignore_case, replace_string_word_ignore_case
from processing.data.utils import uniq_filter_none, flatten_list, filter_none, extract_floats, format_float
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

def extract_and_cleanup_kite_size(name):
    # Define the regular expression pattern
    pattern = r'(\d+([_,\.]\d+)?)m'
    match = re.search(pattern, name)

    if match:
        raw_size = match.group(1)
        kite_size = raw_size.replace('_', '.').replace(',', '.') + 'm'
        return replace_string_ignore_case(name, f"{raw_size}m", ""), kite_size
    else:
        return name, None

def cleanup_all_kite_sizes_from_name(name):
    name_to_parse = name
    keywords = []
    for i in reversed(range(1, 30)):
        keywords.append(f"{i}sqm")
        keywords.append(f"{i}m")
        keywords.append(f"{i} m")
        keywords.append(f"{i}m²")
        keywords.append(f"{i} m²")
        float_1 = "{:.1f}".format(i + 0.5)
        float_2 = float_1.replace('.', ',')
        keywords.append(f"{float_1}sqm")
        keywords.append(f"{float_1}m")
        keywords.append(f"{float_1} m")
        keywords.append(f"{float_1}m²")
        keywords.append(f"{float_1} m²")
        keywords.append(f"{float_2}sqm")
        keywords.append(f"{float_2}m")
        keywords.append(f"{float_2} m")
        keywords.append(f"{float_2}m²")
        keywords.append(f"{float_2} m²")

    for keyword in keywords:
        name_to_parse = replace_string_word_ignore_case(name_to_parse, keyword, "")

    return name_to_parse
def cleanup_size(size):
    r = extract_floats(size)
    if len(r) == 0:
        return None
    return f"{format_float(r[0])}m"


def map_kite_variant_label_to_size_or_none(raw):
    mapped = replace_string_ignore_case(raw, "m²", "")
    mapped = replace_string_ignore_case(mapped, "sqm", "")
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

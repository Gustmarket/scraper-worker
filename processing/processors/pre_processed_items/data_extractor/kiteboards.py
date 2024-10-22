import re

from processing.data.cleanup import replace_string_ignore_case
from processing.data.utils import uniq_filter_none, flatten_list


def extract_and_cleanup_kiteboard_size(name):
    # Define the regular expression patterns for various size formats
    twintip_pattern = r'(\d+(?:[.,]\d+)?)\s*(?:x|-)?\s*(\d+(?:[.,]\d+)?)?\s*(?:cm)?'
    surfboard_pattern = r"(\d+)'(\d+(?:\.\d+)?)?"  # Matches formats like 6'3 or 5'7.5

    # Try to match twintip board size
    twintip_match = re.search(twintip_pattern, name, re.IGNORECASE)
    if twintip_match:
        size1 = float(twintip_match.group(1).replace(',', '.'))
        size2 = float(twintip_match.group(2).replace(',', '.')) if twintip_match.group(2) else 0

        board_size = max(size1, size2)
        board_size = round(board_size)

        cleaned_name = re.sub(twintip_pattern, '', name, flags=re.IGNORECASE).strip()

        return cleaned_name, board_size

    # Try to match surfboard size
    surfboard_match = re.search(surfboard_pattern, name)
    if surfboard_match:
        feet = int(surfboard_match.group(1))
        inches = float(surfboard_match.group(2)) if surfboard_match.group(2) else 0

        board_size = f"{feet}'{inches:.1f}" if inches else f"{feet}'"

        cleaned_name = re.sub(surfboard_pattern, '', name).strip()

        return cleaned_name, board_size

    # If no match found
    return name, None


def map_kiteboard_size(variant_name, kv):
    size = kv.attributes.get('size', None)
    # if size is None:
    #     todo
    #     variant_labels = kv.attributes.get('variant_labels', [])
    #     if variant_labels is None:
    #         variant_labels = []
    #
    #     size_variant_labels = filter_none(list(map(map_kite_variant_label_to_size_or_none, variant_labels)))
    #     if len(size_variant_labels) > 0:
    #         size = size_variant_labels[0]
    # size = cleanup_size(size)

    if size is None:
        name_variants = kv.name_variants
        if name_variants is None:
            name_variants = []
        name_variants = uniq_filter_none(flatten_list(name_variants + [variant_name]))
        for name_variant in name_variants:
            _, size = extract_and_cleanup_kiteboard_size(name_variant)
            if size is not None:
                break
    return size

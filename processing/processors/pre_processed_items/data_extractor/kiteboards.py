import re

from processing.data.utils import uniq_filter_none, flatten_list

def extract_and_cleanup_surfboard_size(raw):
    surfboard_pattern = r"(\d+)'\s*(\d+(?:\.\d+)?)?\"?"  # Matches formats like 6'3, 5'7.5, 6' 3", or 6'  3

    surfboard_match = re.search(surfboard_pattern, raw)
    if surfboard_match:
        feet = int(surfboard_match.group(1))
        inches = float(surfboard_match.group(2).replace(',', '.')) if surfboard_match.group(2) else 0

        cleaned_name = re.sub(surfboard_pattern, '', raw).strip()
        return cleaned_name, f"{feet}'{inches:.1f}" if inches else f"{feet}'"

    return raw, None

def extract_and_cleanup_twintip_size(raw):
    twintip_length_pattern = r'\b(\d{3})\b'
    twintip_width_pattern = r'\b(\d{3})\b'
    twintip_full_size_pattern = r'\b(\d{3})\s*x\s*(\d{2})\b'
    twintip_length_match = re.search(twintip_length_pattern, raw)
    if twintip_length_match:
        twintip_length = float(twintip_length_match.group(1).replace(',', '.'))
        cleaned_name = re.sub(twintip_full_size_pattern, '', raw).strip()
        cleaned_name = re.sub(twintip_length_pattern, '', cleaned_name).strip()
        cleaned_name = re.sub(twintip_width_pattern, '', cleaned_name).strip()
        return cleaned_name, twintip_length
    return raw, None


def extract_and_cleanup_kiteboard_size(name):
    cleaned_name, surfboard_size = extract_and_cleanup_surfboard_size(name)
    if surfboard_size is not None:
        return cleaned_name, surfboard_size

    cleaned_name, twintip_size = extract_and_cleanup_twintip_size(name)
    if twintip_size is not None:
        return cleaned_name, twintip_size

    return name, None


def map_kiteboard_size(variant_name, kv):
    size = kv.attributes.get('size', None)
    extracted_size = None
    if size is not None:
        _, extracted_size = extract_and_cleanup_kiteboard_size(size)

    if extracted_size is None:
        name_variants = kv.name_variants
        if name_variants is None:
            name_variants = []
        name_variants = uniq_filter_none(flatten_list(name_variants + [variant_name]))
        for name_variant in name_variants:
            _, extracted_size = extract_and_cleanup_kiteboard_size(name_variant)
            if extracted_size is not None:
                break
    return extracted_size

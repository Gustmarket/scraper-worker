import re

from processing.data.cleanup import replace_string_ignore_case


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

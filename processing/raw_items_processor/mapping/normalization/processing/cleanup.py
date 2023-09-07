import re

from processing.raw_items_processor.mapping.normalization.processing.constants.colors import color_list

random_keywords_in_order = [
    "kiteboarding",
    "manufacturer",
    "kites",
    "kite",
    "boarding",
    "lightweight lightwind performer",
    "lightwind lightweight performer",
    "lightweight performer",
    "lightwind",
    "hard sale",
    "100% FRISCHFLEISCH",
    "FRISCHFLEISCH",
    "HARDCORE SALE",
    "AILE DE SURF",
    "aile de kitesurf",
    "(copie)",
    "NUE",
    "(new!)"
]

def replace_string_ignore_case(source_string, keyword_to_replace, rep_with):
    compiled = re.compile(re.escape(keyword_to_replace), re.IGNORECASE)
    return compiled.sub(rep_with, source_string)


def replace_string_word_ignore_case(source_string, keyword_to_replace, rep_with):
    compiled = re.compile(r'\b' + re.escape(keyword_to_replace) + r'\b', re.IGNORECASE)
    return compiled.sub(rep_with, source_string)

def remove_colors(name):
    if name is None:
        return None
    cleaned = name
    for color in color_list:
        cleaned = replace_string_word_ignore_case(cleaned, color, " ")
    cleaned = re.sub(" / ", "", cleaned)
    return cleaned.strip()

def cleanup_name_string_by_keywords(name_string):
    if name_string is None:
        return None

    for keyword in random_keywords_in_order:
        name_string = replace_string_word_ignore_case(name_string, keyword, "")

    patterns = [
        "\n",
        ":",
        "_",
        "\\s\\s",
        "\\s\\s",
        "\\s\\s",
    ]
    name_string = remove_colors(name_string)
    for pattern in patterns:
        name_string = re.sub(pattern, " ", name_string.strip())

    return name_string.strip()


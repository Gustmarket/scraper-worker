import re

from celery.utils.log import get_task_logger
from thefuzz import process, fuzz

from processing.data.cleanup import cleanup_name_string_by_keywords, replace_string_ignore_case, \
    replace_string_word_ignore_case
from processing.data.utils import flatten_list, uniq_filter_none
from processing.processors.pre_processed_items.data_extractor.brander import guess_brand
from processing.processors.pre_processed_items.data_extractor.kiteboards import extract_and_cleanup_kiteboard_size
from processing.processors.pre_processed_items.data_extractor.kites import extract_and_cleanup_kite_size, \
    cleanup_all_kite_sizes_from_name
from processing.processors.pre_processed_items.data_extractor.modeler import extract_model

logger = get_task_logger(__name__)


def extract_and_cleanup_year(name):
    concat_year = next(iter(re.findall(r"[0-9]{4}/[0-9]{2,4}", name)), None)
    year = next(iter(re.findall(r"[0-9]{4}", name)), None)
    if concat_year is not None and year != "":
        name = name.replace(concat_year, '').strip()
    elif year is not None and year != "":
        name = name.replace(year, '').strip()

    return name, year


def extract_and_cleanup_condition(raw_name):
    name = raw_name
    condition = "NEW"

    demo_keywords = [
        "(demo)",
        "demo",
        "Testkite",
        "TEST"
    ]

    lower_name = name.lower()
    for keyword in demo_keywords:
        if keyword.lower() in lower_name:
            condition = "DEMO"
            name = replace_string_ignore_case(name, keyword, "")

    used_keywords = [
        "used",
        "(2nd)",
        "second hand"
    ]

    for keyword in used_keywords:
        if keyword.lower() in lower_name:
            condition = "USED"
            name = replace_string_ignore_case(name, keyword, "")

    return name, condition

def extract_brand_model_info(category, raw_brand, raw_name, url):
    model_name = cleanup_name_string_by_keywords(raw_name)
    model_name, year = extract_and_cleanup_year(model_name)
    model_name, condition = extract_and_cleanup_condition(model_name)
    size = None

    if category is None or category == "KITES":
        model_name, size = extract_and_cleanup_kite_size(model_name)
    elif category == "KITEBOARDS":
        #todo: get subcategory(surfboards etc)
        model_name, size = extract_and_cleanup_kiteboard_size(model_name)

    (brand_slug, brand_name, brand_keywords) = guess_brand(raw_brand, model_name, url)

    if brand_keywords is None:
        brand_keywords = []
    brand_keywords = uniq_filter_none(brand_keywords + [brand_name] + [brand_slug])
    for keyword in brand_keywords:
        model_name = replace_string_ignore_case(model_name, keyword, "")

    model_name = cleanup_all_kite_sizes_from_name(model_name).replace('\\s\\s', ' ').strip()

    model_info = extract_model(category, brand_slug, model_name)
    model_name = model_info["name"].strip()
    model_unique_model_identifier = model_info.get("unique_model_identifier", None)  # todo: make one
    model_year = model_info.get("year", None)  # todo: make one

    return {
        "is_standardised": model_info.get("is_standardised", False),
        "brand_slug": brand_slug,
        "brand_name": brand_name,
        "name": model_name,
        "unique_model_identifier": model_unique_model_identifier,
        "condition": condition,
        "size": size,
        "year": model_year if year is None else year
    }


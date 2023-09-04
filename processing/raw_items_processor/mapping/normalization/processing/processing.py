import re

from thefuzz import process, fuzz

from processing.raw_items_processor.mapping.normalization.processing.cleanup import \
    cleanup_name_string_by_keywords, replace_string_ignore_case, replace_string_word_ignore_case
from processing.raw_items_processor.mapping.normalization.processing.constants.brands_and_models import \
    brands_and_models
from processing.raw_items_processor.mapping.utils import flatten_list


from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
def get_brand_slug(brand):
    if brand is None:
        return None
    slug = cleanup_name_string_by_keywords(brand).lower()
    slug = re.sub(" ", "_", slug.strip())
    slug = re.sub("-", "_", slug.strip())
    return slug


def guess_brand_from_string(name):
    to_match = flatten_list(list(map(lambda b: [b['name']] + b.get('variants', []), brands_and_models)))

    (matched_brand, score) = process.extractOne(name, to_match)
    if score < 89:
        return "other", "Other"

    matched_brand = list(
        filter(lambda x: x["name"] == matched_brand or matched_brand in x["variants"], brands_and_models))
    if matched_brand is None:
        raise Exception("Brand not found")

    return matched_brand[0]["slug"], matched_brand[0]["name"]


def extract_and_cleanup_year(name):
    concat_year = next(iter(re.findall(r"[0-9]{4}/[0-9]{4}", name)), None)
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


def get_model_slug(name):
    return name.lower().replace('  ', ' ').replace(' ', '_').replace('/', '_')

def cleanup_all_sizes_from_name(name):
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


def extract_model(brand_slug, name):
    brand_with_models = list(filter(lambda x: x["slug"] == brand_slug, brands_and_models))
    default_return_value = {"name": name, "slug": get_model_slug(name)}
    if len(brand_with_models) == 0:
        return default_return_value

    # todo:not hardcode
    brand_models = brand_with_models[0].get('kites', [])
    if brand_models is None or len(brand_models) == 0:
        return default_return_value

    found = None

    score = 0
    name_to_parse = name.lower()
    for brand_variant in brand_with_models[0]["variants"]:
        name_to_parse = replace_string_ignore_case(name_to_parse, brand_variant, "")

    name_to_parse = cleanup_all_sizes_from_name(name_to_parse).replace('\\s\\s', ' ')

    for brand_model in brand_models:
        no_of_variants = 1
        variant_score = (fuzz.token_sort_ratio(name_to_parse, brand_model['name'].lower()) + fuzz.token_set_ratio(
            name_to_parse, brand_model['name'].lower())) / 2
        for variant in brand_model["variants"]:
            no_of_variants = no_of_variants + 1
            variant_score_2 = (fuzz.token_sort_ratio(name_to_parse, variant.lower()) + fuzz.token_set_ratio(
                name_to_parse, variant.lower())) / 2
            if variant_score_2 > variant_score:
                variant_score = variant_score_2

        if variant_score > score:
            score = variant_score
            found = brand_model

    if score >= 90:
        return {
            "name": found['name'],
            "slug": get_model_slug(found['name']) if found.get('slug', None) is None else found['slug'],
            "year": found.get('year', None),
            "is_standardised": True
        }

    logger.debug(f'{str(score)} - {found["name"]} for {name} parsed {name_to_parse}')

    return default_return_value


def extract_brand_model_info(raw_brand, raw_name):
    brand_slug = None
    brand_name = None
    model_name = cleanup_name_string_by_keywords(raw_name)
    model_name, year = extract_and_cleanup_year(model_name)
    model_name, condition = extract_and_cleanup_condition(model_name)
    model_name, size = extract_and_cleanup_kite_size(model_name)

    if raw_brand is not None:
        brand_slug, brand_name = guess_brand_from_string(raw_brand)
        if brand_slug == "other":
            brand_name = raw_brand
            brand_slug = get_brand_slug(raw_brand)
    else:
        brand_slug, brand_name = guess_brand_from_string(model_name)

    brand_keywords = list(filter(lambda b: b["slug"] == brand_slug, brands_and_models))

    if len(brand_keywords) > 0:
        brand_keywords = brand_keywords[0]["variants"] + [brand_keywords[0]["name"]]
        for keyword in brand_keywords:
            model_name = replace_string_ignore_case(model_name, keyword, "")

    model_info = extract_model(brand_slug, model_name)
    model_name = model_info["name"]
    model_slug = model_info.get("slug", None)  # todo: make one
    model_year = model_info.get("year", None)  # todo: make one
    return {
        "is_standardised": model_info.get("is_standardised", False),
        "brand_slug": brand_slug,
        "brand_name": brand_name,
        "name": model_name,
        "slug": model_slug,
        "condition": condition,
        "size": size,
        "year": model_year if year is None else year
    }

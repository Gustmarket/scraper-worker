import re

from thefuzz import process

from processing.data.cleanup import cleanup_name_string_by_keywords
from processing.processors.pre_processed_items.data_extractor.brander.brands import brand_dictionary

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

def get_brand_slug(brand):
    if brand is None:
        return None
    slug = cleanup_name_string_by_keywords(brand).lower()
    slug = re.sub(" ", "-", slug.strip())
    slug = re.sub("-", "-", slug.strip())
    slug = re.sub("--", "-", slug.strip())
    return slug

def get_slug_and_score(text):
    if text is None:
        return (None, 0)
    highest_score = 0
    highest_brand = None
    for slug, details in brand_dictionary.items():
        result = process.extractOne(text, [details["name"]] + details["keywords"])
        if result is not None:
            matched_keyword, score = result
            if score > highest_score:
                highest_score = score
                highest_brand = slug
    return (highest_brand, highest_score)



def guess_brand(raw_brand, raw_name):
    highest_score = 0
    highest_slug = None
    if raw_brand is not None:
        (highest_slug, highest_score) = get_slug_and_score(raw_brand)

    if highest_score < 90:
        (slug, score) = get_slug_and_score(raw_name)
        if score > highest_score:
            highest_score = score
            highest_slug = slug

    if highest_score > 89:
        if highest_slug in brand_dictionary:
            return (highest_slug, brand_dictionary[highest_slug]['name'], brand_dictionary[highest_slug].get('keywords'))
        return (highest_slug, "", [])

    return (get_brand_slug(raw_brand), raw_brand, [])

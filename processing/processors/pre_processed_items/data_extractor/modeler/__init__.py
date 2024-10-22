import re

from celery.utils.log import get_task_logger
from thefuzz import process, fuzz
from processing.processors.pre_processed_items.data_extractor.modeler.models import get_brand_models

logger = get_task_logger(__name__)
def get_unique_model_identifier(name):
    umi =  name.lower().replace('  ', ' ').replace(' ', '-').replace('/', '-')
    return umi.strip('-')

def extract_model(category, brand_slug, clean_name):
    default_return_value = {"name": clean_name, "unique_model_identifier": get_unique_model_identifier(clean_name)}
    brand_models = get_brand_models(category, brand_slug)

    if brand_models is None:
        return default_return_value
    found = None

    score = 0
    name_to_parse = clean_name.lower()


    for brand_model in brand_models:
        no_of_variants = 1
        variant_score = (fuzz.token_sort_ratio(name_to_parse, brand_model['name'].lower()) + fuzz.token_set_ratio(
            name_to_parse, brand_model['name'].lower())) / 2
        for variant in brand_model["keywords"]:
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
            "unique_model_identifier": get_unique_model_identifier(found['name']) if found.get(
                'unique_model_identifier', None) is None else found['unique_model_identifier'],
            "year": found.get('year', None),
            "is_standardised": True
        }

    logger.debug(f'{str(score)} - {found["name"]} for {clean_name} parsed {name_to_parse}')

    return default_return_value

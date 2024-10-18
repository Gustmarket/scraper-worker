from processing.entitites.pre_processed_item import PreProcessedItem
from thefuzz import process

from processing.processors.pre_processed_items.brander.brands import brand_dictionary

def get_slug_and_score(text): 
    highest_score = 0
    highest_brand = None
    for slug, details in brand_dictionary.items():
        (matched_keyword, score) = process.extractOne(text, details["keywords"])
        if score > highest_score:
            highest_score = score
            highest_brand = slug
    return (highest_brand, highest_score)


def brand_pre_processed_item(brand, name_variants):
    highest_score = 0
    highest_slug = None
    (highest_slug, highest_score) = get_slug_and_score(brand)
    if highest_score < 90:
        for variant in name_variants:
            (slug, score) = get_slug_and_score(variant)
            if score > highest_score:
                highest_score = score
                highest_slug = slug

    if highest_score > 89:
        return highest_slug
    
    return None

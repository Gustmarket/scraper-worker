from processing.entitites.pre_processed_item import PreProcessedItem
from processing.processors.pre_processed_items.categoriser.taxonomy import product_taxonomy

from thefuzz import process

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


def get_category(text, parent_category=None):
    """
    Determines the main category by searching for matching keywords in the combined text.
    Optionally prioritizes the search within the parent_category if provided.
    """
    # If a parent_category is passed, prioritize matching within that category
    if parent_category and parent_category in product_taxonomy:
        return parent_category


    highest_score = 0
    highest_category = None
    # Search across all categories if no parent_category is provided or no match found within it
    for category, details in product_taxonomy.items():
        (matched_keyword, score) = process.extractOne(text, details["keywords"])
        if score > highest_score:
            highest_score = score
            highest_category = category

    if highest_score > 89:
        return highest_category
    return None

def get_subcategory(combined_text, category):
    """
    Determines the subcategory within a main category by matching subcategory keywords in the combined text.
    """

    highest_score = 0
    highest_subcategory = None
    if category in product_taxonomy and "subcategories" in product_taxonomy[category]:
        for subcategory, sub_keywords in product_taxonomy[category]["subcategories"].items():
            (matched_keyword, score) = process.extractOne(combined_text, sub_keywords)
            if score > highest_score:
                highest_score = score
                highest_subcategory = subcategory

    if highest_score > 89:
        return highest_subcategory
    return None

def categorise_pre_processed_item(dirty_name_variants, parent_category):
    category = get_category(" ".join(dirty_name_variants), parent_category)
    if not category:
        return ("UNKNOWN","UNKNOWN")
    
    subcategory = get_subcategory(" ".join(dirty_name_variants), category)
    
    return (category, subcategory)

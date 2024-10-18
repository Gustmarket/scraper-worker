from processing.entitites.pre_processed_item import PreProcessedItem
from processing.processors.pre_processed_items.categoriser.taxonomy import product_taxonomy


def get_category(text, parent_category=None):
    """
    Determines the main category by searching for matching keywords in the combined text.
    Optionally prioritizes the search within the parent_category if provided.
    """
    # If a parent_category is passed, prioritize matching within that category
    if parent_category and parent_category in product_taxonomy:
        return parent_category

    # Search across all categories if no parent_category is provided or no match found within it
    for category, details in product_taxonomy.items():
        for keyword in details["keywords"]:
            if keyword in text:
                return category

    # Return None if no category match is found
    return None

def get_subcategory(combined_text, category):
    """
    Determines the subcategory within a main category by matching subcategory keywords in the combined text.
    """
    if category in product_taxonomy and "subcategories" in product_taxonomy[category]:
        for subcategory, sub_keywords in product_taxonomy[category]["subcategories"].items():
            for sub_keyword in sub_keywords:
                if sub_keyword in combined_text:
                    return subcategory
    
    # Return None if no subcategory match is found
    return None

def categorise_pre_processed_item(pre_processed_item: PreProcessedItem, parent_category):
    name_variants = " ".join(pre_processed_item.get_all_name_variants()).lower()
    category = get_category(name_variants, parent_category)
    if not category:
        return "UNKNOWN"
    
    # Step 2: Get the subcategory if applicable
    subcategory = get_subcategory(name_variants, category)
    
    pre_processed_item.category = category
    pre_processed_item.subcategories = [subcategory] if subcategory else []
    return pre_processed_item

from processing.processors.pre_processed_items.data_extractor.modeler.models.kites import kites

def get_brand_models(category, brand_slug):
    if category == "KITES":
        return kites.get(brand_slug)
    elif category == "KITEBOARDS":
        return None

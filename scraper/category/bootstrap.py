from datetime import datetime
import database
from celery.utils.log import get_task_logger
import hashlib

logger = get_task_logger(__name__)


def create_entity_to_bootstrap(url, category, condition):
    return {
        "hash": hashlib.sha256(
            (url.encode("UTF-8") if url else b'') +
            (category.encode("UTF-8") if category else b'') +
            (condition.encode("UTF-8") if condition else b'')
        ).hexdigest(),
        "type": "gustmarket-category-scraper",
        "next_update_interval_minutes": 1440,
        "config": {
            "url": url,
            "user_data": {
                "condition": condition,
                "category": category
            }
        }
    }

entities_to_bootstrap = [
    create_entity_to_bootstrap("https://www.kitemana.com/kite", "KITE", None),
    create_entity_to_bootstrap("https://www.kitemana.com/secondhand/kite", "KITE", "USED"),
    create_entity_to_bootstrap("https://www.flysurf.com/achat-kitesurf-aile-aile-a-boudin.htm?sectionid=25", "KITE", None),
    create_entity_to_bootstrap("https://www.kiteworldshop.com/en/13-kites", "KITE", None),
    create_entity_to_bootstrap("https://www.glissattitude.com/en/shop/category/kitesurf-aile-kitesurf-1111", "KITE", None),
    create_entity_to_bootstrap("https://www.magasin-glissevolution.com/14-ailes-de-kite", "KITE", None),
    create_entity_to_bootstrap("https://www.surfpirates.de/Kites-3", "KITE", None),
    create_entity_to_bootstrap("https://www.zephcontrol.com/21-ailes", "KITE", None),
    create_entity_to_bootstrap("https://matos.be/en/14-kites", "KITE", None),
    create_entity_to_bootstrap("https://www.coronation-industries.de/shop/en/75-tubekites#/availability-in_stock", "KITE", None),
    create_entity_to_bootstrap("https://www.you-love-it.eu/shop/en/kitesurf/kites/?p=1", "KITE", None),
    create_entity_to_bootstrap("https://www.icarus.eu/collections/kites", "KITE", None),
    create_entity_to_bootstrap("https://www.icarus.eu/collections/used-kites", "KITE", "USED"),
    create_entity_to_bootstrap("https://www.kitemana.com/kiteboard/twintip", "TWINTIP", None),
]


async def bootstrap_crawlable_entities():
    crawlable_entities_model = database.get_model("crawlable_entities")
    
    for entity in entities_to_bootstrap:
        existing_entity = crawlable_entities_model.find_one({"hash": entity["hash"]})
        
        if existing_entity is None:
            logger.info(f"Bootstrapping new crawlable entity: {entity['config']['url']}")
            crawlable_entities_model.insert_one({
                "hash": entity["hash"],
                "type": entity["type"],
                "next_update_interval_minutes": entity["next_update_interval_minutes"],
                "config": entity["config"],
                "next_update": datetime.now()
            })
        else:
            logger.debug(f"Crawlable entity already exists: {entity['config']['url']}")


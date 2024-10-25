from bs4 import BeautifulSoup
import requests
import datetime as dt
import database
from urllib.parse import urlparse
from celery.utils.log import get_task_logger

from scraper.utils import get_main_domain
logger = get_task_logger(__name__)
def get_trustpilot_stats(url: str):
    response = requests.get(f"https://www.trustpilot.com/review/{url}")
    web_page = response.text
    soup = BeautifulSoup(web_page, "html.parser")
    rating = soup.select_one('#business-unit-title .styles_rating__uyC6m p')
    if rating is None:
        return None
    rating = rating.text
    review_count = soup.select_one('#business-unit-title span span')
    if review_count is None:
        return None
    review_count = review_count.text
    review_count = int(''.join(filter(str.isdigit, review_count)))
    return {
        "rating": rating,
        "review_count": review_count,
    }

def extract_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

def scrape_trustpilot_stats():
    crawlable_entities = database.get_model("crawlable_entities").find({})
    unique_domains = set()
    for entity in crawlable_entities:
        if "url" in entity["config"]:
            domain = extract_domain(entity["config"]["url"])
            unique_domains.add(domain)
    
    logger.info(f"Unique domains: {unique_domains}")
    
    for domain in unique_domains:
        stats = get_trustpilot_stats(domain)
        if stats is None:
            logger.info(f"No stats for {domain}")
            continue
        logger.info(f"Stats for {domain}: {stats}")
        database.get_model("trustpilot_stats").find_one_and_update({
            "domain": domain,
            "domain_slug": get_main_domain(domain)
        }, {
            "$set": stats,
        }, upsert=True)

    return len(unique_domains)

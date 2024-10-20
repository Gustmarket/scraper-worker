from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from scraper.category.base import push_product_urls

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

def soup_category_scraper(source, link_selector, get_next_page_url):
    async def cat_s(url, enqueue_link, user_data):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        links = soup.select(link_selector)
        urls = []
        for link in links:
            link_href = link.get('href')
            link_url = urljoin(url, link_href)
            if link_url.startswith(('http://', 'https://')):
                urls.append(link_url)

        urls = list(set(urls))
        if len(links) > 0:
            await push_product_urls(scraped_url=url, source=source, urls=urls, user_data=user_data)
            await enqueue_link(get_next_page_url(url, soup))
        else:
            logger.info(f'no more links {source}')

    return lambda url, enqueue_link, playwright_context, user_data: cat_s(url, enqueue_link, user_data)

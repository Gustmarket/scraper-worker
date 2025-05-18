from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from scraper.category.base import push_product_urls

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

def get_links_with_soup(soup, link_selector, base_url):
    links = soup.select(link_selector)
    if len(links) == 0:
        return []
    urls = []
    for link in links:
        link_href = link.get('href')
        link_url = link_href if base_url is None else urljoin(base_url, link_href)
        if link_url.startswith(('http://', 'https://')):
            urls.append(link_url)
    return list(set(urls))

def soup_category_scraper(source, link_selector, get_next_page_url):
    async def cat_s(url, enqueue_link, user_data, page):
        # todo: add playwrigth/seleium get html and then use soup for the selectors #crazy
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        urls = get_links_with_soup(soup, link_selector, url)
        logger.debug(f"found {len(urls)} links for {url} with selector {link_selector}")

        if len(urls) == 0 and page == 0:
            raise Exception(f'no links found for {url}')
        
        if page > 50:
            raise Exception(f'more than 50 pages have been found. there might be an error')

        if len(urls) > 0:
            await push_product_urls(scraped_url=url, source=source, urls=urls, user_data=user_data)
            await enqueue_link(get_next_page_url(url, soup))
        else:
            logger.info(f'no more links {source}')

    return lambda url, enqueue_link, playwright_context, user_data, page: cat_s(url, enqueue_link, user_data, page)

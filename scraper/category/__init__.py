from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, urljoin
from celery.utils.log import get_task_logger

import pymongo
from pymongo import ReturnDocument

import database
from scraper.category.flysurf import flysurf_category_scraper
from scraper.category.pw import playwright_category_scraper
from scraper.category.shopify import shopify_category_scraper
from scraper.category.soup import soup_category_scraper
from scraper.utils import get_main_domain
logger = get_task_logger(__name__)

def get_next_page_url_query_param(url, param_key='page'):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    query_params[param_key] = [str(int(query_params.get(param_key, ["1"])[0]) + 1)]

    # Convert the modified query parameters back to a query string
    new_query_string = urlencode(query_params, doseq=True)
    # Create the modified URL
    return urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path,
                       parsed_url.params, new_query_string, parsed_url.fragment))


def get_next_page_url_query_param_factory(param_key):
    return lambda url, soup: get_next_page_url_query_param(url, param_key)


def no_next_page(url):
    logger.info('no next page handler')
    return None


def coronation_get_next_page_url(url):
    base_url = url.split('#')[0]
    if '#/page' in url:
        page_no = int(url.split('/page-')[1], 10)
        if page_no > 25:
            raise Exception("kind of too manypages for coronation")

        return f"{base_url}#/page-{page_no + 1}"
    else:
        return f"{url}#/page-{2}"


def glissattitude_get_next_page_url(url):
    split_req_url = url.split('/')

    if split_req_url[-2] == 'page':
        page_no = int(split_req_url[-1])
        cut_by = -1
        if page_no > 9:
            cut_by = -2

        if page_no > 25:
            raise Exception("kind of too manypages for glissattitude")

        new_url = url[0:cut_by] + str(page_no + 1)
    else:
        new_url = f'{url}/page/2'

    return new_url


def soup_selector_get_next_page_url(next_page_selector):
    def internal(url, soup):
        links = soup.select(next_page_selector)

        urls = []
        for link in links:
            link_href = link.get('href')
            link_url = urljoin(url, link_href)
            if link_url.startswith(('http://', 'https://')):
                urls.append(link_url)
        urls = list(set(urls))

        if len(urls) == 0:
            return None
        return urls[0]

    return lambda url, soup: internal(url, soup)


def surfpirates_get_next_page_url(url, soup):
    links = soup.select('.pagination .page-link[aria-label="next"]')
    urls = []
    for link in links:
        link_href = link.get('href')
        if link_href is not None and link_href != "":
            link_url = urljoin(url, link_href)
            if link_url.startswith(('http://', 'https://')):
                urls.append(link_url)
    urls = list(set(urls))
    if len(urls) == 0:
        return None
    return urls[0]


category_domain_handlers = {
    'flysurf.com': flysurf_category_scraper
}


def add_soup_handler(source, link_selector, get_next_page_url):
    handler = soup_category_scraper(source, link_selector, get_next_page_url)
    category_domain_handlers[source] = handler


def add_soup_next_page_selector_handler(source, link_selector, next_page_link_selector):
    add_soup_handler(source, link_selector, soup_selector_get_next_page_url(next_page_link_selector))


def add_soup_next_page_query_param_handler(source, link_selector, param_key):
    add_soup_handler(source, link_selector, get_next_page_url_query_param_factory(param_key))


def add_playwright_handler(source, link_selector, get_next_page_url, should_end=lambda x: False):
    handler = playwright_category_scraper(source, link_selector, get_next_page_url, should_end)
    category_domain_handlers[source] = handler


def add_shopify_handler(source):
    handler = shopify_category_scraper(source)
    category_domain_handlers[source] = handler


add_shopify_handler('icarus.eu')
# or "page" query param
# add_soup_next_page_selector_handler('icarus',
#                                     '.collection__products .product-grid-item .btn--quick',
#                                     '.pagination .next a')
add_soup_next_page_selector_handler('magasin-glissevolution.com',
                                    '#product_list .product-container .product-name',
                                    '#pagination_next_bottom a')
add_soup_next_page_selector_handler('matos.be',
                                    '#products .products article .product-title a',
                                    '#infinity-url-next')
add_playwright_handler('kiteworldshop.com',
                                    '.product_list .product-container .product-name',
                                    get_next_page_url_query_param_factory('p') 
                                    ) #'.pagination_next a'

add_soup_next_page_query_param_handler('kitemana.com',
                                       '.product__item a',
                                       'pg')
add_soup_next_page_query_param_handler('you-love-it.eu',
                                       '.cms-block-product-listing .product-box .product-name',
                                       'p')
add_soup_next_page_query_param_handler('zephcontrol.com',
                                       '.catalog__content .product-grid .product .product-link',
                                       'p')

add_soup_handler('surfpirates.de',
                 '#product-list .product-wrapper a.product-btn-center',
                 surfpirates_get_next_page_url)

add_playwright_handler('glissattitude.com', '#products_grid .tp-product-item .tp-link-dark',
                       glissattitude_get_next_page_url,
                       should_end=lambda urls: len(urls) < 20)
add_playwright_handler('coronation-industries.de', '.product_list .product-container .quick-view',
                       coronation_get_next_page_url)
add_playwright_handler('side-shore.com',
                       '#produit-wrapper .produit a',
                       get_next_page_url_query_param_factory('page'))


async def scrape_category(url, user_data, playwright_context, page=0):
    logger.info(f'scrape_category: category_url->{url} user_data: {user_data}')
    domain_handler = category_domain_handlers.get(get_main_domain(url))
    if domain_handler is None:
        logger.info(f'no domain handler for {url}')
        return
    if user_data is None:
        user_data = {}

    logger.info(f'scraping category: {url}')

    async def enqueue_link(new_url):
        await scrape_category(new_url, user_data, playwright_context, page + 1)

    await domain_handler(url=url, user_data=user_data, enqueue_link=enqueue_link, playwright_context=playwright_context, page=page)


async def get_one_expired_crawlable_entity_and_update(playwright_context):
    crawlable_entities_model = database.get_model("crawlable_entities")
    crawlable_entity = crawlable_entities_model.find_one_and_update({
        '$or': [
            {'next_update': {'$exists': False}},
            {'next_update': {'$lt': datetime.now()}}
        ]
    }, [{
        '$set': {
            'next_update': {'$add': [
                datetime.now(),
                {'$multiply': [{'$ifNull': ['$next_update_interval_minutes', 24 * 60]}, 60000.0]},
            ]},
            'last_error': None,
            'last_error_date': None
        }
    }], sort=[("next_update", pymongo.ASCENDING)], return_document=ReturnDocument.AFTER)
    try:
        if crawlable_entity is None:
            return
        if crawlable_entity['type'] == "gustmarket-category-scraper":
            config = crawlable_entity['config']
            exceptions = []
            try:
                await scrape_category(config['url'], config.get('user_data', {}), playwright_context, 0)
            except Exception as e:
                exceptions.append(e)
            if len(exceptions) > 0:
                raise exceptions[0]
        elif crawlable_entity['type'] == "facebook-group":
            # todo: probably still apify
            # run = apify.start_facebook_actor(crawlable_entity['config']['group_id'])
            logger.debug('fb not implemented')
    except Exception as e:
        logger.exception('error while scraping category')
        crawlable_entities_model.update_one({'_id': crawlable_entity['_id']},
                                            {'$set': {
                                                'last_error': str(e),
                                                'last_error_date': datetime.now(),
                                                'next_update': datetime.now() + timedelta(hours=1)
                                            }},
                                            upsert=False)

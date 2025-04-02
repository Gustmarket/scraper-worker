import asyncio
import uuid
from processing.data.utils import uniq_filter_none
from scraper.product.mapping import extract_product
from bs4 import BeautifulSoup

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

def combination_to_url_hash_path(combo):
    return f"{combo['id_attribute']}-{combo['group']}-{combo['attribute']}"


async def attributes_combinations_product_scraper(url,
                                                  playwright_context,
                                                  product_size_group_keys,
                                                  get_initial_url,
                                                  get_product_node_content):
    page = None
    run_id = uuid.uuid4()
    try:
        page = await playwright_context.new_page()
        await page.goto(url)

        attributes_combinations = await page.evaluate('() => window.attributesCombinations')

        initial_url = get_initial_url(url, attributes_combinations)
        if initial_url is None:
            logger.debug(f'{run_id} no initial url')
            return
        sizes = [c for c in attributes_combinations if c['group'] in product_size_group_keys]
        variants = []

        await page.goto(url.split('#')[0])
        last_price = None
        for sizeCombo in sizes:
            url = f"{initial_url}/{combination_to_url_hash_path(sizeCombo)}"
            logger.debug(f"{run_id} getting product: {url}")
            await page.goto(url)
            logger.debug(f"{run_id} {page.url}")

            tries = 0
            while tries < 10:
                tries = tries + 1
                await asyncio.sleep(1)
                data = await get_product_node_content(page)
                ui_price = await page.query_selector('#our_price_display')
                availability = None
                availability_element = await page.query_selector('#availability_value')
                if availability_element is not None:
                    availability = await availability_element.evaluate('x => x.innerText')

                item = extract_product(data, url)
                new_price = await ui_price.evaluate('x => x.innerText')
                item['extra_data'] = {
                    'price': new_price,
                    'size': sizeCombo['attribute'],
                    'url': url,
                    'availability': availability
                }
                logger.debug(f"{run_id} pricecompare: {last_price}, {new_price}")
                if last_price != new_price:
                    last_price = new_price
                    variants.append(item)
                    break

        result = {
            'id': await page.evaluate('() => window.id_product'),
            'variants': variants,
        }
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        # Find the target div
        description_div = soup.select_one("#short_description_block")
        
        if description_div:
            result["html_description"] = description_div.prettify()  # Keeps HTML formatting
            if description_div.text is not None:
                result["description"] = description_div.text.strip()
        logger.info(f"{run_id} we got {len(variants)} variants")
        return result, 'MICRODATA_VARIANTS_ITEM'
    except Exception as e:
        logger.info(f"{run_id} error")
        raise e
    finally:
        if page is not None:
            await page.close()

def check_requested_url_and_redirected_url(requested_url, redirected_url):
    normalized_requested_url = requested_url.replace('https://', '').replace('http://', '').replace('www.', '')
    normalized_redirected_url = redirected_url.replace('https://', '').replace('http://', '').replace('www.', '')
    return normalized_redirected_url.startswith(normalized_requested_url)
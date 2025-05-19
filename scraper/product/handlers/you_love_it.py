import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
import asyncio
from scraper.product.mapping import extract_product

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

async def map_variant_urls(base_url, variants):
    """
    variants: list of dicts like [{"group_id": "option_id"}, ...]
    product_id: the ID in the original product URL
    group_id: the group ID you're switching (e.g. "color", "size", etc.)
    """
    mapped_variants = []
    for variant in variants:
        logger.debug(f"you-love-it variant: {variant}")
        params = {
            "options": json.dumps(variant),
        }
        # encoded_params = {
        #     k: urllib.parse.quote(v) if k == "options" else v
        #     for k, v in params.items()
        # }

        try:
            response = requests.get(base_url, params=params, allow_redirects=True)
            response_json = response.json()
            url = response_json.get('url')
            logger.debug(f"you-love-it variant url: {url}")
            if url is not None:
                name = next(iter(variant.keys()))
                value = variant[name]
                mapped_variants.append({
                    "url": url,
                    "name": name,
                    "value": value
                })
                await asyncio.sleep(0.2)
        except Exception as e:
            logger.error(f"Error processing variant {variant}: {e}")
            continue

    return mapped_variants

def get_size_variants(soup):
    def variant_group_filter_predicate(variant_group):
        variant_name = variant_group.select_one('.product-detail-configurator-group-title')
        if variant_name is not None and variant_name.text is not None:
            variant_name = variant_name.text.strip()
        logger.debug(f"variant_name: {variant_name}")
        return variant_name is not None and variant_name == 'Kite Size'

    variant_wrapper = list(filter(variant_group_filter_predicate, soup.select('.product-detail-configurator-group')))
    if len(variant_wrapper) == 0:
        return []

    variants = list(map(lambda x: {x['name']: x['value']},
                    variant_wrapper[0].select('.product-detail-configurator-option > input')))
    
    # Remove duplicates by name-value combination
    seen_combos = set()
    unique_variants = []
    for variant in variants:
        name = next(iter(variant.keys()))
        value = variant[name]
        combo = f"{name}-{value}"
        if combo not in seen_combos:
            seen_combos.add(combo)
            unique_variants.append(variant)
    return unique_variants

def get_variant_switch_url(soup):
    form = soup.select_one('.product-detail-configurator form')
    if form is None:
        return None
    variant_switch_options = form.get('data-variant-switch-options')
    if variant_switch_options:
        variant_switch_options = json.loads(variant_switch_options)
        return variant_switch_options.get('url')
    return None

async def you_love_it(url, playwright_context):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    variant_switch_url = get_variant_switch_url(soup)
    if variant_switch_url is None:
        return None
    variants = get_size_variants(soup)
    if len(variants) == 0:
        return None
    mapped_variants = await map_variant_urls(variant_switch_url, variants)
    product_variants = []

    for mapped_variant in mapped_variants:
        prod_url = mapped_variant['url']
        logger.debug(f"you-love-it variant url: {prod_url} {mapped_variant}")
        response = requests.get(prod_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        extracted = extract_product(soup, url)
        input = soup.select_one(f'input[name="{mapped_variant.get("name")}"][value="{mapped_variant.get("value")}"]')
        extracted['extra_data'] = {
            "url": prod_url,
        }
        if input:
            label = soup.select_one(f'label[for="{input.get("id")}"]')
            if label:
                extracted['extra_data']['size'] = label.get('title', label.get_text(strip=True))
        
        product_variants.append(extracted)

    if len(product_variants) > 0:
        return ({
                    'variants': product_variants
                }, 'MICRODATA_VARIANTS_ITEM')

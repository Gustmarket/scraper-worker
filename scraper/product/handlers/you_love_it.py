import requests
from bs4 import BeautifulSoup

from scraper.product.mapping import extract_product


def get_size_variants(soup):
    def variant_group_filter_predicate(variant_group):
        variant_name = variant_group.select_one('.variant--name')
        return variant_name is not None and variant_name.text == 'Kite Size'

    variant_wrapper = list(filter(variant_group_filter_predicate, soup.select('.variant--group')))

    if len(variant_wrapper) == 0:
        return []

    return list(map(lambda x: {'size': x['title'], 'name': x['name'], 'value': x['value']},
                    variant_wrapper[0].select('.variant--option > input')))


async def you_love_it(url, user_data, playwright_context):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    variants = get_size_variants(soup)
    if len(variants) == 0:
        return None
    product_variants = []

    for variant in variants:
        prod_url = f"{url}&{variant['name']}={variant['value']}"
        print(prod_url)
        response = requests.get(prod_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        in_stock_input = soup.select(f'input[value="{variant["value"]}"]')
        in_stock_input = in_stock_input[0] if len(in_stock_input) > 0 else None
        in_stock = None
        if in_stock_input is not None:
            in_stock = in_stock_input.get("checked", None) == 'checked'
        if in_stock:
            extracted = extract_product(soup, url)
            extracted['extra_data'] = {
                "size": variant.get('size'),
                "url": prod_url,
                "in_stock": in_stock
            }
            product_variants.append(extracted)

    if len(product_variants) > 0:
        return ({
                    'variants': product_variants
                }, 'MICRODATA_VARIANTS_ITEM')

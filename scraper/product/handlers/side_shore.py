import requests
from bs4 import BeautifulSoup

from scraper.product.mapping import extract_product


async def side_shore(url, playwright_context):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    extracted = extract_product(soup, url)
    options = soup.select('.declinaison-product ul .li-opt')
    variants = []
    for option in options:
        size = option.select('.size label')[0].get('title')
        price = option.select('.price span')[0].text
        variants.append({
            'size': size,
            'price': price
        })

    return {**extracted,
        'extra_data': {
            'variants': variants
        }
    }, 'MICRODATA_ITEM'

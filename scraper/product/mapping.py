import extruct
from w3lib.html import get_base_url


def extract_product(node, url):
    base_url = get_base_url(url)
    data = extruct.extract(str(node), base_url, syntaxes=['microdata', 'json-ld', 'opengraph'])

    return data

import datetime
import hashlib

import database


async def push_product_urls(scraped_url, source, raw_urls, user_data):
    if raw_urls is None or len(raw_urls) == 0:
        return
    if source == 'matos.be':
        urls = list(map(lambda x: x.split('#')[0], raw_urls))
    else:
        urls = raw_urls
    def map_url(url):
        return {
            'url': url,
            'scraped_category_url': scraped_url,
            'source': source,
            'condition': user_data.get('condition', None),
            'category': user_data.get('category', None),
            'hash': hashlib.sha256(url.encode("UTF-8")).hexdigest(),
            'out_of_stock': False,
            'updated_at': datetime.datetime.utcnow()
        }

    url_posts = list(map(map_url, urls))
    database.bulk_upsert_items(items=url_posts, id_key='hash', model_name='product_urls', upsert=True)

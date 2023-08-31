import traceback


async def add_product(product, product_type, url, source, url_hash):
    if product is None:
        return

    print({
        'source': source,
        'hash': url_hash,
        'url': url,
        'loaded_url': url,
        'item': product,
        'type': product_type})


def route_scraper(source, handler):
    async def internal_handler(url, user_data, playwright_context):
        url_hash = user_data.get('hash')

        try:
            data = await handler(url=url, user_data=user_data, playwright_context=playwright_context)
            if data is None:
                print({
                    'source': source,
                    'hash': url_hash,
                    'url': url,
                    'loaded_url': url,
                    'type': "OUT_OF_STOCK"})
                return
            (product, product_type) = data
            await add_product(product=product,
                              product_type=product_type,
                              source=source,
                              url_hash=url_hash,
                              url=url
                              )
        except Exception as e:
            traceback.print_exc()
            print({
                'source': source,
                'hash': url_hash,
                'url': url,
                'loaded_url': url,
                'error': str(e),
                'type': "ERROR"})


    return lambda url, user_data, playwright_context: internal_handler(url, user_data, playwright_context)

from scraper.product.handlers.base import combination_to_url_hash_path, attributes_combinations_product_scraper


def get_initial_url(url, attributes_combinations):
    kite_only_param = next((c for c in attributes_combinations if c['attribute'] == 'kite_only'), None)
    if not kite_only_param:
        return None
    return f"{url.split('#')[0]}#/{combination_to_url_hash_path(kite_only_param)}"


async def get_product_node_content(page):
    return await page.evaluate('''() => {
                const col = document.getElementById('center_column').children[0];

                let elements = document.getElementsByClassName('products_block');
                [...elements].forEach(el => {
                    try {
                        col.removeChild(el);
                    } catch(e) {}
                });
                elements = document.getElementsByClassName('page-product-box');
                [...elements].forEach(el => {
                    try {
                        col.removeChild(el);
                    } catch(e) {}
                });

                return col.outerHTML;
            }''')


async def coronation_industries(url, user_data, playwright_context):
    return await attributes_combinations_product_scraper(
        url=url,
        user_data=user_data,
        playwright_context=playwright_context,
        kite_size_group_key='08_kite_grossen',
        get_initial_url=get_initial_url,
        get_product_node_content=get_product_node_content
    )

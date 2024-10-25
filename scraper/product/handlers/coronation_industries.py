from scraper.product.handlers.base import combination_to_url_hash_path, attributes_combinations_product_scraper


def get_initial_url(url, attributes_combinations):
    kite_only_param = next((c for c in attributes_combinations if c['attribute'] == 'kite_only'), None)
    board_only = next((c for c in attributes_combinations if c['attribute'] == 'board_only_mit_finnen'), None)
    # todo: include everything here and also scrape sets and everything else
    if not kite_only_param and not board_only:
        raise Exception("no kite or board only param")
    
    combination_path = combination_to_url_hash_path(kite_only_param) if kite_only_param else combination_to_url_hash_path(board_only)
    return f"{url.split('#')[0]}#/{combination_path}"


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


async def coronation_industries(url, playwright_context):
    return await attributes_combinations_product_scraper(
        url=url,
        playwright_context=playwright_context,
        product_size_group_keys=['08_kite_grossen',
                                  '06_langen_kiteboard_wakeboard_boardbags',
                                  '18_surfboard_sup_langen'],
        get_initial_url=get_initial_url,
        get_product_node_content=get_product_node_content
    )

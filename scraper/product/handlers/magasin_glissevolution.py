from scraper.product.handlers.base import attributes_combinations_product_scraper


def get_initial_url(url, attributes_combinations):
    return f"{url.split('#')[0]}#"


async def get_product_node_content(page):
    return await page.evaluate('''() => {
                        const col = document.getElementById('center_column').children[0];
                        const elements = document.getElementsByClassName('easycarousels');
                        [...elements].forEach(el => {
                            try {
                                col.removeChild(el);
                            } catch(e) {}
                        });

                        return col.outerHTML;
                    }''')

async def magasin_glissevolution(url, playwright_context):
    return await attributes_combinations_product_scraper(
        url=url,
        playwright_context=playwright_context,
        kite_size_group_key='taille',
        get_initial_url=get_initial_url,
        get_product_node_content=get_product_node_content
    )

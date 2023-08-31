import asyncio
import traceback

from scraper.product.mapping import extract_product


def combination_to_url_hash_path(combo):
    return f"{combo['id_attribute']}-{combo['group']}-{combo['attribute']}"


async def attributes_combinations_product_scraper(url,
                                                  user_data,
                                                  playwright_context,
                                                  kite_size_group_key,
                                                  get_initial_url,
                                                  get_product_node_content):
    page = None
    try:
        page = await playwright_context.new_page()
        await page.goto(url)

        attributes_combinations = await page.evaluate('() => window.attributesCombinations')

        initial_url = get_initial_url(url, attributes_combinations)
        if initial_url is None:
            print('no initial url')
            return
        sizes = [c for c in attributes_combinations if c['group'] == kite_size_group_key]
        variants = []

        await page.goto(url.split('#')[0])
        last_price = None
        for sizeCombo in sizes:
            url = f"{initial_url}/{combination_to_url_hash_path(sizeCombo)}"
            print(f"getting product: {url}")
            await page.goto(url)
            print(page.url)

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
                print(last_price, new_price)
                if last_price != new_price:
                    last_price = new_price
                    variants.append(item)
                    break

        result = {
            'id': await page.evaluate('() => window.id_product'),
            'variants': variants,
        }
        return result, 'MICRODATA_VARIANTS_ITEM'
    except Exception as e:
        traceback.print_exc()
    finally:
        if page is not None:
            await page.close()

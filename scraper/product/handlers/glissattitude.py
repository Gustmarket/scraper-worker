import asyncio
import traceback

from scraper.product.mapping import extract_product


async def glissattitude(url, user_data, playwright_context):
    page = None

    try:
        page = await playwright_context.new_page()
        await page.goto(url)

        # Find the size option select elements
        size_option_selects = await page.query_selector_all('li[data-attribute_name="Surface (m2)"] select')

        # Get the values of the options
        size_option_values = \
            (await page.evaluate('(els) => els.map(el => [...el.options].map(o => o.value))', size_option_selects))[0]

        product_variants = []

        for size_option_id in size_option_values:
            raw_item_url = f"{url}#attr={size_option_id}"
            await page.goto(raw_item_url)
            print(f"variant: {raw_item_url}")

            def req_pred(r):
                is_url = r.url == 'https://www.glissattitude.com/sale/get_combination_info_website'
                return is_url and r.method == 'POST'

            def page_has_diff_url():
                return page.url != raw_item_url and size_option_id in page.url

            async def wait_for_diff_url():
                while True:
                    await asyncio.sleep(0.5)
                    if page_has_diff_url():
                        break

            async with page.expect_request_finished(req_pred):
                await wait_for_diff_url()
                variant = extract_product(await page.content(), raw_item_url)
                product_size = await (await page.query_selector(f'option[data-value_id="{size_option_id}"]')).evaluate(
                    '(x) => x.getAttribute("data-value_name")')
                in_stock = product_size is not None

                if in_stock:
                    variant['extra_data'] = {
                        'size': product_size,
                        'url': page.url,
                        'in_stock': in_stock,
                    }
                    product_variants.append(variant)

        if len(product_variants) > 0:
            return ({
                        'variants': product_variants
                    }, 'MICRODATA_VARIANTS_ITEM')
    except Exception as e:
        traceback.print_exc()
    finally:
        if page is not None:
            await page.close()

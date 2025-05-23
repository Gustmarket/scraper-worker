import asyncio

from scraper.category.base import push_product_urls
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

async def flysurf_category_scraper(url, enqueue_link, playwright_context, user_data, page):
    page = None
    try:
        page = await playwright_context.new_page()
        await page.goto(url)
        tries = 0
        while tries < 20:
            tries = tries + 1
            await asyncio.sleep(2)
            # Find all elements matching the link selector and extract their href attributes
            urls = await page.evaluate(
                '(linkSelector) => Array.from(document.querySelectorAll(linkSelector)).map(el => el.href)',
                '.dp-product-view-grid .dp-product-item a')

            urls = list(set(urls))

            if len(urls) > 0:
                await push_product_urls(scraped_url=url, source='flysurf', urls=urls, user_data=user_data)
                next = await page.query_selector('li.page-item:not(.disabled) .page-link[title="Suivant"]')
                if next is None:
                    logger.info('no more links flysurf')
                    break
                await next.click()
            else:
                logger.info('no more links flysurf')
                break

    except Exception as e:
        raise e
    finally:
        if page is not None:
            await page.close()

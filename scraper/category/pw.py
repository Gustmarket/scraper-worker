import asyncio

from scraper.category.base import push_product_urls
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


def playwright_category_scraper(source, link_selector, get_next_page_url, should_end):
    async def cat_s(url, enqueue_link, playwright_context, user_data):
        page = None
        try:
            page = await playwright_context.new_page()
            await page.goto(url)
            await asyncio.sleep(2)
            # Find all elements matching the link selector and extract their href attributes
            urls = await page.evaluate(
                '(linkSelector) => Array.from(document.querySelectorAll(linkSelector)).map(el => el.href)',
                link_selector)

            urls = list(set(urls))
            if len(urls) > 0 and not should_end(urls):
                await push_product_urls(scraped_url=url, source=source, urls=urls, user_data=user_data)
                await enqueue_link(get_next_page_url(url))
            else:
                logger.info(f'no more links {source}')

        except Exception as e:
            raise e
        finally:
            if page is not None:
                await page.close()

    return lambda url, enqueue_link, playwright_context, user_data: cat_s(url, enqueue_link, playwright_context,
                                                                          user_data)

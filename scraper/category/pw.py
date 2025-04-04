import asyncio

from scraper.category.base import push_product_urls
from celery.utils.log import get_task_logger
from scraper.category.soup import get_links_with_soup
logger = get_task_logger(__name__)


def playwright_category_scraper(source, link_selector, get_next_page_url, should_end):
    async def cat_s(url, enqueue_link, playwright_context, user_data, page):
        page = None
        try:
            page = await playwright_context.new_page()
            await page.goto(url)
            await asyncio.sleep(2)
            # Find all elements matching the link selector and extract their href attributes
            urls = get_links_with_soup(await page.content(), link_selector, url)
            logger.debug(f"found {len(urls)} links for {url} with selector {link_selector}")

            urls = list(set(urls))
            if len(urls) == 0 and page == 0:
                raise Exception(f'no links found for {url}')
            
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

    return lambda url, enqueue_link, playwright_context, user_data, page: cat_s(url, enqueue_link, playwright_context,
                                                                          user_data, page)

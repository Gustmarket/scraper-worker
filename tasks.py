import asyncio
import os

from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from playwright.async_api import async_playwright

import database
from processing import process_raw_items, process_out_of_stock_raw_items, normalize_pre_processed_items, \
    upsert_products_from_normalized_items, upsert_product_offers, delete_out_of_stock_raw_items, \
    cleanup_inexsistent_items
from scraper.category import get_one_expired_crawlable_entity_and_update
from scraper.product import get_one_expired_product_url_and_update, get_one_expired_product_url_and_update_test
from scraper.category.bootstrap import bootstrap_crawlable_entities
from trustpilot import scrape_trustpilot_stats
app = Celery('tasks', broker=os.getenv("CELERY_BROKER_URL"))
logger = get_task_logger(__name__)

# app.conf.beat_schedule = {
#     'add-every-30-seconds': {
#         'task': 'tasks.add',
#         'schedule': 30.0,
#         'args': (16, 16)
#     },
# }
app.conf.timezone = 'UTC'


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60 * 15.0, schedule_url_batch.s(), name='schedule_url_batch every 15m')
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        scrape_trustpilot_stats_task.s(),
        name='scrape_trustpilot_stats once per day'
    )
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        schedule_crawlable_entity.s(),
        name="schedule_crawlable_entity every morning"
    )


@app.task
def schedule_url_batch():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(schedule_url_batch_async())
    process_raw_items_task.delay()


@app.task
def schedule_crawlable_entity():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(schedule_crawlable_entity_async())
    process_raw_items_task.delay()


@app.task
def re_process_source_raw_items(source):
    database.get_model('raw_items').update_many({
        'source': source
    }, {
        '$set': {
            'processed': False
        }
    })
    process_raw_items_task.delay()


@app.task
def re_process_brand_raw_items(brand_slug):
    normalized_items_for_brand = database.get_model('normalized_items').find({
        'item.brand_slug': brand_slug
    })

    hashes = []
    for normalized_item in normalized_items_for_brand:
        hashes.append(normalized_item['hash'])

    database.get_model('raw_items').update_many({
        'hash': {
            '$in': hashes
        }
    }, {
        '$set': {
            'processed': False
        }
    })

    process_raw_items_task.delay()


@app.task
def process_raw_items_task():
    nr_of_items = process_raw_items()
    if nr_of_items > 0:
        normalize_pre_processed_items_task.delay()
    process_out_of_stock_raw_items_task.delay()


@app.task
def process_out_of_stock_raw_items_task():
    process_out_of_stock_raw_items()


@app.task
def normalize_pre_processed_items_task():
    normalize_pre_processed_items()
    upsert_products_from_normalized_items_task.delay()
    upsert_product_offers_task.delay()


@app.task
def upsert_products_from_normalized_items_task():
    upsert_products_from_normalized_items()


@app.task
def upsert_product_offers_task():
    upsert_product_offers()


@app.task
def delete_out_of_stock_raw_items_task():
    delete_out_of_stock_raw_items()


@app.task
def cleanup_inexsistent_items_task():
    cleanup_inexsistent_items()

@app.task
def local_test_task():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(local_test_async())

@app.task
def bootstrap_crawlable_entities_task():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bootstrap_crawlable_entities())

@app.task
def scrape_trustpilot_stats_task():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scrape_trustpilot_stats())

def get_playwright_context(browser):
    return browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                               locale="en-US")

def execute_function_with_browser_factory(execute_function_fn):
    async def execute_function_with_browser(browser):
        playwright_context = None
        try:
            playwright_context = await get_playwright_context(browser)
            await execute_function_fn(playwright_context)
        except Exception as e:
            logger.exception(f'get_one_expired_product_url_and_update_with_browser_error: ${e}')
        finally:
            if playwright_context is not None:
                try:
                    await playwright_context.close()
                except Exception as e:
                    # ignore
                    pass
    return execute_function_with_browser

async def schedule_crawlable_entity_async():
    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            for i in range(20):
                try:
                    logger.info(f'schedule_crawlable_entity_async: ${i}')

                    if not browser.is_connected():
                        logger.info("Browser was closed, launching new one...")
                        browser = await playwright.chromium.launch(headless=True)
                    fn = execute_function_with_browser_factory(get_one_expired_crawlable_entity_and_update)
                    await fn(browser)
                except Exception as e:
                    logger.exception(f'schedule_crawlable_entity_async_error: ${e}')
    except Exception as e:
        logger.exception(f'schedule_crawlable_entity_async_wrapper_error: ${e}')


async def get_one_expired_product_url_and_update_with_browser(browser):
    fn = execute_function_with_browser_factory(get_one_expired_product_url_and_update)
    return await fn(browser)

async def schedule_url_batch_async():
    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            for i in range(30):
                try:
                    logger.info(f'schedule_url_batch_async: ${i} ${browser.is_connected()}')
                    if not browser.is_connected():
                        logger.info("Browser was closed, launching new one...")
                        browser = await playwright.chromium.launch(headless=True)
                    tasks = [get_one_expired_product_url_and_update_with_browser(browser) for _ in range(1)]
                    await asyncio.gather(*tasks)
                    logger.info(f'end schedule_url_batch_async: ${i}')
                except Exception as e:
                    logger.exception(f'schedule_url_batch_async_error: ${e}')
    except Exception as e:
        logger.exception(f'schedule_url_batch_async_wrapper_error: ${e}')


async def local_test_async():
    # todo: count before starting
    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            for i in range(1):
                try:
                    logger.info(f'local_test_async: ${i}')
                    if not browser.is_connected():
                        logger.info("Browser was closed, launching new one...")
                        browser = await playwright.chromium.launch(headless=True)
                    fn_to_execute = execute_function_with_browser_factory(get_one_expired_product_url_and_update_test)
                    await fn_to_execute(browser)
                except Exception as e:
                    logger.exception(f'local_test_async_error: ${e}')
    except Exception as e:
        logger.exception(f'local_test_async_wrapper_error: ${e}')


# process_raw_items_task.delay()
# normalize_pre_processed_items_task.delay()
# process_out_of_stock_raw_items_task.delay()
local_test_task.delay()
# schedule_url_batch.delay()
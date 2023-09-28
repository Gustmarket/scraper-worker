import asyncio
import os

from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from playwright.async_api import async_playwright

import database
from processing.raw_items_processor import process_raw_items, normalize_pre_processed_items, \
    upsert_products_from_normalized_items, upsert_product_offers, delete_out_of_stock_raw_items, \
    cleanup_inexsistent_items, process_out_of_stock_raw_items
from scraper.category import get_one_expired_crawlable_entity_and_update
from scraper.product import get_one_expired_product_url_and_update

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
    sender.add_periodic_task(600.0, schedule_url_batch.s(), name='schedule_url_batch every 10m')
    sender.add_periodic_task(600.0, schedule_url_batch.s(), name='schedule_url_batch_2 every 10m')
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


async def schedule_crawlable_entity_async():
    # todo: count before starting
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        playwright_context = await browser.new_context()
        for i in range(1, 3):
            logger.info(f'schedule_url_batch_async: ${i}')
            await get_one_expired_crawlable_entity_and_update(playwright_context)


async def schedule_url_batch_async():
    # todo: count before starting
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        playwright_context = await browser.new_context()
        for i in range(1, 12):
            logger.info(f'schedule_url_batch_async: ${i}')
            await get_one_expired_product_url_and_update(playwright_context)

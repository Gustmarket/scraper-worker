import asyncio
import os

from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from playwright.async_api import async_playwright

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
    # # Executes every Monday morning at 0:00 a.m.
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        schedule_crawlable_entity.s(),
        name="schedule_crawlable_entity every morning"
    )


@app.task
def schedule_url_batch():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(schedule_url_batch_async())


@app.task
def schedule_crawlable_entity():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(schedule_crawlable_entity_async())


async def schedule_crawlable_entity_async():
    # todo: count before starting
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        playwright_context = await browser.new_context()
        await get_one_expired_crawlable_entity_and_update(playwright_context)


async def schedule_url_batch_async():
    # todo: count before starting
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        playwright_context = await browser.new_context()
        for i in range(1, 10):
            print('schedule_url_batch_async', i)
            await get_one_expired_product_url_and_update(playwright_context)


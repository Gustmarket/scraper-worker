import asyncio
import os

from celery import Celery
from celery.utils.log import get_task_logger
from playwright.async_api import async_playwright

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
    print('setup_periodic_tasks')
    sender.add_periodic_task(120.0, schedule_url_batch.s('hello'), name='schedule_url_batch every 120s')

    # # Executes every Monday morning at 7:30 a.m.
    # sender.add_periodic_task(
    #     crontab(hour=7, minute=30, day_of_week=1),
    #     test.s('Happy Mondays!'),
    # )


@app.task
def schedule_url_batch(arg):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(schedule_url_batch_async(arg))


async def schedule_url_batch_async(arg):
    # todo: count before starting
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        playwright_context = await browser.new_context()
        for i in range(1, 10):
            print('schedule_url_batch_async', i)
            await get_one_expired_product_url_and_update(playwright_context)


schedule_url_batch.delay('ZenRows')

import asyncio
import os
import traceback
from datetime import datetime, timedelta

import pymongo
from celery import Celery
from celery.utils.log import get_task_logger
from celery.schedules import crontab
from playwright.async_api import async_playwright

from database import get_model
from scraper.product import product_route

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
    product_urls_model = get_model("product_urls")
    cursor = product_urls_model.find({}, sort=[("next_update", pymongo.ASCENDING)], limit=5)

    batch = []
    for doc in cursor:
        batch.append(doc)

    query_by_ids = {'_id': {'$in': list(map(lambda x: x['_id'], batch))}}
    try:
        if len(batch) > 0:
            product_urls_model.update_many(query_by_ids,
                                           {'$set': {
                                               'next_update': datetime.now() + timedelta(hours=47)
                                           }},
                                           upsert=False)
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            playwright_context = await browser.new_context()
            for request in batch:
                url = request['url']
                user_data = {"hash": request['hash']}
                print(f'Scraping {url} ...')
                print(request)
                await product_route(url, user_data, playwright_context)
    except Exception as e:
        traceback.print_exc()
        product_urls_model.update_many(query_by_ids,
                                       {'$set': {
                                           'next_update': datetime.now() + timedelta(hours=1)
                                       }},
                                       upsert=False)

schedule_url_batch.delay('ZenRows')

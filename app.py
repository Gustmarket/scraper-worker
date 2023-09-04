import os
from flask import Flask, flash, render_template, redirect, request
from tasks import schedule_crawlable_entity,schedule_url_batch, process_out_of_stock_raw_items_task

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', "super-secret")


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/schedule_crawlable_entity', methods=['POST'])
def perform_schedule_crawlable_entity():
    schedule_crawlable_entity.delay()
    flash("Your schedule_crawlable_entity job has been submitted.")
    return redirect('/')

@app.route('/process_out_of_stock_raw_items_task', methods=['POST'])
def perform_process_out_of_stock_raw_items_task():
    process_out_of_stock_raw_items_task.delay()
    flash("Your process_out_of_stock_raw_items_task job has been submitted.")
    return redirect('/')

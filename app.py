import os

from flask import Flask, flash, render_template, redirect, request
from flask_basicauth import BasicAuth

from tasks import schedule_crawlable_entity, schedule_url_batch, process_out_of_stock_raw_items_task, \
    re_process_source_raw_items, re_process_brand_raw_items

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', "super-secret")
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = os.getenv('AUTH_PW', 'admin')
app.config['BASIC_AUTH_FORCE'] = True
basic_auth = BasicAuth(app)


@app.route('/')
@basic_auth.required
def main():
    return render_template('main.html')


@app.route('/schedule_crawlable_entity', methods=['POST'])
@basic_auth.required
def perform_schedule_crawlable_entity():
    schedule_crawlable_entity.delay()
    flash("Your schedule_crawlable_entity job has been submitted.")
    return redirect('/')


@app.route('/schedule_url_batch', methods=['POST'])
@basic_auth.required
def perform_schedule_url_batch():
    schedule_url_batch.delay()
    flash("Your schedule_url_batch job has been submitted.")
    return redirect('/')


@app.route('/process_out_of_stock_raw_items_task', methods=['POST'])
@basic_auth.required
def perform_process_out_of_stock_raw_items_task():
    process_out_of_stock_raw_items_task.delay()
    flash("Your process_out_of_stock_raw_items_task job has been submitted.")
    return redirect('/')


@app.route('/re_process_source_raw_items', methods=['POST'])
@basic_auth.required
def perform_re_process_source_raw_items():
    source = request.form['source']
    if source is None or source == "":
        flash("source is required")
        return redirect('/')
    re_process_source_raw_items.delay(source)
    flash("Your re_process_source_raw_items job has been submitted.")
    return redirect('/')


@app.route('/re_process_brand_raw_items', methods=['POST'])
@basic_auth.required
def perform_re_process_brand_raw_items():
    brand_slug = request.form['brand_slug']
    if brand_slug is None or brand_slug == "":
        flash("brand_slug is required")
        return redirect('/')
    re_process_brand_raw_items.delay(brand_slug)
    flash("Your brand_slug job has been submitted.")
    return redirect('/')

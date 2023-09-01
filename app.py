import os
from flask import Flask, flash, render_template, redirect, request
from tasks import schedule_crawlable_entity

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', "super-secret")


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/add', methods=['POST'])
def add_inputs():
    schedule_crawlable_entity.delay()
    flash("Your addition job has been submitted.")
    return redirect('/')

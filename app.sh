#!/bin/sh

source .env && gunicorn app:app

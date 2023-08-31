#!/bin/sh

source .env && celery --app tasks worker --loglevel=info

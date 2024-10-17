#!/bin/sh
source .env
celery --app tasks beat -l debug

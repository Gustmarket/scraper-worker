#!/bin/sh
export CELERY_BROKER_URL="redis://@localhost:6379" && celery -A tasks worker --loglevel=info

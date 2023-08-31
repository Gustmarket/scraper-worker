#!/bin/sh
docker run -d -p 6379:6379 --name myredis --network redisnet redis

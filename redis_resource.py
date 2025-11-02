import json
import config

from upstash_redis import Redis


redis = Redis(
    url=config.REDIS_URL,
    token=config.REDIS_TOKEN
)

connection_link = f"rediss://default:{config.REDIS_TOKEN}@{config.REDIS_URL}:{config.REDIS_PORT}?ssl_cert_reqs=required"

def set_redis(key, value):
    redis.setex(key, 60*60, value)

def get_redis(key):
    return json.loads(redis.get(key))

def increment_redis(key, increment_value):
    redis.incrby(key, increment_value)
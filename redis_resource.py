import json
import config

from upstash_redis import Redis


redis = Redis(
    url=config.REDIS_URL,
    token=config.REDIS_TOKEN
)

def set_redis(key, value):
    redis.setex(key, 60*60, value)

def get_redis(key):
    return json.loads(redis.get(key))

def increment_redis(key, increment_value):
    redis.incrby(key, increment_value)
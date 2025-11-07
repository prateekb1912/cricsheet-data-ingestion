import json
from app.config import REDIS_URL, REDIS_TOKEN, REDIS_PORT

from upstash_redis import Redis


redis = Redis(
    url=REDIS_URL,
    token=REDIS_TOKEN
)

connection_link = f"rediss://default:{REDIS_TOKEN}@{REDIS_URL}:{REDIS_PORT}?ssl_cert_reqs=required"

def set_redis(key, value):
    redis.setex(key, 60*60, value)

def get_redis(key):
    return json.loads(redis.get(key))

def increment_redis(key, increment_value):
    redis.incrby(key, increment_value)


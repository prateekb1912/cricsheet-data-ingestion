import json
import os

from dotenv import load_dotenv
from upstash_redis import Redis

load_dotenv()

redis = Redis(
    url=os.getenv("REDIS_URL"),
    token=os.getenv("REDIS_TOKEN")
)

def set_redis(key, value):
    redis.setex(key, 60*60, value)

def get_redis(key):
    return json.loads(redis.get(key))

def increment_redis(key, increment_value):
    redis.incrby(key, increment_value)
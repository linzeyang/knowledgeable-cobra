"""redis.py"""

import os

from redis import asyncio as redis

URI = os.getenv("REDIS_URI", "")

pool = None


def get_client():
    global pool

    if pool is None:
        pool = redis.ConnectionPool.from_url(url=URI)

    return redis.Redis.from_pool(connection_pool=pool)

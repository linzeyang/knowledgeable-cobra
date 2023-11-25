"""mongo.py"""

import os

from motor import motor_asyncio as motor

URI = str(os.getenv("MONGO_CONNECTION"))

client = None


def get_client():
    global client

    if client is None:
        client = motor.AsyncIOMotorClient(URI)

    return client

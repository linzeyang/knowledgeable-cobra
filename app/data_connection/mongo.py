"""mongo.py"""

import os

from motor import motor_asyncio as motor

URI = os.getenv("MONGO_URI", "")

client = None


def get_client() -> motor.AsyncIOMotorClient:
    global client

    if client is None:
        client = motor.AsyncIOMotorClient(URI, uuidRepresentation="standard")

    return client

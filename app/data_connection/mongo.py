"""mongo.py"""

import os

from motor import motor_asyncio as motor

URI = os.getenv("MONGO_URI", "")

client = None


def get_client() -> motor.AsyncIOMotorClient:
    global client

    if client is None:
        # Explicitly set uuidRepresentation = "standard" to handle UUID fields
        # Reference: https://pymongo.readthedocs.io/en/stable/examples/uuid.html
        client = motor.AsyncIOMotorClient(URI, uuidRepresentation="standard")

    return client

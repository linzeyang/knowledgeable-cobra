"""dashvector.py"""

import os

from dashvector import Client

API_KEY = os.getenv("DASHVECTOR_API_KEY", "")


def get_client():
    client = Client(api_key=API_KEY, timeout=5)

    return client

"""qdrant.py"""

import os

from qdrant_client import QdrantClient

URI = os.getenv("QDRANT_URI", "")
API_KEY = os.getenv("QDRANT_API_KEY", "")


def get_client():
    client = QdrantClient(url=URI, api_key=API_KEY)

    return client

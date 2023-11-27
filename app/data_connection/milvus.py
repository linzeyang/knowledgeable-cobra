"""milvus.py"""

import os

from pymilvus import connections

URI = os.getenv("MILVUS_URI", "")
API_KEY = os.getenv("MILVUS_API_KEY", "")


def make_connection():
    connections.connect(uri=URI, token=API_KEY)

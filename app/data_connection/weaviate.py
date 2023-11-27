"""weaviate.py"""

import os

from weaviate import AuthApiKey, Client

URI = os.getenv("WEAVIATE_URI", "")
API_KEY = os.getenv("WEAVIATE_API_KEY", "")


def get_client():
    auth_config = AuthApiKey(api_key=API_KEY)
    client = Client(url=URI, auth_client_secret=auth_config)
    return client

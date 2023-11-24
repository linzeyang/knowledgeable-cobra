"""authenticator.py"""

from typing import Callable
from uuid import UUID

DUMMY_USER_DB = {
    "joe.bloggs": UUID("cfc0bd70-be32-4d62-85f8-cbdb65ce2ab7"),
}


class BaseAuthenticator:
    def authenticate(*args, **kwargs):
        raise NotImplementedError


class UserAuthenticator(BaseAuthenticator):
    def authenticate(*args, **kwargs):
        if uuid := DUMMY_USER_DB.get(kwargs["username"]):
            return uuid

        return False


def get_authenticator(purpose: str) -> Callable:
    mapping = {
        "signin": UserAuthenticator,
    }

    return mapping[purpose]

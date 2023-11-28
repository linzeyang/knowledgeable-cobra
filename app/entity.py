"""
entity.py

Reference: https://www.mongodb.com/developer/languages/python/python-quickstart-fastapi/
"""

from datetime import date, datetime
from typing import Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field, HttpUrl
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]


class UserAuth(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)


class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    uuid: UUID = Field(default_factory=uuid4)
    username: str = Field(..., min_length=3, max_length=32)
    email: EmailStr = Field(...)
    mobile: Optional[str] = Field(default=None, min_length=7, max_length=32)
    date_joined: date = Field(default_factory=datetime.now().date)
    date_purged: Optional[date] = Field(default=None)


class Library(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    uuid: UUID = Field(default_factory=uuid4)
    user_id: UUID = Field(...)
    name: str = Field(..., min_length=3, max_length=32)
    description: str = Field(..., min_length=3, max_length=64)
    embedding: str = Field(..., min_length=1, max_length=64)
    vectordb: str = Field(..., min_length=1, max_length=128)
    datetime_created: datetime = Field(default_factory=datetime.now)
    datetime_removed: Optional[datetime] = Field(default=None)


class LibraryList(BaseModel):
    libraries: list[Library]


class Document(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    uuid: UUID = Field(default_factory=uuid4)
    user_id: UUID = Field(...)
    library_id: UUID = Field(...)
    type: str = Field(..., max_length=64)
    path: Union[HttpUrl, str] = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=128)
    datetime_created: datetime = Field(default_factory=datetime.now)
    datetime_removed: Optional[datetime] = Field(default=None)


class DocumentList(BaseModel):
    documents: list[Document]


class Dialogue(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    uuid: UUID = Field(default_factory=uuid4)
    user_id: UUID = Field(...)
    library_id: UUID = Field(...)
    llm: str = Field(..., min_length=3, max_length=128)
    title: str = Field(default="New Dialogue", min_length=3, max_length=128)
    content: list = Field(default=[], min_length=0)
    datetime_created: datetime = Field(default_factory=datetime.now)
    datetime_updated: datetime = Field(default_factory=datetime.now)
    datetime_removed: Optional[datetime] = Field(default=None)


class DialogueList(BaseModel):
    dialogues: list[Dialogue]


class UserPrompt(BaseModel):
    content: str = Field(..., min_length=1, max_length=1024)

"""entity.py"""

from datetime import date, datetime
from typing import Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class UserAuth(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)


class User(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    username: str = Field(..., min_length=3, max_length=32)
    email: EmailStr = Field(...)
    mobile: Optional[str] = Field(default=None, min_length=7, max_length=32)
    date_joined: date = Field(default_factory=datetime.now().date)
    date_purged: Optional[date] = Field(default=None)


class Library(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    user_id: UUID = Field(...)
    name: str = Field(..., min_length=3, max_length=32)
    description: str = Field(..., min_length=3, max_length=64)
    embedding: str = Field(..., min_length=1, max_length=64)
    vectordb: str = Field(..., min_length=1, max_length=128)
    datetime_created: datetime = Field(default_factory=datetime.now)
    datetime_removed: Optional[datetime] = Field(default=None)


class Document(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    user_id: UUID = Field(...)
    library_id: UUID = Field(...)
    type: str = Field(..., max_length=64)
    path: Union[HttpUrl, str] = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=128)
    datetime_created: datetime = Field(default_factory=datetime.now)
    datetime_removed: Optional[datetime] = Field(default=None)


class Dialogue(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    user_id: UUID = Field(...)
    library_id: UUID = Field(...)
    llm: str = Field(..., min_length=3, max_length=128)
    title: str = Field(..., min_length=3, max_length=128)
    content: str = Field(default="", min_length=0)
    datetime_created: datetime = Field(default_factory=datetime.now)
    datetime_updated: datetime = Field(default_factory=datetime.now)
    datetime_removed: Optional[datetime] = Field(default=None)


class UserPrompt(BaseModel):
    content: str = Field(..., min_length=1, max_length=1024)

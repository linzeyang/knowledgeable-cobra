"""controller.py"""

import os
from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from fastapi import UploadFile
from langchain.schema.messages import AIMessage, HumanMessage

from app.data_connection.mongo import get_client
from app.document_processor import process_document
from app.entity import (
    Dialogue,
    DialogueList,
    Document,
    DocumentList,
    Library,
    LibraryList,
    UserPrompt,
)
from app.prompt_processor import construct_chat_history, get_prompt_processor

PROJECT_NAME = os.getenv("PROJECT_NAME", "knowledgeable-cobra")


def _get_collection(collection_name: str):
    client = get_client()

    return client.get_database(PROJECT_NAME).get_collection(name=collection_name)


async def get_libraries(user_id: UUID):
    collection = _get_collection(collection_name="library")

    cursor = collection.find({"user_id": user_id})

    libraries = await cursor.to_list(length=10)

    return LibraryList(libraries=libraries)


async def create_library(instance: Library):
    collection = _get_collection(collection_name="library")

    await collection.insert_one(
        document=instance.model_dump(by_alias=True, exclude=["id"])
    )

    return instance


async def get_library(user_id: UUID, library_id: UUID):
    collection = _get_collection(collection_name="library")

    resp = await collection.find_one(
        {
            "user_id": user_id,
            "uuid": library_id,
        }
    )

    return resp


async def update_library(instance: Library):
    # collection = _get_collection(collection_name="library")

    ...


async def remove_library(user_id: UUID, library_id: UUID):
    # collection = _get_collection(collection_name="library")

    ...


async def get_documents(user_id: UUID, library_id: UUID):
    collection = _get_collection(collection_name="document")

    cursor = collection.find({"user_id": user_id, "library_id": library_id})

    documents = await cursor.to_list(length=20)

    return DocumentList(documents=documents)


async def create_document(
    user_id: UUID,
    instance: Union[Document, UploadFile],
    library_id: Optional[UUID] = None,
):
    collection = _get_collection(collection_name="document")

    if isinstance(instance, UploadFile):
        document = Document(
            user_id=user_id,
            library_id=library_id,
            type=instance.content_type or "file",
            path="",
            name=instance.filename or "file",
        )
    else:
        document = instance

    await collection.insert_one(
        document=document.model_dump(by_alias=True, exclude=["id"])
    )

    return instance


async def get_document(user_id: UUID, document_id: UUID):
    collection = _get_collection(collection_name="document")

    resp = await collection.find_one(
        {
            "user_id": user_id,
            "uuid": document_id,
        }
    )

    return resp


async def emb_document(user_id: UUID, document_id: UUID):
    collection = _get_collection(collection_name="document")

    document = await collection.find_one(
        {
            "user_id": user_id,
            "uuid": document_id,
        }
    )

    collection = _get_collection(collection_name="library")

    library = await collection.find_one(
        {
            "user_id": user_id,
            "uuid": document["library_id"],
        }
    )

    result = await process_document(
        document_type=document["type"],
        document_path=document["path"],
        library_uuid=library["uuid"],
        library_embedding=library["embedding"],
        library_vectordb=library["vectordb"],
    )

    return result


async def remove_document(user_id: UUID, document_id: UUID):
    # collection = _get_collection(collection_name="document")
    ...


async def create_dialogue(user_id: UUID, instance: Dialogue):
    collection = _get_collection(collection_name="dialogue")

    await collection.insert_one(
        document=instance.model_dump(by_alias=True, exclude=["id"])
    )

    return instance


async def get_dialogues(user_id: UUID, library_id: UUID):
    collection = _get_collection(collection_name="dialogue")

    cursor = collection.find({"user_id": user_id, "library_id": library_id})

    dialogues = await cursor.to_list(length=20)

    return DialogueList(dialogues=dialogues)


async def get_dialogue(user_id: UUID, dialogue_id: UUID):
    collection = _get_collection(collection_name="dialogue")

    resp = await collection.find_one(
        {
            "user_id": user_id,
            "uuid": dialogue_id,
        }
    )

    return resp


async def update_dialogue(user_id: UUID, dialogue_id: UUID, user_prompt: UserPrompt):
    dialogue_collection = _get_collection(collection_name="dialogue")

    dialogue = await dialogue_collection.find_one(
        {"user_id": user_id, "uuid": dialogue_id}
    )

    library_collection = _get_collection(collection_name="library")

    library = await library_collection.find_one(
        {"user_id": user_id, "uuid": dialogue["library_id"]}
    )

    history = construct_chat_history(messages=dialogue["content"])

    response: AIMessage = await get_prompt_processor(
        embedding=library["embedding"],
        vectordb=library["vectordb"],
        collection=library["uuid"],
        llm=dialogue["llm"],
    )({"question": user_prompt.content, "chat_history": history})

    history.append(HumanMessage(content=user_prompt.content))
    history.append(response)

    history = [
        {"type": message.type, "content": message.content} for message in history
    ]

    dialogue_collection.update_one(
        {"user_id": user_id, "uuid": dialogue_id},
        {"$set": {"content": history, "datetime_updated": datetime.now()}},
    )

    return response

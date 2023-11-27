"""controller.py"""

import os
from uuid import UUID

from app.data_connection.mongo import get_client
from app.document_processor import process_document
from app.entity import Document, Library

PROJECT_NAME = os.getenv("PROJECT_NAME", "knowledgeable-cobra")


def _get_collection(collection_name: str):
    client = get_client()

    return client.get_database(PROJECT_NAME).get_collection(name=collection_name)


async def get_libraries(user_id: UUID):
    collection = _get_collection(collection_name="library")

    cursor = collection.find({"user_id": user_id})

    resp = await cursor.to_list(length=10)

    print(type(resp), len(resp))

    return resp


async def create_library(instance: Library):
    collection = _get_collection(collection_name="library")

    await collection.insert_one(document=instance.dict())

    return instance


async def get_library(user_id: UUID, library_id: UUID):
    collection = _get_collection(collection_name="library")

    resp = await collection.find_one(
        {
            "user_id": user_id,
            "library_id": library_id,
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

    resp = await cursor.to_list(length=20)

    print(type(resp), len(resp))

    return resp


async def create_document(user_id: UUID, instance: Document):
    collection = _get_collection(collection_name="document")

    await collection.insert_one(document=instance.dict())

    return instance


async def get_document(user_id: UUID, document_id: UUID):
    collection = _get_collection(collection_name="document")

    resp = await collection.find_one(
        {
            "user_id": user_id,
            "document_id": document_id,
        }
    )

    return resp


async def emb_document(user_id: UUID, document_id: UUID):
    # collection = _get_collection(collection_name="document")

    # document = await collection.find_one(
    #     {
    #         "user_id": user_id,
    #         "document_id": document_id,
    #     }
    # )

    document = Document(
        uuid=document_id,
        user_id=user_id,
        library_id=UUID("8a304dd0-45fe-4c8c-ac81-d513ca722fb8"),
        type="web_page",
        path="https://realpython.com/python-rich-package/",
        name="xxx",
    )

    # collection = _get_collection(collection_name="library")

    # library = await collection.find_one({"library_id": document.library_id})

    library = Library(
        uuid=document.library_id,
        user_id=user_id,
        name="xxx",
        description="xxx",
        embedding="cohere",
        vectordb="qdrant",
    )

    result = await process_document(
        document_type=document.type,
        document_path=document.path,
        library_uuid=library.uuid,
        library_embedding=library.embedding,
        library_vectordb=library.vectordb,
    )

    return result


async def remove_document(user_id: UUID, document_id: UUID):
    # collection = _get_collection(collection_name="document")
    ...

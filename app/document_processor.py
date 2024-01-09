"""document_processor.py"""

import os
from uuid import UUID

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.embeddings.cohere import CohereEmbeddings
from langchain_community.embeddings.dashscope import DashScopeEmbeddings
from langchain_community.vectorstores.dashvector import DashVector
from langchain_community.vectorstores.milvus import Milvus
from langchain_community.vectorstores.qdrant import Qdrant
from langchain_community.vectorstores.weaviate import Weaviate

from app.data_connection.dashvector import get_client as get_dashvector_client
from app.data_connection.weaviate import get_client as get_weaviate_client


def get_pdf_loader(document_path: str):
    loader = PyPDFLoader(file_path=document_path)

    return loader


def get_web_page_loader(document_path: str):
    loader = WebBaseLoader(web_path=document_path)

    return loader


def get_cohere_embedding():
    # return CohereEmbeddings(
    #     model="embed-multilingual-light-v3.0", max_retries=5, request_timeout=20
    # )
    return CohereEmbeddings(max_retries=5, request_timeout=20)


def get_dashscope_embedding():
    return DashScopeEmbeddings(model="text-embedding-v2", max_retries=5)


async def get_dashvector_collection(
    library_embedding: str, library_uuid: UUID, documents: list[Document]
):
    client = get_dashvector_client()

    # character must be in [a-zA-Z0-9] and symbols[_, -] and length must be in [3,32]
    collection_name = library_uuid.hex

    collection = client.get(name=collection_name)

    if not collection:
        instance = await DashVector.afrom_documents(
            documents=documents,
            embedding=EMBEDDING_MAPPING[library_embedding](),
            collection_name=collection_name,
        )
    else:
        instance = await DashVector(
            collection=collection,
            embedding=EMBEDDING_MAPPING[library_embedding](),
            text_field="text",
        ).aadd_documents(
            documents=documents,
        )

    return instance


async def get_milvus_collection(
    library_embedding: str, library_uuid: UUID, documents: list[Document]
):
    instance = await Milvus.afrom_documents(
        documents=documents,
        embedding=EMBEDDING_MAPPING[library_embedding](),
        # The first character of a collection name must be an underscore or letter
        collection_name=f"_{library_uuid.hex}",
        connection_args={
            "uri": os.getenv("MILVUS_URI", ""),
            "token": os.getenv("MILVUS_API_KEY", ""),
            "secure": os.getenv("MILVUS_URI", "").startswith("https"),
        },
    )

    return instance


async def get_qdrant_collection(
    library_embedding: str, library_uuid: UUID, documents: list[Document]
):
    instance = await Qdrant.afrom_documents(
        documents=documents,
        embedding=EMBEDDING_MAPPING[library_embedding](),
        collection_name=library_uuid.hex,
        prefer_grpc=True,
        url=os.getenv("QDRANT_URI", ""),
        api_key=os.getenv("QDRANT_API_KEY", ""),
    )

    return instance


async def get_weaviate_collection(
    library_embedding: str, library_uuid: UUID, documents: list[Document]
):
    instance = await Weaviate.afrom_documents(
        client=get_weaviate_client(),
        documents=documents,
        index_name=f"collection_{library_uuid.hex}",
        embedding=EMBEDDING_MAPPING[library_embedding](),
        by_text=False,
    )

    return instance


async def process_document(
    document_type: str,
    document_path: str,
    library_uuid: UUID,
    library_embedding: str,
    library_vectordb: str,
):
    loader = LOADER_MAPPING[document_type](document_path=document_path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )

    splitted_documents = splitter.split_documents(documents=loader.load())

    await VECTORDB_MAPPING[library_vectordb](
        library_embedding=library_embedding,
        library_uuid=library_uuid,
        documents=splitted_documents,
    )

    return True


EMBEDDING_MAPPING = {
    "cohere": get_cohere_embedding,
    "dashscope": get_dashscope_embedding,
}


VECTORDB_MAPPING = {
    "dashvector": get_dashvector_collection,
    "milvus": get_milvus_collection,
    "qdrant": get_qdrant_collection,
    "weaviate": get_weaviate_collection,
}


LOADER_MAPPING = {
    "pdf": get_pdf_loader,
    "web_page": get_web_page_loader,
}

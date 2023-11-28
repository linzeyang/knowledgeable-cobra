"""document_processor.py"""

import os
from uuid import UUID

from langchain.document_loaders import WebBaseLoader
from langchain.embeddings.cohere import CohereEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.milvus import Milvus
from langchain.vectorstores.qdrant import Qdrant
from langchain.vectorstores.weaviate import Weaviate

from app.data_connection.weaviate import get_client as get_weaviate_client


def get_web_page_loader(document_path: str):
    loader = WebBaseLoader(web_path=document_path)

    return loader


def get_cohere_embedding():
    return CohereEmbeddings(max_retries=5, request_timeout=20)


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
}


VECTORDB_MAPPING = {
    "milvus": get_milvus_collection,
    "qdrant": get_qdrant_collection,
    "weaviate": get_weaviate_collection,
}


LOADER_MAPPING = {
    "web_page": get_web_page_loader,
}

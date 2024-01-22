"""prompt_processor.py"""

import os
from typing import Callable
from uuid import UUID

from langchain_community.chat_models.cohere import ChatCohere
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.embeddings.cohere import CohereEmbeddings
from langchain_community.embeddings.dashscope import DashScopeEmbeddings
from langchain_community.vectorstores.dashvector import DashVector
from langchain_community.vectorstores.milvus import Milvus
from langchain_community.vectorstores.qdrant import Qdrant
from langchain_community.vectorstores.weaviate import Weaviate
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from app.chain import get_rag_chain
from app.data_connection.dashvector import get_client as get_dashvector_client
from app.data_connection.qdrant import get_client as get_qdrant_client
from app.data_connection.weaviate import get_client as get_weaviate_client


def get_prompt_processor(
    embedding: str, vectordb: str, collection: UUID, llm: str
) -> Callable:
    chain = build_chain(embedding, vectordb, collection, llm)

    return chain.ainvoke


def build_chain(embedding: str, vectordb: str, collection: UUID, llm: str):
    db_collection = VECTORDB_MAPPING[vectordb](
        embedding=EMBEDDING_MAPPING[embedding](), collection=collection
    )

    chat = CHAT_MAPPING[llm](temperature=0.1)

    return get_rag_chain(retriever=db_collection.as_retriever(), llm=chat)


def get_cohere_embedding():
    # return CohereEmbeddings(
    #     model="embed-multilingual-light-v3.0", max_retries=5, request_timeout=20
    # )
    return CohereEmbeddings(max_retries=5, request_timeout=20)


def get_dashscope_embedding():
    return DashScopeEmbeddings(model="text-embedding-v2", max_retries=5)


def get_dashvector_collection(embedding, collection: UUID):
    client = get_dashvector_client()

    instance = DashVector(
        # character must be in [a-zA-Z0-9] and symbols[_,-] and length must be in [3,32]
        collection=client.get(name=collection.hex),
        embedding=embedding,
        text_field="text",
    )

    return instance


def get_milvus_collection(embedding, collection: UUID):
    instance = Milvus(
        embedding_function=embedding,
        # The first character of a collection name must be an underscore or letter
        collection_name=f"_{collection.hex}",
        connection_args={
            "uri": os.getenv("MILVUS_URI", ""),
            "token": os.getenv("MILVUS_API_KEY", ""),
            "secure": os.getenv("MILVUS_URI", "").startswith("https"),
        },
    )

    return instance


def get_qdrant_collection(embedding, collection: UUID):
    client = get_qdrant_client()

    instance = Qdrant(
        client=client, collection_name=collection.hex, embeddings=embedding
    )

    return instance


def get_weaviate_collection(embedding, collection: UUID):
    client = get_weaviate_client()

    instance = Weaviate(
        client=client, index_name=f"collection_{collection.hex}", embedding=embedding
    )

    return instance


def get_cohere_chat(temperature: float):
    return ChatCohere(temperature=temperature)


def get_tongyi_chat(temperature: float):
    return ChatTongyi(model="qwen-max", model_kwargs={"temperature": temperature})


MESSAGE_MAPPING = {
    "ai": AIMessage,
    "human": HumanMessage,
    "system": SystemMessage,
}


def construct_chat_history(messages: list[dict[str, str]]) -> list[BaseMessage]:
    return [
        MESSAGE_MAPPING[message["type"]](content=message["content"])
        for message in messages
    ]


CHAT_MAPPING = {
    "cohere": get_cohere_chat,
    "dashscope": get_tongyi_chat,
}


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

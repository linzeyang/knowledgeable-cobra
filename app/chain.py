"""chain.py"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough


class DummyChain:
    def invoke(self, prompt: str) -> str:
        return f"Your prompt is {prompt}"

    async def ainvoke(self, prompt: str) -> str:
        return f"Your prompt is {prompt}"


def format_docs(docs) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


condense_q_system_prompt = """Given a chat history and the latest user question \
which might reference the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""


condense_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", condense_q_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)


qa_system_prompt = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
Use three sentences maximum and keep the answer concise.\

{context}"""


qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)


def get_rag_chain(retriever, llm):
    condense_q_chain = condense_q_prompt | llm | StrOutputParser()

    def condense_question(input: dict):
        if input.get("chat_history"):
            return condense_q_chain

        return input["question"]

    rag_chain = (
        RunnablePassthrough.assign(context=condense_question | retriever | format_docs)
        | qa_prompt
        | llm
    )

    return rag_chain

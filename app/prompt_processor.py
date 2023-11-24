"""prompt_processor.py"""

from typing import Callable
from uuid import UUID

from app.chain import DummyChain


def get_prompt_processor(dialogue_id: UUID) -> Callable:
    chain = build_chain()

    return chain.invoke


def build_chain():
    return DummyChain()

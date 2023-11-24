"""chain.py"""


class DummyChain:
    def invoke(self, prompt: str) -> str:
        return f"Your prompt is {prompt}"

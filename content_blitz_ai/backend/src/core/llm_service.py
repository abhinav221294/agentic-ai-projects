from dataclasses import dataclass
from typing import Any, Dict, Generator


@dataclass
class LLMResponse:
    content: str
    metadata: Dict[str, Any]


class LLMService:
    """
    Common wrapper for all LangChain chat models.

    Supported providers:
    - Claude
    - Gemini
    - OpenAI
    - Any LangChain ChatModel
    """

    @staticmethod
    def invoke(llm: Any, prompt: str) -> LLMResponse:
        """
        Invoke an LLM and return a standardized response.
        """

        response = llm.invoke(prompt)

        return LLMResponse(
            content=str(getattr(response, "content", "")).strip(),
            metadata=getattr(response, "response_metadata", {}),
        )

    @staticmethod
    def stream(llm: Any, prompt: str) -> Generator[str, None, LLMResponse]:
        """
        Stream text from an LLM.

        Yields:
            Individual text chunks.

        Returns:
            LLMResponse containing the full response and metadata.
        """

        full_response = ""
        metadata = {}

        for chunk in llm.stream(prompt):

            text = getattr(chunk, "content", "")

            if not text:
                continue

            full_response += text

            if hasattr(chunk, "response_metadata"):
                metadata = chunk.response_metadata

            yield text

        return LLMResponse(
            content=full_response.strip(),
            metadata=metadata,
        )
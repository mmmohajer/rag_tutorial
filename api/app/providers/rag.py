from openai import OpenAI

from app.rag.constants import EMBEDDING_DIMENSION
from app.settings import settings


class Rag:
    def __init__(
        self,
        embedding_model: str = "text-embedding-3-large",
        chat_model: str = "gpt-6-astra",
    ) -> None:
        self.embedding_model = embedding_model
        self.chat_model = chat_model
        self._client = OpenAI(api_key=settings.open_ai_api_key)

    def build_embedding(self, text: str) -> list[float]:
        cleaned = text.strip()
        if not cleaned:
            raise ValueError("text is empty")

        response = self._client.embeddings.create(
            model=self.embedding_model,
            input=cleaned,
            dimensions=EMBEDDING_DIMENSION,
        )
        embedding = response.data[0].embedding
        if len(embedding) != EMBEDDING_DIMENSION:
            raise ValueError(
                f"expected {EMBEDDING_DIMENSION} dimensions, got {len(embedding)}"
            )
        return embedding

    def generate_response(self, user_message: str, system_message: str) -> str:
        user_message = user_message.strip()
        system_message = system_message.strip()
        if not user_message:
            raise ValueError("user message is empty")
        if not system_message:
            raise ValueError("system message is empty")

        response = self._client.chat.completions.create(
            model=self.chat_model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("model returned an empty response")
        return content

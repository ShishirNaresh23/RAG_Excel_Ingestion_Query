from openai import AsyncOpenAI
from app.core.config import settings

class Embedder:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def embed(self, texts: list[str]) -> list[list[float]]:
        response = await self.client.embeddings.create(
            model=settings.embedding_model,
            input=texts
        )
        return [item.embedding for item in response.data]
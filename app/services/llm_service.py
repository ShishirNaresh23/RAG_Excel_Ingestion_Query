from openai import AsyncOpenAI
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate_answer(self, query: str, context: str) -> str:
        prompt = f"Context from Excel:\n{context}\n\nQuestion: {query}\n\nAnswer based on context:"
        response = await self.client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message.content
import uuid
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from app.core.config import settings
from app.models.domain import Chunk

class VectorStore:
    def __init__(self):
        self.client = AsyncQdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)

    def _collection_name(self, file_hash: str) -> str:
        return f"excel_rag_{file_hash[:16]}"

    async def ensure_collection(self, file_hash: str) -> bool:
        name = self._collection_name(file_hash)
        collections = await self.client.get_collections()
        if name in [c.name for c in collections.collections]:
            return False
        
        await self.client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=settings.embedding_dim, distance=Distance.COSINE)
        )
        return True

    async def upsert(self, file_hash: str, chunks: list[Chunk], embeddings: list[list[float]]):
        name = self._collection_name(file_hash)
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=emb,
                payload={"content": c.content, **c.payload, "chunk_type": c.chunk_type, "sheet_name": c.sheet_name}
            )
            for c, emb in zip(chunks, embeddings)
        ]
        await self.client.upsert(collection_name=name, points=points)

    async def search(self, file_hash: str, query_vector: list[float], top_k: int, filters: dict = None):
        name = self._collection_name(file_hash)
        must_conditions = []
        
        if filters.get("sheet_name"):
            must_conditions.append(FieldCondition(key="sheet_name", match=MatchValue(value=filters["sheet_name"])))
        if filters.get("chunk_type"):
            must_conditions.append(FieldCondition(key="chunk_type", match=MatchValue(value=filters["chunk_type"])))

        query_filter = Filter(must=must_conditions) if must_conditions else None
        
        results = await self.client.query_points(
            collection_name=name,
            query=query_vector,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True
        )
        return [{"content": p.payload["content"], "score": p.score, "chunk_type": p.payload["chunk_type"], "sheet_name": p.payload["sheet_name"]} for p in results.points]

    async def close(self):
        await self.client.close()
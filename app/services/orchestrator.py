import hashlib
import httpx
import logging
from app.services.parser import ExcelParser
from app.services.analyzer import SchemaAnalyzer
from app.services.chunker import SemanticChunker
from app.services.embedder import Embedder
from app.services.vector_store import VectorStore
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.parser = ExcelParser()
        self.analyzer = SchemaAnalyzer()
        self.chunker = SemanticChunker()
        self.embedder = Embedder()
        self.vector_store = VectorStore()
        self.llm = LLMService()

    async def process_and_query(self, file_url: str, query: str, top_k: int, sheet_filter: str = None, type_filter: str = None):
        # 1. Get File
        async with httpx.AsyncClient() as client:
            resp = await client.get(file_url)
            file_bytes = resp.content
        
        file_hash = hashlib.sha256(file_bytes).hexdigest()

        # 2. Parse
        metadata = await self.parser.parse_bytes(file_bytes)
        data = self.parser.extract_data(metadata, file_bytes)

        # 3. Analyze
        relationships = self.analyzer.detect_relationships(metadata, data)
        roles = {sheet: self.analyzer.detect_roles(meta, data[sheet], relationships) for sheet, meta in metadata.items()}

        # 4. Chunk
        chunks = self.chunker.build_chunks(metadata, data, roles, relationships)

        # 5. Store (Check if exists)
        is_new = await self.vector_store.ensure_collection(file_hash)
        if is_new:
            embeddings = await self.embedder.embed([c.content for c in chunks])
            await self.vector_store.upsert(file_hash, chunks, embeddings)

        # 6. Retrieve
        query_vec = (await self.embedder.embed([query]))[0]
        filters = {"sheet_name": sheet_filter, "chunk_type": type_filter}
        results = await self.vector_store.search(file_hash, query_vec, top_k, filters)

        # 7. Generate
        context = "\n\n".join([r["content"] for r in results])
        answer = await self.llm.generate_answer(query, context)

        await self.vector_store.close()

        return {
            "answer": answer,
            "collection_name": self.vector_store._collection_name(file_hash),
            "chunks_indexed": len(chunks),
            "matches": results[:5],
            "sheets": list(metadata.keys()),
            "relationships": relationships
        }
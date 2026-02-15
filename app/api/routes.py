from fastapi import APIRouter
from app.api.schemas import ExcelQueryRequest, ExcelQueryResponse, MatchResult, RelationshipInfo
from app.services.orchestrator import Orchestrator

router = APIRouter()

@router.post("/", response_model=ExcelQueryResponse)
async def query_excel(request: ExcelQueryRequest):
    orchestrator = Orchestrator()
    result = await orchestrator.process_and_query(
        file_url=request.excel_file,
        query=request.query,
        top_k=request.top_k,
        sheet_filter=request.sheet_filter,
        type_filter=request.chunk_type_filter
    )
    
    return ExcelQueryResponse(
        answer=result["answer"],
        collection_name=result["collection_name"],
        chunks_indexed=result["chunks_indexed"],
        top_matches=[MatchResult(**m) for m in result["matches"]],
        sheets_parsed=result["sheets"],
        relationships_detected=[RelationshipInfo(**r.dict()) for r in result["relationships"]]
    )
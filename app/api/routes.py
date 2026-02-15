from fastapi import APIRouter,UploadFile, File, Form
from app.api.schemas import ExcelQueryRequest, ExcelQueryResponse, MatchResult, RelationshipInfo
from app.services.orchestrator import Orchestrator
import logging
from fastapi import HTTPException

router = APIRouter()

@router.post("/upload", response_model=ExcelQueryResponse)
async def upload_and_query(
    excel_file: UploadFile = File(..., description="Excel file to upload"),
    query: str = Form(..., description="Natural language question"),
    top_k: int = Form(default=10),
    sheet_filter: str = Form(default=None)
):
    try:
        orchestrator = Orchestrator()
        
        # Read file bytes
        file_bytes = await excel_file.read()
        
        # Process
        result = await orchestrator.process_query_from_bytes(
            file_bytes=file_bytes,
            query=query,
            top_k=top_k,
            sheet_filter=sheet_filter
        )
        
        return ExcelQueryResponse(
            answer=result["answer"],
            collection_name=result["collection_name"],
            chunks_indexed=result["chunks_indexed"],
            top_matches=[MatchResult(**m) for m in result["matches"]],
            sheets_parsed=result["sheets"],
            relationships_detected=[RelationshipInfo(**r.dict()) for r in result["relationships"]]
        )
    
    except ValueError as e:
        # Catch our custom validation errors (like wrong file format)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catch unexpected errors
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

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
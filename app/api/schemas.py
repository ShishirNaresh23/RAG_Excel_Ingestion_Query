from pydantic import BaseModel, Field
from typing import List, Optional

class ExcelQueryRequest(BaseModel):
    excel_file: str = Field(..., description="URL or path to the Excel file")
    query: str = Field(..., description="Natural language question")
    top_k: int = Field(default=10, ge=1, le=50)
    sheet_filter: Optional[str] = None
    chunk_type_filter: Optional[str] = None

class MatchResult(BaseModel):
    content: str
    score: float
    chunk_type: str
    sheet_name: str

class RelationshipInfo(BaseModel):
    type: str
    from_col: str = Field(alias="from")
    to_col: str = Field(alias="to")
    overlap: str

    class Config:
        populate_by_name = True

class ExcelQueryResponse(BaseModel):
    answer: str
    collection_name: str
    chunks_indexed: int
    top_matches: List[MatchResult]
    sheets_parsed: List[str]
    relationships_detected: List[RelationshipInfo]
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ColumnMetadata(BaseModel):
    name: str
    index: int
    data_type: str
    sample_values: List[Any]
    non_empty_count: int

class SheetMetadata(BaseModel):
    sheet_name: str
    header_row: int
    columns: List[ColumnMetadata]
    total_rows: int

class ColumnRole(BaseModel):
    role: str  # primary_key, foreign_key, value, metadata
    data_type: str
    unique_count: int
    total_count: int
    foreign_key_to: Optional[str] = None

class Relationship(BaseModel):
    type: str
    sheet_a: str
    column_a: str
    sheet_b: str
    column_b: str
    overlapping_values: List[str]
    overlap_ratio: float

class Chunk(BaseModel):
    chunk_id: str
    chunk_type: str
    sheet_name: str
    content: str
    payload: Dict[str, Any]
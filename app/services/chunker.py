from typing import Dict, List
from app.models.domain import SheetMetadata, ColumnRole, Relationship, Chunk
from app.utils.text_helpers import expand_abbreviation, extract_keywords

class SemanticChunker:
    def build_chunks(self, metadata: Dict[str, SheetMetadata], data: Dict, roles: Dict[str, Dict[str, ColumnRole]], relationships: List[Relationship]) -> List[Chunk]:
        chunks = []
        
        for sheet_name, meta in metadata.items():
            sheet_roles = roles[sheet_name]
            sheet_data = data[sheet_name]
            sheet_rels = [r for r in relationships if r.sheet_a == sheet_name or r.sheet_b == sheet_name]
            
            # 1. Sheet Summary
            chunks.append(self._build_sheet_summary(meta, sheet_roles, sheet_rels))
            
            # 2. Row Chunks
            for row_idx in range(meta.total_rows):
                row_data = {h: sheet_data[h][row_idx] for h in [c.name for c in meta.columns] if row_idx < len(sheet_data.get(h, []))}
                if any(v is not None for v in row_data.values()):
                    chunks.append(self._build_row_chunk(sheet_name, row_idx + 1, row_data, sheet_roles, sheet_rels))
            
            # 3. Column Profiles
            for col in meta.columns:
                col_chunk = self._build_column_profile(sheet_name, col.name, sheet_data.get(col.name, []), sheet_roles.get(col.name), sheet_rels)
                if col_chunk: chunks.append(col_chunk)
        
        # 4. Relationship Chunks
        for rel in relationships:
            chunks.append(self._build_relationship_chunk(rel))
            
        return chunks

    def _build_row_chunk(self, sheet_name, row_idx, row_data, roles, rels) -> Chunk:
        # Simplified logic from original code
        pk_col = next((c for c, r in roles.items() if r.role == "primary_key"), None)
        pk_val = row_data.get(pk_col)
        
        summary = f"Record in {sheet_name} (Row {row_idx})"
        details = []
        
        for col, val in row_data.items():
            if val is not None:
                role = roles.get(col)
                ctx = f"{col} (identifier)" if role and role.role == "primary_key" else col
                details.append(f"{ctx}: {val}")
                
        content = f"{summary}\n\nDetails:\n" + "\n".join(f"- {d}" for d in details)
        keywords = extract_keywords(row_data, roles)
        
        return Chunk(
            chunk_id=f"row_{sheet_name}_{row_idx}",
            chunk_type="row_semantic",
            sheet_name=sheet_name,
            content=content,
            payload={"row_index": row_idx, "keywords": keywords, "primary_key": pk_val}
        )

    def _build_sheet_summary(self, meta, roles, rels) -> Chunk:
        cols = [c.name for c in meta.columns]
        content = f"Sheet '{meta.sheet_name}' has {meta.total_rows} rows. Columns: {', '.join(cols)}."
        return Chunk(chunk_id=f"sheet_{meta.sheet_name}", chunk_type="sheet_summary", sheet_name=meta.sheet_name, content=content, payload={})

    def _build_column_profile(self, sheet_name, col_name, data, role, rels) -> Chunk:
        non_null = [v for v in data if v is not None]
        if not non_null: return None
        
        content = f"Column '{col_name}' in {sheet_name}. Contains {len(non_null)} values. Sample: {non_null[:3]}."
        return Chunk(chunk_id=f"col_{sheet_name}_{col_name}", chunk_type="column_profile", sheet_name=sheet_name, content=content, payload={})

    def _build_relationship_chunk(self, rel) -> Chunk:
        content = f"Link found: {rel.sheet_a}.{rel.column_a} <-> {rel.sheet_b}.{rel.column_b}."
        return Chunk(chunk_id=f"rel_{rel.sheet_a}_{rel.column_a}", chunk_type="relationship", sheet_name=rel.sheet_a, content=content, payload={})
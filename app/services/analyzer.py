from typing import Dict, List
from app.models.domain import SheetMetadata, ColumnRole, Relationship

class SchemaAnalyzer:
    def detect_relationships(self, metadata: Dict[str, SheetMetadata], data: Dict[str, Dict]) -> List[Relationship]:
        relationships = []
        sheet_names = list(metadata.keys())
        
        for i, sheet_a in enumerate(sheet_names):
            for sheet_b in sheet_names[i + 1:]:
                rels = self._find_links(metadata[sheet_a], metadata[sheet_b], data[sheet_a], data[sheet_b])
                relationships.extend(rels)
        return relationships

    def detect_roles(self, metadata: SheetMetadata, data: Dict[str, List], relationships: List[Relationship]) -> Dict[str, ColumnRole]:
        roles = {}
        headers = [c.name for c in metadata.columns]
        
        for header in headers:
            col_data = data.get(header, [])
            vals = [str(v) for v in col_data if v is not None]
            unique_count = len(set(vals))
            total_count = len(vals)
            
            role_type = "value"
            fk_target = None
            header_lower = header.lower().strip()
            
            # Basic ID detection
            is_id_col = any(kw in header_lower for kw in ["_id", " id", "identifier", "key", "code"]) or header_lower.endswith("id")
            if is_id_col:
                role_type = "primary_key" if total_count > 0 and unique_count == total_count else "foreign_key"
            
            # Relationship-based refinement
            for rel in relationships:
                if rel.sheet_a == metadata.sheet_name and rel.column_a == header:
                    if role_type != "primary_key": role_type = "foreign_key"
                    fk_target = f"{rel.sheet_b}.{rel.column_b}"
                elif rel.sheet_b == metadata.sheet_name and rel.column_b == header:
                    if role_type != "primary_key": role_type = "foreign_key"
                    fk_target = f"{rel.sheet_a}.{rel.column_a}"

            # Metadata detection
            if any(kw in header_lower for kw in ["updated", "created", "modified", "date", "timestamp"]):
                if role_type == "value": role_type = "metadata"

            roles[header] = ColumnRole(
                role=role_type, 
                data_type="string", # Simplified for brevity, should match metadata
                unique_count=unique_count,
                total_count=total_count,
                foreign_key_to=fk_target
            )
        return roles

    def _find_links(self, meta_a, meta_b, data_a, data_b) -> List[Relationship]:
        links = []
        cols_a = {c.name.lower(): c.name for c in meta_a.columns}
        cols_b = {c.name.lower(): c.name for c in meta_b.columns}
        
        shared = set(cols_a.keys()) & set(cols_b.keys())
        
        for col_lower in shared:
            col_a, col_b = cols_a[col_lower], cols_b[col_lower]
            vals_a = set(str(v) for v in data_a.get(col_a, []) if v is not None)
            vals_b = set(str(v) for v in data_b.get(col_b, []) if v is not None)
            
            overlap = vals_a & vals_b
            if overlap:
                links.append(Relationship(
                    type="shared_key", sheet_a=meta_a.sheet_name, column_a=col_a,
                    sheet_b=meta_b.sheet_name, column_b=col_b,
                    overlapping_values=list(overlap)[:10],
                    overlap_ratio=len(overlap) / max(len(vals_a), len(vals_b), 1)
                ))
        return links
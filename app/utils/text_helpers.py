import re

def expand_abbreviation(text: str) -> str:
    """Expand camelCase and PascalCase into readable form."""
    if not isinstance(text, str):
        return str(text)
    # Insert space before capital letters
    expanded = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    expanded = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", expanded)
    return expanded

def extract_keywords(row_data: dict, column_roles: dict) -> list[str]:
    """Extract searchable keywords from a row."""
    keywords: list[str] = []
    for col_name, value in row_data.items():
        if value is None:
            continue
        val_str = str(value).strip()
        keywords.append(val_str)
        
        # Add expanded forms
        expanded = expand_abbreviation(val_str)
        if expanded.lower() != val_str.lower():
            keywords.extend(w for w in expanded.split() if len(w) > 1)
            
        # Add column name context
        keywords.append(col_name.lower().replace("_", " "))
        
    return sorted(set(kw for kw in keywords if len(kw) > 1))[:25]
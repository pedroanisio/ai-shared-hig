# API Export Formats - Complete Guide

## Overview

The Universal Corpus API provides **5 export formats** optimized for different use cases. All formats are accessible via REST API endpoints with optional filtering.

## Available Export Formats

| Endpoint | Format | Size | Best For |
|----------|--------|------|----------|
| `GET /export/jsonl` | Full JSONL | 1,042 KB | API storage, complete data |
| `GET /export/compact` | Compact JSONL | 732 KB (-30%) | AI/LLM prompts, token optimization |
| `GET /export/csv-compact` | CSV Compact | 832 KB (-20%) | Data analysis, spreadsheets + code |
| `GET /export/csv-simple` | CSV Simple | 90 KB (-91%) | Human review, quick browsing ⭐ |
| `GET /export/csv` | CSV Full | 1,000+ KB | Legacy format, verbose |

---

## 1. Full JSONL Format

**Endpoint:** `GET /export/jsonl`

### Description
Complete pattern data in JSONL format (one JSON object per line). This is the canonical format for API storage and complete data preservation.

### Use Cases
- Long-term storage
- API responses
- Complete data backup
- When token efficiency doesn't matter

### Example Request
```bash
curl http://localhost:8000/export/jsonl -o patterns.jsonl
```

### With Filtering
```bash
# Export only stable concepts
curl "http://localhost:8000/export/jsonl?category=concept&status=stable" \
  -o concepts_stable.jsonl
```

### Response Format
```jsonl
{"id":"C1","version":"1.1","metadata":{"name":"Graph Structure",...},...}
{"id":"C2","version":"1.1","metadata":{"name":"Document/Artifact",...},...}
```

---

## 2. Compact JSONL Format ⭐ For AI/LLMs

**Endpoint:** `GET /export/compact`

### Description
Token-efficient JSONL format with **30% reduction** in tokens while preserving all semantic information. Optimized for AI/LLM interactions.

### Use Cases
- Sharing with AI assistants (ChatGPT, Claude, etc.)
- Embedding in prompts
- RAG systems
- API token cost optimization
- When context window is limited

### Example Request
```bash
curl http://localhost:8000/export/compact -o patterns_compact.jsonl
```

### Response Format
```jsonl
{"id":"C1","v":"1.1","name":"Graph Structure","cat":"concept","def":"$G = (N, E, \\lambda_n, \\lambda_e)$","comps":[{"n":"λ_n","t":"N → Label_n",...}],...}
```

### Token Savings
- Full format: ~260,509 tokens
- Compact format: ~182,933 tokens
- **Savings: ~77,576 tokens (29.8%)**

### Key Features
- Short keys: `v` (version), `cat` (category), `cx` (complexity)
- Inline format: latex assumed by default
- Flattened structure: metadata at top level
- Lossless: 100% data preservation

---

## 3. CSV Compact Format

**Endpoint:** `GET /export/csv-compact`

### Description
Columnar CSV format with both human-readable summaries and programmatic access via `*_detail` columns. Best of both worlds.

### Use Cases
- Data analysis with pandas/R
- Spreadsheet viewing + coding
- Database imports
- BI tools
- Combined manual + programmatic workflows

### Example Request
```bash
curl http://localhost:8000/export/csv-compact -o patterns_compact.csv
```

### Columns Structure

**Core Columns:**
```
id, version, name, category, status, complexity, domains, last_updated
```

**Summary Columns:**
```
components          → "λ_n:N → Label_n|λ_e:E → Label_e"
properties          → "P.C1.1:Connectivity|P.C1.2:Cycle Detection"
operations          → "Traverse|Path|Neighbors"
manifestations      → "Knowledge graphs|Social networks"
```

**Detail Columns (compact JSON):**
```
components_detail   → [{"n":"λ_n","t":"N → Label","d":"..."}]
properties_detail   → [{"id":"P.C1.1","n":"Connectivity","spec":"..."}]
operations_detail   → [{"n":"Traverse","sig":"...","def":"..."}]
```

### Python Usage
```python
import pandas as pd

# Load CSV
df = pd.read_csv('patterns_compact.csv')

# Quick analysis
print(df.groupby('category').size())
print(df[df['complexity'] == 'high']['name'])

# Access detail columns
import json
for _, row in df.iterrows():
    comps = json.loads(row['components_detail'])
    for comp in comps:
        print(f"{comp['n']}: {comp['t']}")
```

---

## 4. CSV Simple Format ⭐ For Humans

**Endpoint:** `GET /export/csv-simple`

### Description
Ultra-lightweight CSV format with **91% reduction** from full format. Human-readable only, perfect for non-technical stakeholders.

### Use Cases
- Stakeholder reviews
- Executive summaries
- Quick pattern browsing
- Pattern catalogs
- Email sharing
- BI dashboards

### Example Request
```bash
curl http://localhost:8000/export/csv-simple -o patterns.csv
```

### Columns Structure
```
id, version, name, category, status, complexity, domains, last_updated,
tuple_notation, definition_desc, num_components, num_properties,
num_operations, num_type_definitions, num_manifestations, component_names,
property_names, operation_names, requires, uses, specializes,
specialized_by, manifestation_names
```

### Sample Data
```csv
id,version,name,category,status,complexity,num_components,num_properties,component_names
C1,1.1,Graph Structure,concept,stable,medium,2,2,λ_n|λ_e
P64,1.0,Generative UI,pattern,stable,high,5,3,T_lib|ctx|gen|render|stream
```

### Excel/Google Sheets Usage
1. Open CSV in Excel/Google Sheets
2. Use Auto-filter to sort/filter
3. Create pivot tables for statistics
4. Split pipe-separated columns: Data → Text to Columns

---

## 5. CSV Full Format (Legacy)

**Endpoint:** `GET /export/csv`

### Description
Original verbose CSV format with all nested data flattened into string columns. Maintained for backward compatibility.

### Use Cases
- Legacy systems
- When maximum verbosity is needed
- Historical compatibility

### Example Request
```bash
curl http://localhost:8000/export/csv -o patterns_full.csv
```

---

## Filtering Options

All export endpoints support the same filtering parameters:

### Available Filters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `category` | enum | Filter by category | `concept`, `pattern`, `flow` |
| `status` | enum | Filter by status | `stable`, `draft`, `deprecated` |

### Examples

```bash
# Export only concepts
curl "http://localhost:8000/export/compact?category=concept" \
  -o concepts.jsonl

# Export only stable patterns
curl "http://localhost:8000/export/csv-simple?status=stable" \
  -o stable_patterns.csv

# Export stable concepts (combine filters)
curl "http://localhost:8000/export/csv-simple?category=concept&status=stable" \
  -o stable_concepts.csv

# Export patterns only
curl "http://localhost:8000/export/compact?category=pattern" \
  -o patterns_only.jsonl
```

---

## Import Endpoints

### Import JSONL (Full)
```bash
curl -X POST http://localhost:8000/import/jsonl \
  -F "file=@patterns.jsonl" \
  -F "skip_existing=true"
```

### Import Compact JSONL
```bash
curl -X POST http://localhost:8000/import/compact \
  -F "file=@patterns_compact.jsonl"
```

### Import CSV Compact
```bash
curl -X POST http://localhost:8000/import/csv-compact \
  -F "file=@patterns_compact.csv"
```

---

## Format Comparison Matrix

| Feature | Full JSONL | Compact JSONL | CSV Compact | CSV Simple |
|---------|-----------|---------------|-------------|------------|
| **Size (176 patterns)** | 1,042 KB | 732 KB | 832 KB | 90 KB |
| **Token Count** | ~260K | ~183K | ~208K | ~23K |
| **Human Readable** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Programmatic** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Spreadsheet** | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Round-trip** | ✅ | ✅ | ✅ | ❌ |
| **AI/LLM Optimized** | ❌ | ✅ | ❌ | ❌ |
| **Data Complete** | ✅ | ✅ | ✅ | ⚠️ Summary |

---

## Use Case Decision Tree

```
What's your primary use case?
│
├─ Sharing with AI/LLMs?
│  └─→ Use: /export/compact (Compact JSONL)
│
├─ Data analysis with code?
│  └─→ Use: /export/csv-compact (CSV Compact)
│
├─ Stakeholder review / Quick browsing?
│  └─→ Use: /export/csv-simple (CSV Simple) ⭐
│
├─ Long-term storage / API?
│  └─→ Use: /export/jsonl (Full JSONL)
│
└─ Need XML for schema validation?
   └─→ Use: GET /patterns/{id}/xml
```

---

## Response Headers

All export endpoints return appropriate headers:

```http
Content-Type: text/csv | application/x-ndjson
Content-Disposition: attachment; filename=patterns_*.csv
```

---

## Rate Limits & Performance

- No rate limits on export endpoints
- Exports are streamed for memory efficiency
- Large datasets (10,000+ patterns) are handled efficiently
- Filtering at database level for optimal performance

---

## Error Handling

### Common Errors

**Invalid Category:**
```json
{
  "detail": "value is not a valid enumeration member"
}
```

**Invalid Status:**
```json
{
  "detail": "value is not a valid enumeration member"
}
```

**Server Error:**
```json
{
  "detail": "Export failed: <error message>"
}
```

---

## Complete API Documentation

For interactive API documentation with request/response examples:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Examples by Language

### Python

```python
import requests

# Export compact JSONL for AI
response = requests.get('http://localhost:8000/export/compact')
with open('patterns_compact.jsonl', 'wb') as f:
    f.write(response.content)

# Export CSV simple for humans
response = requests.get('http://localhost:8000/export/csv-simple')
with open('patterns_simple.csv', 'wb') as f:
    f.write(response.content)

# Export with filtering
response = requests.get(
    'http://localhost:8000/export/csv-simple',
    params={'category': 'concept', 'status': 'stable'}
)
```

### cURL

```bash
# Basic export
curl http://localhost:8000/export/compact -o patterns.jsonl

# With query parameters
curl "http://localhost:8000/export/csv-simple?category=concept" \
  -o concepts.csv

# Save with timestamp
curl http://localhost:8000/export/csv-simple \
  -o "patterns_$(date +%Y%m%d).csv"
```

### JavaScript

```javascript
// Fetch compact format
fetch('http://localhost:8000/export/compact')
  .then(response => response.blob())
  .then(blob => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'patterns_compact.jsonl';
    a.click();
  });

// Fetch CSV simple for display
fetch('http://localhost:8000/export/csv-simple')
  .then(response => response.text())
  .then(csv => {
    // Parse CSV or load into table
    console.log(csv);
  });
```

---

## Summary

✅ **5 export formats** available via REST API  
✅ **Filtering support** for all endpoints  
✅ **Streaming responses** for memory efficiency  
✅ **Token optimization** (up to 91% reduction)  
✅ **Complete documentation** at `/docs`  

Choose the right format for your use case and start exporting!

---

**Version:** 1.0  
**Last Updated:** 2025-11-23  
**API Version:** 1.0.0


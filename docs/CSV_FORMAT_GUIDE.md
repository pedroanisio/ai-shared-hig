# CSV Compact Format Guide

## Overview

The **CSV Compact Format** provides a columnar (spreadsheet-friendly) representation of Universal Corpus patterns. It's perfect for:

- 📊 **Spreadsheet viewing**: Excel, Google Sheets, LibreOffice
- 📈 **Data analysis**: pandas, R, SQL imports
- 🔍 **Quick browsing**: Sort, filter, search in familiar tools
- 👥 **Stakeholder reviews**: Non-technical audience accessibility

## Format Variants

### 1. CSV Compact (Full)

**Size:** ~832KB for 176 patterns  
**Use case:** Complete data with programmatic access  
**Best for:** Data analysis, full import/export

**Columns:**
```
id, version, name, category, status, complexity, domains, last_updated,
tuple_notation, definition_desc, components, properties, operations,
type_definitions, manifestations, requires, uses, specializes, 
specialized_by, components_detail, properties_detail, operations_detail,
type_definitions_detail, manifestations_detail
```

**Key features:**
- **Summary columns**: Pipe-separated names for quick scanning
- **Detail columns**: Full compact JSON for programmatic access
- **Round-trip capable**: Can reconstruct full Pattern objects

### 2. CSV Simple

**Size:** ~90KB for 176 patterns (91% smaller!)  
**Use case:** Human-readable summaries  
**Best for:** Quick reviews, stakeholder presentations, BI tools

**Columns:**
```
id, version, name, category, status, complexity, domains, last_updated,
tuple_notation, definition_desc, num_components, num_properties,
num_operations, num_type_definitions, num_manifestations, component_names,
property_names, operation_names, requires, uses, specializes,
specialized_by, manifestation_names
```

**Key features:**
- **No detail columns**: Clean, simple view
- **Count columns**: Quick metrics (num_components, num_properties, etc.)
- **Name lists**: Pipe-separated for easy reading

## Sample Data

### CSV Simple Format (recommended for viewing)

```csv
id,version,name,category,status,complexity,domains,last_updated,tuple_notation,definition_desc,num_components,num_properties,num_operations
C1,1.1,Graph Structure,concept,stable,medium,Data Structures|Graph Theory,2025-11-23,"$G = (N, E, \lambda_n, \lambda_e)$",A graph structure represents entities...,2,2,3
C2,1.1,Document/Artifact,pattern,stable,medium,Data Structures|Formal Methods,2025-11-23,"$doc = (state, process, visualize, interact)$",Documents and artifacts process input...,4,4,3
P64,1.0,Generative UI,pattern,stable,high,Generative AI|User Interface,2025-11-23,"$G = (T_lib, ctx, gen, render, stream)$",AI-generated interface components...,5,3,4
```

### CSV Compact Format (programmatic access)

```csv
id,version,name,components,components_detail
C1,1.1,Graph Structure,λ_n:N → Label_n|λ_e:E → Label_e,"[{""n"":""λ_n"",""t"":""N → Label_n"",""d"":""node labeling function""},{""n"":""λ_e"",""t"":""E → Label_e"",""d"":""edge labeling function""}]"
```

## Usage

### API Endpoints

#### Export CSV Compact

```bash
# Full CSV compact (with detail columns)
curl http://localhost:8000/export/csv-compact -o patterns_compact.csv

# Simplified CSV (human-readable)
curl http://localhost:8000/export/csv-simple -o patterns_simple.csv

# Filter by category
curl "http://localhost:8000/export/csv-simple?category=concept" \
  -o concepts.csv
```

#### Import CSV Compact

```bash
# Import patterns from CSV compact format
curl -X POST http://localhost:8000/import/csv-compact \
  -F "file=@patterns_compact.csv"
```

### CLI Tool

```bash
# Convert JSONL to CSV compact
python -m universal_corpus.cli.compact_converter to-csv \
  final_corpus.jsonl patterns_compact.csv

# Convert to simplified CSV
python -m universal_corpus.cli.compact_converter to-csv --simple \
  final_corpus.jsonl patterns_simple.csv
```

### Python API

```python
from universal_corpus.csv_compact import (
    patterns_to_csv,
    patterns_to_csv_simple,
    csv_to_patterns
)

# Export to CSV compact
csv_content = patterns_to_csv(patterns)
with open('patterns_compact.csv', 'w') as f:
    f.write(csv_content)

# Export to CSV simple
csv_simple = patterns_to_csv_simple(patterns)
with open('patterns_simple.csv', 'w') as f:
    f.write(csv_simple)

# Import from CSV compact
with open('patterns_compact.csv', 'r') as f:
    patterns = csv_to_patterns(f.read())
```

## Column Descriptions

### Core Columns (all formats)

| Column | Description | Example |
|--------|-------------|---------|
| `id` | Pattern identifier | `C1`, `P64`, `F1` |
| `version` | Pattern version | `1.1`, `2.0` |
| `name` | Human-readable name | `Graph Structure` |
| `category` | Pattern category | `concept`, `pattern`, `flow` |
| `status` | Development status | `stable`, `draft`, `deprecated` |
| `complexity` | Complexity level | `low`, `medium`, `high` |
| `domains` | Applicable domains | `Data Structures\|Graph Theory` |
| `last_updated` | Last update date | `2025-11-23` |
| `tuple_notation` | Formal definition | `$G = (N, E, \lambda_n, \lambda_e)$` |
| `definition_desc` | Description text | `A graph structure represents...` |

### Summary Columns (CSV Compact)

| Column | Description | Format |
|--------|-------------|--------|
| `components` | Component names:types | `λ_n:N → Label_n\|λ_e:E → Label_e` |
| `properties` | Property IDs:names | `P.C1.1:Connectivity\|P.C1.2:Cycle Detection` |
| `operations` | Operation names | `Traverse\|Path\|Neighbors` |
| `manifestations` | Manifestation names | `Knowledge graphs\|Social networks` |

### Count Columns (CSV Simple only)

| Column | Description | Example |
|--------|-------------|---------|
| `num_components` | Number of components | `4` |
| `num_properties` | Number of properties | `3` |
| `num_operations` | Number of operations | `5` |
| `num_type_definitions` | Number of type defs | `2` |
| `num_manifestations` | Number of manifestations | `7` |

### Detail Columns (CSV Compact only)

| Column | Description | Format |
|--------|-------------|--------|
| `components_detail` | Full component data | Compact JSON array |
| `properties_detail` | Full property data | Compact JSON array |
| `operations_detail` | Full operation data | Compact JSON array |
| `type_definitions_detail` | Full type def data | Compact JSON array |
| `manifestations_detail` | Full manifestation data | Compact JSON array |

### Dependency Columns (all formats)

| Column | Description | Format |
|--------|-------------|--------|
| `requires` | Required patterns | `C1\|C2\|P1` |
| `uses` | Used patterns | `P10\|P15` |
| `specializes` | Parent patterns | `P.Base` |
| `specialized_by` | Child patterns | `P.Derived1\|P.Derived2` |

## Use Cases

### 1. Spreadsheet Analysis

Open `patterns_simple.csv` in Excel/Google Sheets:

```excel
=COUNTIF(D:D,"concept")        # Count concepts
=AVERAGE(K:K)                  # Average num_components
=FILTER(A:J,E:E="stable")      # Filter stable patterns
```

### 2. Data Analysis (pandas)

```python
import pandas as pd

# Load CSV
df = pd.read_csv('patterns_simple.csv')

# Analysis
print(df.groupby('category').size())
print(df[df['complexity'] == 'high']['name'])
print(df['num_operations'].describe())

# Filter
ai_patterns = df[df['domains'].str.contains('AI', na=False)]
```

### 3. SQL Import

```sql
-- Import to SQLite
.mode csv
.import patterns_simple.csv patterns

-- Query
SELECT category, COUNT(*) 
FROM patterns 
GROUP BY category;

SELECT name, tuple_notation 
FROM patterns 
WHERE complexity = 'high';
```

### 4. Stakeholder Review

Share `patterns_simple.csv` with non-technical stakeholders:
- Sort by complexity to see challenging patterns
- Filter by domains to focus on specific areas
- Count columns show pattern richness at a glance

### 5. Pattern Catalog

Use CSV as a lightweight catalog:
- Quick search by name
- Filter by category/status
- View manifestations to see real-world examples

## Format Comparison

| Metric | Full JSONL | Compact JSONL | CSV Compact | CSV Simple |
|--------|------------|---------------|-------------|------------|
| **Size** | 1,042 KB | 732 KB | 832 KB | 90 KB |
| **Tokens** | ~260K | ~183K | ~208K | ~23K |
| **Human-readable** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Programmatic** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Spreadsheet** | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Data complete** | ✅ | ✅ | ✅ | ⚠️ (summary only) |
| **Best for** | API | AI/LLM | Analysis | Humans |

## Best Practices

### When to Use CSV Compact

✅ **Use CSV Compact for:**
- Data analysis with pandas/R
- Importing to databases
- Programmatic processing
- Full round-trip conversions

### When to Use CSV Simple

✅ **Use CSV Simple for:**
- Stakeholder reviews
- Quick pattern browsing
- Executive summaries
- BI tool imports
- Pattern catalogs

### When to Use JSONL Compact

✅ **Use JSONL Compact for:**
- AI/LLM interactions
- API token optimization
- Prompt embeddings
- RAG systems

## Tips for Spreadsheets

### Excel Tips

1. **Freeze headers**: View > Freeze Panes > Freeze Top Row
2. **Auto-filter**: Data > Filter
3. **Split pipe-separated**: Data > Text to Columns (delimiter: `|`)
4. **Conditional formatting**: Highlight patterns by status/complexity

### Google Sheets Tips

1. **Filter views**: Data > Filter views > Create new filter view
2. **Split columns**: `=SPLIT(A2, "|")` for pipe-separated values
3. **Count formula**: `=COUNTIF(D:D, "concept")`
4. **Conditional color**: Format > Conditional formatting

## Migration Guide

### From Full JSONL

```bash
# Step 1: Convert to CSV simple for stakeholders
python -m universal_corpus.cli.compact_converter to-csv --simple \
  final_corpus.jsonl patterns_simple.csv

# Step 2: Share with team
# Open patterns_simple.csv in Google Sheets

# Step 3: If programmatic access needed, use CSV compact
python -m universal_corpus.cli.compact_converter to-csv \
  final_corpus.jsonl patterns_compact.csv
```

### Import to Database

```python
import pandas as pd
from sqlalchemy import create_engine

# Load CSV
df = pd.read_csv('patterns_simple.csv')

# Import to database
engine = create_engine('postgresql://...')
df.to_sql('patterns', engine, if_exists='replace', index=False)
```

## Technical Details

### Encoding

- **CSV encoding**: UTF-8
- **Line endings**: LF (\n)
- **Quoting**: Minimal (only when necessary)
- **Delimiter**: Comma (,)
- **Array separator**: Pipe (|)

### Detail Column Format

Detail columns contain compact JSON arrays:

```json
[
  {"n": "component1", "t": "Type1", "d": "description"},
  {"n": "component2", "t": "Type2", "d": "description"}
]
```

### Round-Trip Conversion

CSV Compact → Pattern Objects:
1. Parse CSV rows
2. Extract `*_detail` columns
3. Parse compact JSON
4. Reconstruct full Pattern objects
5. Validate with Pydantic

## Examples

### Example 1: Pattern Overview

```bash
# Export simple CSV
curl http://localhost:8000/export/csv-simple -o overview.csv

# Open in Excel and:
# - Sort by complexity (descending)
# - Filter to only "stable" patterns
# - Count patterns by category
```

### Example 2: Data Analysis

```python
import pandas as pd

df = pd.read_csv('patterns_simple.csv')

# Most complex patterns
complex = df[df['complexity'] == 'high'].sort_values('num_operations', ascending=False)
print(complex[['id', 'name', 'num_operations']].head(10))

# Patterns by domain
domains_exploded = df['domains'].str.split('|', expand=True).stack()
print(domains_exploded.value_counts())
```

### Example 3: Pattern Dependencies

```python
import pandas as pd
import networkx as nx

df = pd.read_csv('patterns_simple.csv')

# Build dependency graph
G = nx.DiGraph()
for _, row in df.iterrows():
    G.add_node(row['id'])
    if pd.notna(row['requires']):
        for dep in row['requires'].split('|'):
            G.add_edge(row['id'], dep)

# Find most depended-on patterns
centrality = nx.in_degree_centrality(G)
print(sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10])
```

## Support

For issues or questions:
- Check API documentation at `/docs`
- Review examples in this guide
- Validate CSV format before import

---

**Version:** 1.0  
**Last Updated:** 2025-11-23  
**Compatibility:** Universal Corpus Pattern API v1.0.0




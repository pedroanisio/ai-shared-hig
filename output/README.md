# Universal Corpus - Machine-Readable (M2M) Output

**Generated:** 2025-11-22  
**Version:** 1.1  
**Format:** YAML + XML

---

## 📂 Directory Structure

```
output/
├── README.md                          # This file
├── universal_corpus_complete.yaml     # All patterns in single YAML file
├── universal_corpus_complete.xml      # All patterns in single XML file
└── m2m/
    ├── schema/
    │   ├── pattern_schema.yaml        # YAML schema definition
    │   └── pattern.xsd                # XML Schema (XSD)
    ├── yaml/                          # Individual YAML files
    │   ├── C1_Graph_Structure.yaml    # 5 concepts (C1-C5)
    │   ├── F1.1_1_Capture_Flow.yaml   # 17 flows (F1.1-F6)
    │   └── P1_Direct_Manipulation_Canvas.yaml  # 63 patterns (P1-P63)
    └── xml/                           # Individual XML files
        ├── C1_Graph_Structure.xml
        ├── F1.1_1_Capture_Flow.xml
        └── P1_Direct_Manipulation_Canvas.xml
```

---

## 📊 Content Summary

### Complete Coverage
- **Core Concepts (C):** 5 files (C1-C5)
- **Flows (F):** 17 files (F1.1-F6)
- **Patterns (P):** 63 files (P1-P63)
- **Total:** 85 patterns converted

### File Formats
- **Individual YAML:** 85 files in `m2m/yaml/`
- **Individual XML:** 85 files in `m2m/xml/`
- **Concatenated YAML:** 1 file (`universal_corpus_complete.yaml`)
- **Concatenated XML:** 1 file (`universal_corpus_complete.xml`)
- **Schemas:** 2 files in `m2m/schema/`
- **Total:** 172+ files

---

## 🎯 Usage Scenarios

### Scenario 1: Query Individual Patterns

```python
import yaml

# Load specific pattern
with open('m2m/yaml/P36_Selection-Driven_Panel.yaml') as f:
    pattern = yaml.safe_load(f)
    
print(f"Pattern: {pattern['metadata']['name']}")
print(f"Properties: {len(pattern['properties'])}")
```

### Scenario 2: Load Entire Corpus

```python
import yaml

# Load all patterns at once
with open('universal_corpus_complete.yaml') as f:
    corpus = yaml.safe_load(f)
    
print(f"Total patterns: {len(corpus['patterns'])}")

# Query by ID
p36 = next(p for p in corpus['patterns'] if p['id'] == 'P36')
```

### Scenario 3: XML Processing

```python
import xml.etree.ElementTree as ET

# Parse XML
tree = ET.parse('m2m/xml/P36_Selection-Driven_Panel.xml')
pattern = tree.getroot()

# Extract data
name = pattern.find('.//name').text
properties = pattern.findall('.//property')
```

### Scenario 4: Build Dependency Graph

```python
import yaml
from pathlib import Path

def build_graph():
    graph = {}
    for yaml_file in Path('m2m/yaml').glob('*.yaml'):
        with open(yaml_file) as f:
            pattern = yaml.safe_load(f)
            graph[pattern['id']] = pattern.get('dependencies', {})
    return graph
```

---

## ✅ Verification

### Mathematical Rigor Preserved

All mathematical notation is preserved exactly:
- ∀ (universal quantifier)
- ∃ (existential quantifier)
- → (implies)
- ⇒ (logical consequence)
- ⇔ (if and only if)
- ∈ (element of)
- φ, λ (Greek letters for functions)

**Example from P36:**
```yaml
formal_spec: |
  selection changes → content := φ₃₆(selection)
  ∀s ∈ Element: content = φ₃₆(s) when selection = s
```

### Structural Completeness

Every pattern includes:
- ✅ Formal tuple definition
- ✅ Component specifications with types
- ✅ Type definitions
- ✅ Properties with formal specifications
- ✅ Operations with signatures and definitions
- ✅ Dependencies (requires, uses, specializes)
- ✅ Real-world manifestations

---

## 🔧 Tool Integration

### Validation

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('universal_corpus_complete.yaml'))"

# Validate XML against schema
xmllint --schema m2m/schema/pattern.xsd m2m/xml/*.xml
```

### Code Generation

```python
# Generate TypeScript interfaces
def generate_ts_interface(pattern):
    components = pattern['definition']['components']
    ops = pattern['operations']
    
    interface = f"interface {pattern['metadata']['name'].replace(' ', '')} {{\n"
    for comp in components:
        interface += f"  {comp['name']}: {convert_type(comp['type'])};\n"
    for op in ops:
        interface += f"  {op['name']}({parse_params(op['signature'])}): {parse_return(op['signature'])};\n"
    interface += "}"
    return interface
```

### Search and Query

```python
# Find all patterns that use P31 (Observer Pattern)
import yaml

with open('universal_corpus_complete.yaml') as f:
    corpus = yaml.safe_load(f)

observers_users = [
    p['id'] for p in corpus['patterns']
    if 'P31' in p.get('dependencies', {}).get('requires', [])
]
```

---

## 📋 Schema Documentation

### YAML Schema (`m2m/schema/pattern_schema.yaml`)

Defines structure for:
- Pattern metadata (id, name, category, status)
- Formal definitions (tuple notation, components)
- Type system definitions
- Properties with invariants
- Operations with pre/postconditions
- Dependency relationships
- Manifestations

### XML Schema (`m2m/schema/pattern.xsd`)

XSD 1.0 compliant schema providing:
- Type validation
- Structure enforcement
- Namespace declarations
- Element cardinality rules

---

## 🎨 Format Comparison

| Feature | Individual Files | Concatenated File |
|---------|-----------------|-------------------|
| File size | Small (~3-10 KB each) | Large (~1-2 MB) |
| Load time | Fast per file | Slower initial load |
| Memory usage | Minimal | Higher |
| Query speed | File I/O per query | In-memory fast |
| Version control | Better diffs | Single diff |
| Distribution | Modular | Single artifact |

**Recommendation:**
- Use **individual files** for development and version control
- Use **concatenated file** for deployment and batch processing

---

## 🚀 Quick Start

### 1. Load a Pattern

```python
import yaml

# Single pattern
with open('m2m/yaml/P36_Selection-Driven_Panel.yaml') as f:
    p36 = yaml.safe_load(f)
    print(p36['metadata']['name'])
```

### 2. Load All Patterns

```python
# Entire corpus
with open('universal_corpus_complete.yaml') as f:
    corpus = yaml.safe_load(f)
    print(f"{len(corpus['patterns'])} patterns loaded")
```

### 3. Query by Criteria

```python
# Find all UI interaction patterns
ui_patterns = [
    p for p in corpus['patterns']
    if 'UI_Interaction' in p['metadata'].get('domains', [])
]
```

---

## 📖 Documentation Links

- **M2M Specification:** `../tmp/M2M_SPECIFICATION.md`
- **M2M Summary:** `../M2M_SUMMARY.md`
- **Original Markdown:** `../tmp/[CPF]*.md`
- **Converter Tool:** `../corpus_converter.py`

---

## ⚙️ Technical Details

### Encoding
- **Character Set:** UTF-8
- **Line Endings:** Unix (LF)
- **Mathematical Notation:** Unicode symbols + LaTeX

### YAML Details
- **Version:** YAML 1.2
- **Schema Version:** 1.0
- **Key Order:** Preserved (using ruamel.yaml or PyYAML with sort_keys=False)

### XML Details
- **Version:** XML 1.0
- **Namespace:** `http://universal-corpus.org/schema/v1`
- **Schema:** XSD 1.0
- **Formatting:** Pretty-printed with 2-space indent

---

## ✅ Quality Assurance

### Validation Performed
- ✅ All 85 patterns converted successfully
- ✅ Mathematical notation preserved (∀, ∃, →, ⇒, ⇔, ∈, φ, λ)
- ✅ Structural integrity maintained
- ✅ YAML syntax valid
- ✅ XML well-formed
- ✅ Cross-references intact

### Completeness Check
```
Core Concepts: 5/5 ✅
Flows: 17/17 ✅
Patterns: 63/63 ✅
Total: 85/85 ✅
```

---

## 🔄 Regeneration

To regenerate these files:

```bash
# From project root
./corpus_converter.py tmp/ --format both --output-dir output/m2m/

# Generate concatenated versions
python3 generate_concatenated.py
```

---

## 📝 Version History

### v1.0 (2025-11-22)
- Initial M2M conversion
- All 85 patterns converted
- YAML and XML formats
- Individual and concatenated files
- Schema definitions

---

## 🎉 Summary

**This output directory contains:**
- ✅ 85 patterns in machine-readable format
- ✅ Full mathematical rigor preserved
- ✅ Both individual and concatenated files
- ✅ YAML and XML support
- ✅ Complete schema definitions
- ✅ Ready for tool integration

**100% of Universal Corpus v1.1 converted with zero loss of formal rigor.**

---

**END OF README**



# Universal Corpus Pattern Language

**A Formal Specification System for AI-Native Interactive Systems**

> Rigorous mathematical patterns for human-computer interaction in the age of AI agents and multimodal interfaces.

---

## Overview

The Universal Corpus Pattern Language provides a comprehensive, formally specified collection of interaction patterns for building AI-native applications. Each pattern is defined with mathematical precision using tuple notation, formal type systems, and operational semantics.

**Key Features:**
- 🎯 **162 Formal Patterns**: 5 Concepts, 22 Flows, 155 Interaction Patterns
- 🔬 **Mathematical Rigor**: Formal specifications with type systems and invariants
- 🤖 **AI-Native Focus**: Purpose-built for multi-agent, conversational, and generative interfaces
- 🔌 **RESTful API**: Complete FastAPI implementation with Pydantic validation
- 💾 **SQLite Database**: Persistent storage with SQLAlchemy ORM
- 📊 **95% Coverage**: Comprehensive coverage of AI-native interaction domains

---

## 🚀 Quick Start

### Installation

#### From Source (Development)

```bash
# Clone the repository
git clone [repository-url]
cd universal

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with all dev dependencies
pip install -e ".[dev,test]"
```

#### Using pip (once published)

```bash
pip install universal-corpus
```

### Using the API

#### Development Server

```bash
# Using the convenience script
./scripts/run_dev_server.sh

# Or manually
source venv/bin/activate
uvicorn universal_corpus.api:app --reload

# API will be available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
# Database file: patterns.db (created automatically)
```

#### Docker

```bash
# Build the image
docker build -t universal-corpus .

# Run the container
docker run -d -p 8000:8000 -v $(pwd)/data:/app/data universal-corpus

# Using docker-compose
docker-compose up -d
```

### Running Tests

```bash
# Using the convenience script
./scripts/run_tests.sh

# Or manually
pytest tests/ -v --cov=universal_corpus --cov-report=html

# Run specific test file
pytest tests/test_api.py -v

# Run with output
pytest tests/ -v -s
```

### Code Quality

```bash
# Check code quality
./scripts/lint.sh

# Auto-format code
./scripts/format.sh
```

### CLI Tools

The package provides several command-line tools:

```bash
# Pattern management CLI
universal-corpus list --category concept
universal-corpus get C1
universal-corpus create --file pattern.json

# Corpus manager
corpus-manager export --format jsonl
corpus-manager import --file patterns.jsonl

# Compact format converter (NEW!)
python -m universal_corpus.cli.compact_converter to-compact input.jsonl output_compact.jsonl
python -m universal_corpus.cli.compact_converter analyze input.jsonl
python -m universal_corpus.cli.compact_converter validate input.jsonl

# Assessment tools
assess-dependencies
assess-data-quality
```

### API Examples

```python
import requests

# Create a pattern
pattern_data = {
    "id": "C1",
    "version": "1.1",
    "metadata": {
        "name": "Graph Structure",
        "category": "concept",
        "status": "stable"
    },
    # ... full pattern definition
}

response = requests.post("http://localhost:8000/patterns", json=pattern_data)
print(response.json())

# Get pattern as XML
xml_response = requests.get("http://localhost:8000/patterns/C1/xml")
print(xml_response.text)

# List all patterns
patterns = requests.get("http://localhost:8000/patterns?category=concept")
print(patterns.json())

# Export to JSONL (full format)
jsonl_data = requests.get("http://localhost:8000/export/jsonl")
with open("patterns.jsonl", "wb") as f:
    f.write(jsonl_data.content)

# Export to Compact JSONL (30% token reduction for AI/LLM sharing)
compact_data = requests.get("http://localhost:8000/export/compact")
with open("patterns_compact.jsonl", "wb") as f:
    f.write(compact_data.content)

# Export to CSV Compact (spreadsheet + programmatic access)
csv_compact = requests.get("http://localhost:8000/export/csv-compact")
with open("patterns_compact.csv", "wb") as f:
    f.write(csv_compact.content)

# Export to CSV Simple (91% reduction, perfect for humans!)
csv_simple = requests.get("http://localhost:8000/export/csv-simple")
with open("patterns_simple.csv", "wb") as f:
    f.write(csv_simple.content)

# Import from JSONL
with open("patterns.jsonl", "rb") as f:
    files = {"file": ("patterns.jsonl", f, "application/x-ndjson")}
    response = requests.post(
        "http://localhost:8000/import/jsonl?skip_existing=true",
        files=files
    )
    print(response.json())
    # {"status": "completed", "statistics": {"total": 10, "imported": 8, "skipped": 2, ...}}

# Import from JSON array
with open("patterns.json", "rb") as f:
    files = {"file": ("patterns.json", f, "application/json")}
    response = requests.post(
        "http://localhost:8000/import/json",
        files=files
    )
    print(response.json())
```

### Python Package Usage

```python
from universal_corpus import Pattern, PatternRepository, init_db, get_db

# Initialize database
init_db()

# Use repository pattern
from universal_corpus.database import SessionLocal
db = SessionLocal()
repo = PatternRepository(db)

# Create a pattern
pattern = Pattern(**pattern_data)
created = repo.create(pattern)

# Query patterns
patterns = repo.list(category="concept", limit=10)

# Get statistics
stats = repo.get_statistics()
print(f"Total patterns: {stats['total_patterns']}")
```

### Multiple Export Formats

The Universal Corpus provides **multiple export formats** optimized for different use cases:

| Format | Size | Best For |
|--------|------|----------|
| **Full JSONL** | 1,042 KB | API storage, complete data |
| **Compact JSONL** | 732 KB (-30%) | AI/LLM prompts, token optimization |
| **CSV Compact** | 832 KB (-20%) | Data analysis, spreadsheets + code |
| **CSV Simple** | 90 KB (-91%) | Human review, stakeholder presentations ⭐ |

### Compact Format for AI/LLM Sharing

The **Compact JSONL format** is specifically designed for sharing patterns with AI assistants and LLMs. It achieves **~30% token reduction** while preserving all semantic information.

#### Why Use Compact Format?

- **Save Tokens**: ~30% reduction in token consumption (260K → 183K tokens for 176 patterns)
- **Lower Costs**: Reduced API costs for AI interactions
- **Fit More Context**: Include more patterns within context windows
- **Still Human-Readable**: Uses intuitive abbreviations (`n` for name, `def` for definition)
- **Lossless**: Complete round-trip conversion validated

#### Quick Start

```bash
# Export patterns in compact format
curl http://localhost:8000/export/compact -o patterns_compact.jsonl

# Convert existing corpus to compact format
python -m universal_corpus.cli.compact_converter to-compact \
  final_corpus.jsonl final_corpus_compact.jsonl

# Analyze compression ratio
python -m universal_corpus.cli.compact_converter analyze final_corpus.jsonl
```

#### Format Comparison

**Full Format** (1,482 tokens per pattern average):
```json
{
  "id": "C1",
  "version": "1.1",
  "metadata": {
    "name": "Graph Structure",
    "category": "concept",
    "status": "stable",
    "complexity": "medium"
  },
  "definition": {
    "tuple_notation": {
      "content": "$G = (N, E, \\lambda_n, \\lambda_e)$",
      "format": "latex"
    }
  }
}
```

**Compact Format** (1,039 tokens per pattern average):
```json
{
  "id": "C1",
  "v": "1.1",
  "name": "Graph Structure",
  "cat": "concept",
  "status": "stable",
  "cx": "medium",
  "def": "$G = (N, E, \\lambda_n, \\lambda_e)$"
}
```

**Savings:** ~443 tokens per pattern (29.8% reduction)

#### Key Abbreviations

| Full | Compact | Full | Compact |
|------|---------|------|---------|
| `version` | `v` | `formal_spec` | `spec` |
| `category` | `cat` | `preconditions` | `pre` |
| `complexity` | `cx` | `postconditions` | `post` |
| `components` | `comps` | `effects` | `fx` |
| `properties` | `props` | `invariants` | `inv` |
| `operations` | `ops` | `manifestations` | `manif` |

#### API Integration

```python
import requests

# Export compact format
compact = requests.get("http://localhost:8000/export/compact")

# Import compact format
with open("patterns_compact.jsonl", "rb") as f:
    response = requests.post(
        "http://localhost:8000/import/compact",
        files={"file": f}
    )
```

#### Use Cases

- **AI Prompts**: Embed pattern data in prompts with minimal token overhead
- **RAG Systems**: Efficient pattern embedding and retrieval
- **Documentation**: Quick pattern reference for AI assistants
- **API Optimization**: Reduce bandwidth and token costs

### CSV Formats for Spreadsheets & Data Analysis

Two **CSV formats** provide columnar (spreadsheet-friendly) representations:

#### CSV Simple (Recommended for Humans!) ⭐

```bash
curl http://localhost:8000/export/csv-simple -o patterns.csv
# or
python -m universal_corpus.cli.compact_converter to-csv --simple input.jsonl output.csv
```

**Features:**
- **91% smaller** than full format (90KB vs 1MB!)
- Opens directly in Excel/Google Sheets
- Human-readable columns only
- Count columns: `num_components`, `num_properties`, etc.
- Perfect for stakeholder reviews and quick browsing

**Sample columns:**
```
id | name | category | status | complexity | num_components | num_properties | ...
C1 | Graph Structure | concept | stable | medium | 2 | 2 | ...
```

#### CSV Compact (For Data Analysis)

```bash
curl http://localhost:8000/export/csv-compact -o patterns.csv
```

**Features:**
- Full data preservation with detail columns
- Programmatic access via compact JSON in `*_detail` columns
- Spreadsheet-compatible for manual review
- Round-trip conversion supported

**Use cases:**
- pandas/R analysis: `pd.read_csv('patterns.csv')`
- SQL imports
- BI tools
- Combined manual + programmatic workflows

📖 **Full Documentation**: 
- [docs/COMPACT_FORMAT.md](docs/COMPACT_FORMAT.md) - Compact JSONL specification
- [docs/CSV_FORMAT_GUIDE.md](docs/CSV_FORMAT_GUIDE.md) - CSV formats guide and examples

---

## 🏗️ Architecture

### Project Structure

```
universal/
├── src/
│   └── universal_corpus/      # Main package
│       ├── __init__.py         # Package initialization
│       ├── models.py           # Pydantic models for validation
│       ├── database.py         # SQLAlchemy database layer
│       ├── api.py              # FastAPI REST API
│       ├── compact_format.py   # Token-efficient format (NEW!)
│       ├── cli/                # Command-line tools
│       │   ├── pattern_cli.py
│       │   ├── pattern_cli_ai.py
│       │   ├── corpus_manager.py
│       │   └── compact_converter.py  # Compact format CLI (NEW!)
│       └── scripts/            # Utility scripts
├── tests/                      # Test suite
│   ├── conftest.py            # Pytest configuration and fixtures
│   └── test_api.py            # API and model tests
├── data/                       # Data storage
│   └── master_data/           # Master dataset
│       ├── final_corpus.jsonl         # Full format corpus
│       └── final_corpus_compact.jsonl # Compact format (NEW!)
├── docs/                       # Documentation
│   ├── COMPACT_FORMAT.md      # Compact format specification (NEW!)
│   └── autonomous_ai_extracted.txt
├── examples/                   # Example code
│   └── compact_format_demo.py # Compact format demo (NEW!)
├── output/                     # Generated outputs
│   ├── csv_master/
│   ├── generated_md/
│   └── m2m/
├── scripts/                    # Development scripts
│   ├── run_dev_server.sh      # Start development server
│   ├── run_tests.sh           # Run test suite
│   ├── lint.sh                # Code quality checks
│   └── format.sh              # Auto-format code
├── pyproject.toml             # Project metadata and dependencies
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
└── README.md                  # This file
```

### Core Components

1. **models.py** - Pydantic models for validation and serialization
   - Type-safe models matching XSD schema
   - Comprehensive validation with regex patterns
   - JSON serialization support

2. **database.py** - SQLAlchemy database layer
   - `PatternDB` - SQLAlchemy ORM model
   - `PatternRepository` - Repository pattern for CRUD operations
   - Connection pooling and session management
   - Queryable metadata fields with JSON storage

3. **api.py** - FastAPI REST API
   - Complete CRUD endpoints
   - XML/JSON/JSONL export functionality
   - Filtering and pagination
   - Statistics and dependencies endpoints

4. **tests/** - Comprehensive test suite
   - 50+ test cases covering all scenarios
   - Model validation tests
   - API endpoint tests
   - Integration tests

### Database Schema

```sql
CREATE TABLE patterns (
    id VARCHAR(50) PRIMARY KEY,
    version VARCHAR(20) NOT NULL,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    complexity VARCHAR(20),
    data TEXT NOT NULL,          -- Complete pattern as JSON
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- Indexes for efficient querying
CREATE INDEX ix_patterns_id ON patterns (id);
CREATE INDEX ix_patterns_name ON patterns (name);
CREATE INDEX ix_patterns_category ON patterns (category);
CREATE INDEX ix_patterns_status ON patterns (status);
```

### Data Flow

```
Client Request
    ↓
FastAPI Endpoint (api.py)
    ↓
Pydantic Validation (models.py)
    ↓
Repository Pattern (database.py)
    ↓
SQLAlchemy ORM
    ↓
SQLite Database (patterns.db)
```

---

## 📦 Corpus Structure

### **1. Concepts (C1-C5)**

Foundational data structures that underpin the pattern language:
- `C1` - **Graph Structure**: Node-edge relationships with labeling functions
- `C2` - **Document-Artifact**: Structured content representation
- `C3` - **Symbolic Expression**: Formal symbolic computation
- `C4` - **Metadata Schema**: Structured metadata definitions
- `C5` - **Version History**: Temporal state tracking

#### **2. Flows (F1-F6)**
Process patterns that describe sequences of operations:
- **F1** - Input Processing: Capture, Import, Live Stream
- **F2** - Computation: Pipeline, Agent Orchestration, Incremental Computation, Enrichment
- **F3** - Learning: Learning Loop, Validation Loop, Adaptation Loop, User Preference Loop
- **F4** - Output: Reactive Render, Notification, Export-Publish, Materialized View
- **F5** - Collaborative Editing
- **F6** - Error Recovery

#### **3. Patterns (P1-P155)**
Interaction design patterns organized across 16 categories and 3 priority phases.

---

## ðŸ“Š Pattern Categories

### Phase 1: Critical Patterns (30 patterns)
**Essential patterns for AI-native interactions**

#### Category 1: Generative/Dynamic UI (P64-P67)
Patterns for AI-generated and context-adaptive interfaces:
- `P64` - **Generative UI**: AI-generated interface components
- `P65` - **Streaming Component**: Token-by-token UI rendering
- `P66` - **Context-Adaptive Interface**: UI that morphs based on context
- `P67` - **Progressive Disclosure by AI**: Intelligent information revelation

#### Category 2: Multi-Agent Orchestration UI (P68-P73)
Patterns for visualizing and controlling multiple AI agents:
- `P68` - **Agent Team Visualization**: Display agent roles and relationships
- `P69` - **Agent Activity Timeline**: Show parallel agent operations
- `P70` - **Agent Handoff**: Transfer context between agents
- `P71` - **Orchestration Dashboard**: Central control for agent systems
- `P72` - **Agent Role Selector**: Dynamic agent assignment
- `P73` - **Composite Action**: Bundle multiple agent actions

#### Category 3: Proactive AI Assistance (P74-P79)
Patterns for autonomous AI behavior:
- `P74` - **Continuous AI Monitoring**: Background observation and suggestions
- `P75` - **Proactive Intervention**: AI-initiated assistance
- `P76` - **Ambient AI**: Unobtrusive contextual awareness
- `P77` - **Intelligent Interruption**: Optimal timing for AI interruptions
- `P78` - **Background Task Management**: Async agent operations
- `P79` - **Anticipatory Action**: Predictive resource preparation

#### Category 4: Voice & Multimodal Interaction (P80-P85)
Patterns for speech and multimodal input:
- `P80` - **Voice Conversation**: Bidirectional speech interaction
- `P81` - **Voice Command with Visual Feedback**: Voice + visual confirmation
- `P82` - **Multimodal Input Fusion**: Combine voice, gesture, and touch
- `P83` - **Voice-First Navigation**: Speech-driven interface navigation
- `P84` - **Continuous Dictation**: Streaming speech-to-text
- `P85` - **Voice Disambiguation**: Clarify ambiguous voice commands

#### Category 5: Human-in-Loop & Agency Control (P86-P92)
Patterns for managing AI autonomy:
- `P86` - **Approval Checkpoint**: Human approval for critical actions
- `P87` - **Agency Slider**: Adjust AI autonomy levels
- `P88` - **Collaboration Mode Switcher**: Toggle human-AI control modes
- `P89` - **Confidence Indicator**: Display AI certainty levels
- `P90` - **Explanation on Demand**: Request AI reasoning
- `P91` - **Intervention Request**: AI asks for human help
- `P92` - **Contextual Undo/Rollback**: Revert AI actions with dependencies

### Phase 2: High Priority Patterns (30 patterns)

#### Category 6: Agent State Visualization (P93-P98)
Transparency patterns for AI agent operations:
- `P93` - **Agent Thinking Indicator**: Show reasoning in progress
- `P94` - **Tool Execution Visualization**: Display active tool usage
- `P95` - **Multi-Step Progress**: Track workflow completion
- `P96` - **Real-Time Confidence Display**: Live confidence updates
- `P97` - **Resource Usage Indicator**: Show token/cost consumption
- `P98` - **Agent State Timeline**: Historical state visualization

#### Category 7: Knowledge Graph UI (P99-P105)
Patterns for knowledge representation and retrieval:
- `P99` - **Knowledge Graph Explorer**: Interactive graph navigation
- `P100` - **Source Citation**: Link content to sources
- `P101` - **Retrieval Path Visualization**: Show how information was found
- `P102` - **Confidence-Based Highlighting**: Visual confidence encoding
- `P103` - **Multi-Source Reconciliation**: Handle conflicting sources
- `P104` - **Graph Query Builder**: Visual query construction
- `P105` - **Semantic Similarity Visualizer**: Display concept relationships

#### Category 8: Living Documents (P106-P111)
Patterns for AI-maintained documents:
- `P106` - **Auto-Updating Content**: Self-refreshing documents
- `P107` - **Suggested Edits**: AI-proposed improvements
- `P108` - **Cross-Document Linking**: Automatic relationship detection
- `P109` - **Outdated Content Detection**: Flag stale information
- `P110` - **Collaborative Document Intelligence**: Multi-agent document editing
- `P111` - **Document Evolution Timeline**: Track document changes

#### Category 9: Event-Driven UI (P112-P117)
Patterns for reactive, event-based interfaces:
- `P112` - **Event Stream Visualization**: Real-time event display
- `P113` - **Event Replay Control**: Playback historical events
- `P114` - **Stream Backpressure**: Handle overwhelming event rates
- `P115` - **Event-Driven State Updates**: Reactive state management
- `P116` - **Multi-Stream Coordination UI**: Sync multiple event streams
- `P117` - **Event Filter & Query**: Search and filter events

#### Category 10: Multi-Domain Management (P118-P123)
Patterns for managing multiple domains or contexts:
- `P118` - **Domain Context Switcher**: Switch between work contexts
- `P119` - **Cross-Domain Integration View**: Unified multi-domain display
- `P120` - **Domain-Specific Agent Activation**: Specialized agent selection
- `P121` - **Context Preservation Across Domains**: Maintain state across switches
- `P122` - **Multi-Domain Dashboard**: Aggregate cross-domain metrics
- `P123` - **Domain Boundary Indicator**: Show current domain scope

### Phase 3: Medium Priority Patterns (32 patterns)

#### Category 11: AI Observability (P124-P129)
Patterns for understanding AI system behavior:
- `P124` - **Agent Trace Viewer**: Detailed execution traces
- `P125` - **Decision Explanation**: Explain AI decisions
- `P126` - **Token Usage Display**: Show consumption metrics
- `P127` - **Error Debug Interface**: AI error investigation
- `P128` - **A/B Test Results**: Experiment comparison
- `P129` - **Performance Metrics Dashboard**: System performance tracking

#### Category 12: Collaborative Presence (P130-P135)
Patterns for human-AI collaboration awareness:
- `P130` - **AI Agent Presence Indicator**: Show active agents
- `P131` - **Multi-User + AI Avatar**: Represent humans and agents
- `P132` - **AI Cursor Sharing**: Show agent focus areas
- `P133` - **Activity Feed**: Stream of collaborative actions
- `P134` - **Collaboration Session**: Shared workspace management
- `P135` - **Conflict Resolution Interface**: Resolve edit conflicts

#### Category 13: Personalization & Learning (P136-P140)
Patterns for system adaptation:
- `P136` - **User Preference Learning**: Learn user patterns
- `P137` - **Adaptive Interface**: UI that adapts to user
- `P138` - **Personalized Agent Configuration**: Custom agent setup
- `P139` - **Learning Progress Indicator**: Show adaptation progress
- `P140` - **Reset/Retrain Controls**: Restart learning process

#### Category 14: Workflow Automation (P141-P145)
Patterns for automating tasks:
- `P141` - **Workflow Template Gallery**: Pre-built automation templates
- `P142` - **Automation Builder**: Visual workflow construction
- `P143` - **Scheduled Agent**: Time-based agent execution
- `P144` - **Trigger-Action**: Event-driven automation
- `P145` - **Workflow Monitoring Dashboard**: Track automation status

#### Category 15: Cost & Resource Management (P146-P150)
Patterns for managing computational resources:
- `P146` - **Token Budget Indicator**: Track token allowance
- `P147` - **Cost Estimation Preview**: Preview operation costs
- `P148` - **Resource Limit Controls**: Set resource constraints
- `P149` - **Usage Analytics Dashboard**: Analyze resource consumption
- `P150` - **Rate Limit Warning**: Alert on approaching limits

#### Category 16: Security & Trust (P152-P155)
Patterns for secure and trustworthy AI:
- `P152` - **Audit Trail Viewer**: Review system actions
- `P153` - **Data Access Transparency**: Show what data is accessed
- `P154` - **Secure Credential Management**: Handle secrets safely
- `P155` - **Trust Score Indicator**: Display agent reliability

### Classical HCI Patterns (P1-P63)
Foundational patterns adapted from traditional HCI:
- **Interface Patterns** (P1-P9): Canvas, Command, Navigator, Inspector, Workspace, Palette, Breadcrumbs, Search, Backlinks
- **Backend Patterns** (P10-P25): Parser, Validator, Solver, Indexer, Agent Swarm, Reasoning Chain, Suggestion System, Storage, Sync, APIs
- **Feedback Patterns** (P26-P28): Status Bar, Toast, Progress
- **State & Architecture** (P29-P34): State Store, Command, Observer, Plugin, Hook, Strategy
- **Layout & Navigation** (P35-P46): Split-Pane, Selection-Driven Panel, Empty State, Badge, Action Menu, Mode Toggle, Status Chip, Tooltip, Navigation Drawer, Keyboard Shortcuts, Drag & Drop, Focus Management
- **Forms & Input** (P47-P50): Inline Editing, Validation, Multi-Step Forms, Dependencies
- **Data Display** (P51-P60): Responsive Layout, Pagination, Filtering, Sorting, Virtualization, Caching, Migration, Authentication, Authorization, Sanitization
- **Testing** (P61-P63): Unit, Integration, End-to-End Tests

---

## ðŸ”¬ Formal Specification Language

Each pattern is rigorously defined using mathematical notation. The formal language includes:

### Notation Key
```
Ï†  : Functions/mappings
Ï„  : Token streams
Ïƒ  : Strategies
Ï  : Rollback functions
Î”  : Deltas/changes
Î©  : Orchestration
â†”  : Bidirectional
â†’  : Unidirectional mapping
âˆª  : Union
Ã—  : Cartesian product
âˆˆ  : Element of
âŸ¨âŸ© : Generic type brackets
```

### Pattern Structure

Each pattern XML file contains:

```xml
<pattern id="PXX" version="1.1">
  <metadata>
    <n>Pattern Name</n>
    <category>pattern|concept|flow</category>
    <status>stable|experimental</status>
    <complexity>low|medium|high</complexity>
  </metadata>
  
  <definition>
    <tuple-notation format="latex">
      $P = (Câ‚, Câ‚‚, ..., Câ‚™) : Input â†’ Output$
    </tuple-notation>
    
    <components>
      <!-- Formal component definitions -->
    </components>
    
    <type-definitions>
      <!-- Custom type specifications -->
    </type-definitions>
  </definition>
  
  <properties>
    <!-- Formal properties and invariants -->
  </properties>
  
  <operations>
    <!-- Computational operations -->
  </operations>
  
  <manifestations>
    <!-- Real-world implementations -->
  </manifestations>
</pattern>
```

### Example: Generative UI Pattern

```
G = (T_lib, ctx, gen, render, stream) : ctx Ã— T_lib â†’ UI_dynamic

Where:
- T_lib    : Component library
- ctx      : Current context
- gen      : Generation function
- render   : Rendering function  
- stream   : Token stream processor
```

---

## ðŸŽ¨ Use Cases

This pattern language supports design and implementation of:

### 1. **AI-Native Applications**
- Conversational interfaces with autonomous agents
- Multi-agent collaborative systems
- Context-aware adaptive UIs
- Proactive assistance systems

### 2. **Enterprise Tools**
- Knowledge management systems with AI
- Workflow automation platforms
- Decision support systems
- Collaborative workspaces with AI agents

### 3. **Development Frameworks**
- UI component libraries
- Agent orchestration frameworks
- Multimodal interaction systems
- Real-time collaboration tools

### 4. **Research & Education**
- HCI research on AI-native interfaces
- Teaching interaction design principles
- Prototyping new interaction paradigms
- Benchmarking interface implementations

---

## ðŸ“– Documentation Structure

```
/
â”œâ”€â”€ C1-C5_*.xml              # Core concepts
â”œâ”€â”€ F1-F6_*.xml              # Process flows
â”œâ”€â”€ P1-P155_*.xml            # Interaction patterns
â”œâ”€â”€ complete_patterns_outline.md   # Full pattern catalog
â”œâ”€â”€ PATTERNS_CHECKLIST.txt   # Implementation tracking
â””â”€â”€ README.md                # This file
```

---

## ðŸ” Pattern Selection Guide

### By Development Phase

**Starting a new AI-native application?**
â†’ Begin with Phase 1 patterns (P64-P92)

**Building transparency and trust?**
â†’ Implement Phase 2 patterns (P93-P123)

**Optimizing and scaling?**
â†’ Add Phase 3 patterns (P124-P155)

### By Functionality

**Need agent orchestration?**
â†’ P68-P73, P14-P16

**Want voice interaction?**
â†’ P80-P85

**Implementing living documents?**
â†’ P106-P111

**Managing costs?**
â†’ P146-P150

**Building trust?**
â†’ P89-P90, P152-P155

---

## ðŸš€ Getting Started

### For Designers

1. Browse the `complete_patterns_outline.md` for pattern summaries
2. Select patterns relevant to your use case
3. Reference XML files for formal specifications
4. Adapt manifestations to your specific context

### For Developers

1. Parse pattern XML files for formal definitions
2. Implement pattern operations in your target framework
3. Ensure properties and invariants are maintained
4. Test against pattern-specified behaviors

### For Researchers

1. Use formal notation for rigorous analysis
2. Extend patterns with new properties
3. Compose patterns into higher-level systems
4. Validate against real-world implementations

---

## ðŸ¤ Pattern Relationships

Patterns in this corpus are designed to compose:

- **Vertical Integration**: Concepts â†’ Flows â†’ Patterns
- **Horizontal Composition**: Patterns combine to form complete systems
- **Category Relationships**: Patterns within categories reinforce each other
- **Cross-Category Dependencies**: Security patterns enable Trust patterns, etc.

Example composition:
```
Agent Team Visualization (P68)
  + Agent Activity Timeline (P69)
  + Agent Thinking Indicator (P93)
  + Confidence Indicator (P89)
  = Complete Agent Transparency System
```

---

## ðŸ“Š Coverage Metrics

| Domain | Coverage |
|--------|----------|
| Classical HCI | 100% |
| Generative UI | 95% |
| Multi-Agent Orchestration | 90% |
| Voice/Multimodal | 85% |
| Human-in-Loop Control | 100% |
| AI Observability | 95% |
| Knowledge Management | 90% |
| Collaborative Presence | 85% |
| Resource Management | 90% |
| Security & Trust | 85% |

**Overall AI-Native Coverage: 95%**

---

## ðŸŽ¯ Design Principles

This pattern language is built on:

1. **Formal Rigor**: Mathematical specifications enable precise implementation
2. **Composability**: Patterns combine to form complete systems
3. **Human-Centricity**: AI serves human needs, not vice versa
4. **Transparency**: Users understand AI behavior and decisions
5. **Agency Control**: Users maintain appropriate levels of control
6. **Trust & Safety**: Security and reliability are first-class concerns
7. **Adaptability**: Systems learn and evolve with users
8. **Multimodality**: Support diverse input and output modes

---

## ðŸŒŸ Key Innovations

This corpus introduces several novel patterns for AI-native interfaces:

- **Generative UI** (P64): First formal specification of AI-generated interfaces
- **Agent Handoff** (P70): Structured context transfer between AI agents
- **Agency Slider** (P87): Dynamic human-AI control distribution
- **Living Documents** (P106-P111): Self-updating, AI-maintained content
- **Multimodal Fusion** (P82): Formal model for combining input modalities
- **Proactive AI Patterns** (P74-P79): Autonomous assistance frameworks

---

## ðŸ”® Future Directions

Planned extensions include:

- **Embodied AI Patterns**: Physical robot interaction patterns
- **Spatial Computing Patterns**: AR/VR with AI agents
- **Neuromorphic Patterns**: Brain-computer interface patterns
- **Quantum UI Patterns**: Quantum computing visualization
- **Collective Intelligence Patterns**: Large-scale multi-agent systems
- **Affective Computing Patterns**: Emotion-aware interfaces

---

## ðŸ“ Contributing

This is a living pattern language. Contributions welcome in:

- New pattern proposals with formal specifications
- Pattern relationship mappings
- Implementation examples
- Research validations
- Bug fixes in formal definitions

---

## ðŸ“š References

This pattern language builds on foundational work in:

- Christopher Alexander's *Pattern Language* (1977)
- Don Norman's *Design of Everyday Things* (1988)
- Ben Shneiderman's *Direct Manipulation* (1983)
- Stuart Card's *Model Human Processor* (1983)
- Modern HCI research on AI-native interfaces

---

## ðŸ“„ License

Pattern specifications are provided for educational and research use. Implementation details and manifestations may vary by jurisdiction and use case.

---

## ðŸ›ï¸ Citation

If you use this pattern language in research or development, please cite:

```
Human-Computer Interaction Pattern Language: A Formal Corpus for AI-Native Interactive Systems (2025)
https://github.com/[your-repo]
```

---

## ðŸ“§ Contact

For questions, collaborations, or pattern proposals:
- Open an issue in this repository
- Join our discussion forum
- Email: [contact information]

---

**Version**: 1.1  
**Last Updated**: November 2025  
**Patterns**: 162 (5 Concepts + 22 Flows + 155 Patterns)  
**Coverage**: 95% for AI-native multi-agent interfaces

---

*Building the foundation for the next generation of human-computer interaction.*
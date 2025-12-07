# CMS Editor - Complete UX/UI Specification
**Version:** 2.0  
**Date:** November 23, 2025  
**Status:** Draft for Review

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture & Formal Foundation](#2-system-architecture--formal-foundation)
3. [User Experience Design](#3-user-experience-design)
4. [Information Architecture](#4-information-architecture)
5. [UI Component Specifications](#5-ui-component-specifications)
6. [Interaction Patterns & Workflows](#6-interaction-patterns--workflows)
7. [Visual Design System](#7-visual-design-system)
8. [Technical Implementation Guidelines](#8-technical-implementation-guidelines)
9. [Accessibility & Performance](#9-accessibility--performance)
10. [Future Enhancements](#10-future-enhancements)

---

## 1. Executive Summary

### 1.1 Project Overview

The CMS Editor is a next-generation content management system built on formal design patterns and mathematical foundations. It provides content creators, developers, and administrators with a powerful, intuitive interface for managing complex content structures, workflows, and collaborative editing.

### 1.2 Core Objectives

- **Formal Correctness**: Apply proven design patterns (P1-P30+) and concepts (C1-C5) for reliability
- **User-Centric Design**: Intuitive interface that scales from novice to expert users
- **Collaborative by Design**: Real-time multi-user editing with conflict resolution (F5)
- **Extensible Architecture**: Plugin system built on formal component composition
- **Performance**: Sub-200ms interactions, optimistic UI updates, efficient data structures

### 1.3 Key Differentiators

1. **Graph-Based Content Model** (C1): Content as nodes with rich relationships
2. **Version History as First-Class Citizen** (C5): Complete audit trail and time-travel debugging
3. **Formal Validation Pipeline** (P11): Catch errors before they propagate
4. **AI-Powered Suggestions** (P16): Context-aware content recommendations
5. **Real-Time Collaboration** (F5): Operational Transform-based concurrent editing

---

## 2. System Architecture & Formal Foundation

### 2.1 Core Concepts

#### 2.1.1 Graph Structure (C1)

**Definition**: Content model represented as `G = (N, E, λₙ, λₑ)`

```
Nodes (N): Content items (pages, posts, media, components)
Edges (E): Relationships (parent-child, references, links)
λₙ: Node labeling (type, metadata, content)
λₑ: Edge labeling (relationship type, constraints)
```

**Application in CMS**:
- Pages, posts, media, and components are nodes
- Parent-child, cross-references, media links are edges
- Enables powerful queries: "Find all pages referencing this image"
- Supports circular dependency detection
- Facilitates content reuse and modular design

**Operations**:
- `traverse(node, depth)`: Content tree navigation
- `neighbors(node)`: Get related content
- `path(nodeA, nodeB)`: Find connection between content items

#### 2.1.2 Document/Artifact Structure (C2)

**Definition**: Content item with versioning and metadata

```typescript
type Document = {
  id: DocumentID
  content: Content
  metadata: Metadata
  version: Version
  history: VersionHistory
  permissions: AccessControl
}
```

**Properties**:
- Immutable versions (P.C2.1)
- Complete audit trail
- Branching support
- Rich metadata schema (C4)

#### 2.1.3 Version History (C5)

**Definition**: `H = (commits, branches, merge_strategy)`

**Features**:
- Linear history with branching
- Merge conflict detection
- Time-travel to any version
- Diff visualization
- Blame/attribution tracking

#### 2.1.4 Metadata Schema (C4)

**Definition**: Extensible key-value pairs with validation

```typescript
type Metadata = {
  [key: string]: {
    value: any
    type: DataType
    required: boolean
    validator?: ValidationRule
  }
}
```

### 2.2 Architectural Patterns

#### 2.2.1 Command Pattern (P30)

All user actions are commands:

```typescript
interface Command {
  execute(): Promise<Result>
  undo(): Promise<void>
  redo(): Promise<void>
  validate(): ValidationResult
}
```

**Benefits**:
- Undo/redo stack
- Command history
- Macro recording
- Keyboard shortcuts mapping

#### 2.2.2 Parser/Compiler Pipeline (P10)

Content transformation pipeline:

```
Raw Input → Lexer → Parser → Validator → Transformer → Renderer
```

**Stages**:
1. **Lexical Analysis**: Tokenize markdown/HTML/custom syntax
2. **Parsing**: Build AST (Abstract Syntax Tree)
3. **Validation** (P11): Check constraints, references
4. **Transformation**: Apply plugins, macros
5. **Rendering**: Generate output (HTML, PDF, etc.)

#### 2.2.3 Validator/Checker (P11)

Multi-level validation:

```typescript
type ValidationLevel = 'syntax' | 'semantic' | 'business' | 'accessibility'

interface Validator {
  validate(content: Content, level: ValidationLevel): ValidationResult
  constraints: Rule[]
  suggestions: Hint[]
}
```

**Validation Types**:
- **Syntax**: Markdown/HTML structure
- **Semantic**: Link validity, image existence
- **Business**: Required fields, workflow state
- **Accessibility**: Alt text, heading hierarchy, color contrast

#### 2.2.4 Indexer/Query Engine (P13)

Full-text search with facets:

```typescript
interface QueryEngine {
  index(document: Document): void
  search(query: SearchQuery): SearchResults
  facets: Facet[]
}

type SearchQuery = {
  text?: string
  filters?: Filter[]
  sort?: SortCriteria
  facets?: FacetSelection[]
}
```

**Features**:
- Full-text search (Elasticsearch/Meilisearch)
- Fuzzy matching
- Tag/category filters
- Date range filters
- Author filters
- Status filters

#### 2.2.5 Suggestion/Recommendation System (P16)

Context-aware AI assistance:

```typescript
interface SuggestionEngine {
  suggest(context: EditContext): Suggestion[]
  learn(feedback: UserFeedback): void
  model: MLModel
}
```

**Suggestion Types**:
- Content completions
- SEO improvements
- Accessibility fixes
- Related content links
- Image suggestions
- Tag recommendations

---

## 3. User Experience Design

### 3.1 User Personas

#### 3.1.1 Content Creator (Primary)

**Profile**:
- Name: Sarah, Marketing Manager
- Experience: Intermediate technical skills
- Goals: Create engaging content quickly, collaborate with team
- Pain Points: Complex formatting, broken links, slow workflows

**Needs**:
- Intuitive WYSIWYG editor
- Real-time preview
- Quick media insertion
- Template library
- Version history

#### 3.1.2 Developer (Secondary)

**Profile**:
- Name: Alex, Frontend Developer
- Experience: Advanced technical skills
- Goals: Customize CMS, integrate with other systems, optimize performance
- Pain Points: Limited API access, poor documentation, inflexible data models

**Needs**:
- Code editor mode
- API access
- Plugin development tools
- Webhook configuration
- GraphQL/REST APIs

#### 3.1.3 Administrator (Tertiary)

**Profile**:
- Name: James, IT Administrator
- Experience: System administration background
- Goals: Manage users, monitor system health, configure workflows
- Pain Points: Complex permission systems, lack of analytics, security concerns

**Needs**:
- User management dashboard
- System monitoring
- Audit logs
- Workflow configuration
- Security controls

### 3.2 User Journey Maps

#### 3.2.1 Content Creation Journey

```
1. DISCOVER
   ↓ Browse template library or start from scratch
2. CREATE
   ↓ Write content with AI assistance and real-time validation
3. ENHANCE
   ↓ Add media, format text, create links
4. REVIEW
   ↓ Preview across devices, check accessibility
5. COLLABORATE
   ↓ Share with team, receive feedback
6. PUBLISH
   ↓ Schedule or publish immediately
7. MONITOR
   ↓ Track analytics, update as needed
```

#### 3.2.2 Content Management Journey

```
1. SEARCH
   ↓ Find content using filters and full-text search
2. ANALYZE
   ↓ View content relationships and dependencies
3. ORGANIZE
   ↓ Tag, categorize, create collections
4. MAINTAIN
   ↓ Update outdated content, fix broken links
5. ARCHIVE
   ↓ Remove or archive obsolete content
```

### 3.3 Core User Flows

#### 3.3.1 Input Capture Flow (F1.1)

**Trigger**: User wants to create new content

**Steps**:
1. Click "New Content" → Template selector modal
2. Choose template or blank → Editor opens
3. Auto-save starts (every 5 seconds)
4. Real-time validation (P11) shows inline warnings
5. Progress indicator (P28) for long operations

**Error Handling** (F6):
- Connection lost → Show toast (P27), enable offline mode
- Validation error → Inline error with suggestion (P16)
- Auto-save failed → Retry with exponential backoff

#### 3.3.2 Collaborative Editing Flow (F5)

**Trigger**: Multiple users edit same document

**Steps**:
1. User A opens document → Acquire edit lock
2. User B opens document → Show "User A is editing" indicator
3. Both users edit → Operational Transform resolves conflicts
4. Changes stream (P25) → Sub-100ms latency
5. Cursor positions visible → Awareness of collaborators
6. Auto-merge on save → Manual resolution if conflicts

**Conflict Resolution**:
```
IF no_conflict THEN
  auto_merge()
ELSE IF simple_conflict THEN
  show_inline_resolution_UI()
ELSE
  show_3way_merge_editor()
END IF
```

#### 3.3.3 Export and Publishing Flow (F4.3)

**Trigger**: User wants to publish content

**Steps**:
1. Click "Publish" → Validation runs (P11)
2. IF errors → Show blocking modal with fixes
3. IF warnings → Show confirmable modal
4. Select publish target (web, API, static site)
5. Configure options (schedule, visibility)
6. Progress indicator (P28) shows export status
7. Success toast (P27) with preview link

---

## 4. Information Architecture

### 4.1 Navigation Structure

```
┌─ Primary Navigation (Left Sidebar)
│  ├─ Dashboard (Overview, recent items)
│  ├─ Content
│  │  ├─ All Content (List view with filters)
│  │  ├─ Pages
│  │  ├─ Posts
│  │  ├─ Custom Types
│  │  └─ Drafts
│  ├─ Media Library
│  │  ├─ Images
│  │  ├─ Videos
│  │  ├─ Documents
│  │  └─ Collections
│  ├─ Structure
│  │  ├─ Navigation Menus
│  │  ├─ Content Model (Graph view)
│  │  └─ Taxonomies (Tags, Categories)
│  ├─ Users & Teams
│  │  ├─ Users
│  │  ├─ Roles & Permissions
│  │  └─ Activity Log
│  ├─ Settings
│  │  ├─ General
│  │  ├─ Publishing
│  │  ├─ Integrations
│  │  └─ Plugins
│  └─ Help & Support
│
├─ Top Bar
│  ├─ Global Search (⌘K)
│  ├─ Notifications
│  ├─ Quick Actions
│  └─ User Menu
│
└─ Context Panel (Right Sidebar - Conditional)
   ├─ Content Properties
   ├─ Version History
   ├─ Comments & Feedback
   └─ SEO & Metadata
```

### 4.2 Content Organization

#### 4.2.1 Graph-Based Organization (C1)

Content organized as directed acyclic graph (DAG):

```
Site Root
├── Pages (hierarchical)
│   ├── Home
│   ├── About
│   │   ├── Team
│   │   └── History
│   └── Services
├── Posts (chronological)
│   └── Blog Post 1
│       ├→ References: [Image1, Author1]
│       └→ Tagged: [Tech, Tutorial]
└── Media
    ├── Image1
    └── Video1
```

**Benefits**:
- Multiple parents (content reuse)
- Automatic backlinks ("Referenced by")
- Circular reference detection
- Orphan content detection

#### 4.2.2 Taxonomy System

**Multi-dimensional Classification**:

```typescript
type Taxonomy = {
  tags: string[]           // Folksonomy (user-generated)
  categories: Category[]   // Hierarchy (pre-defined)
  collections: Collection[] // Curated groups
  customFields: Record<string, any>
}
```

### 4.3 Search & Discovery

#### 4.3.1 Query Interface (F4.2)

**Advanced Search** (P13):

```
┌─ Search Bar (Global)
│  ├─ Full-text search
│  ├─ Filters (Type, Status, Author, Date)
│  ├─ Faceted search (Tags, Categories)
│  └─ Saved searches
│
└─ Search Results
   ├─ Relevance sorting
   ├─ Grid/List view toggle
   ├─ Preview on hover
   └─ Bulk actions
```

#### 4.3.2 Content Graph Explorer

Visual representation of content relationships:

```
Interactive Graph View:
- Nodes: Content items (sized by importance)
- Edges: Relationships (colored by type)
- Interactions:
  - Click node → View content
  - Drag → Reorganize
  - Filter → Show/hide types
  - Zoom → Detail levels
```

---

## 5. UI Component Specifications

### 5.1 Editor Components

#### 5.1.1 Rich Text Editor

**Core Features**:
- Block-based editing (like Notion/Gutenberg)
- WYSIWYG with markdown shortcuts
- Real-time preview
- Inline media embedding
- Code block with syntax highlighting
- Table editor
- AI writing assistance (P16)

**Architecture**:

```typescript
interface Editor {
  // State
  content: Block[]
  selection: Selection
  history: UndoStack
  
  // Operations (P30 - Command Pattern)
  executeCommand(cmd: EditorCommand): void
  undo(): void
  redo(): void
  
  // Real-time (F5)
  syncState: CollaborationState
  applyRemoteChange(change: Change): void
  
  // Validation (P11)
  validate(): ValidationResult
  
  // Plugins
  plugins: Plugin[]
}

type Block = 
  | { type: 'paragraph', content: RichText }
  | { type: 'heading', level: 1..6, content: RichText }
  | { type: 'image', src: string, alt: string, caption?: string }
  | { type: 'code', language: string, code: string }
  | { type: 'table', rows: TableRow[] }
  | { type: 'embed', url: string, provider: string }
  | { type: 'custom', component: string, props: any }
```

**UI Specification**:

```
┌─────────────────────────────────────────────────────────────┐
│ [← Back]  Blog Post Title                    [Save] [Publish]│
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  # Enter title here...                                       │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [+ Add block]                                       │   │
│  │                                                     │   │
│  │ Start writing or press '/' for commands...         │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  [+ Add block]  ← Hover to show insert options              │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│ Status Bar: ✓ Saved  |  1,234 words  |  ⚠ 2 suggestions     │
└─────────────────────────────────────────────────────────────┘
```

**Block Menu** (Slash commands):

```
Type '/' to trigger:
┌─────────────────────────┐
│ 🔤 Text               │
│   Paragraph            │
│   Heading 1-6          │
│   List (bullet/number) │
│   Quote                │
├─────────────────────────┤
│ 🎨 Media              │
│   Image                │
│   Video                │
│   Audio                │
│   File                 │
├─────────────────────────┤
│ 💻 Code               │
│   Code Block           │
│   Embed (URL)          │
│   HTML                 │
├─────────────────────────┤
│ 📊 Advanced           │
│   Table                │
│   Columns              │
│   Accordion            │
│   Custom Component     │
└─────────────────────────┘
```

#### 5.1.2 Media Library Component

**Features**:
- Grid/List view
- Drag-and-drop upload
- Bulk upload with progress (P28)
- Inline editing (crop, resize, filters)
- Metadata editing
- Collections/folders
- Search and filter

**UI Layout**:

```
┌─────────────────────────────────────────────────────────────┐
│ Media Library                        [Upload] [New Folder]  │
├──────────┬──────────────────────────────────────────────────┤
│          │ [Grid] [List]  Search: [___________]  Sort: [▼]  │
│ Folders  ├──────────────────────────────────────────────────┤
│ ├─ All   │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐           │
│ ├─ Images│  │      │ │      │ │      │ │      │           │
│ ├─ Videos│  │ IMG1 │ │ IMG2 │ │ IMG3 │ │ IMG4 │           │
│ ├─ Docs  │  │      │ │      │ │      │ │      │           │
│ └─ Recent│  └──────┘ └──────┘ └──────┘ └──────┘           │
│          │                                                   │
│ Tags     │  [Checkbox] Select All  [Delete] [Move] [Edit]   │
│ □ Logo   │                                                   │
│ □ Hero   │  Showing 1-20 of 245 items                       │
│ □ Icons  │  [1] 2 3 ... 13 [Next]                          │
└──────────┴──────────────────────────────────────────────────┘
```

**Upload Flow** (F1.2):

```
1. Drag & Drop or Click Upload
   ↓
2. File Selection (Multiple files supported)
   ↓
3. Upload Progress (P28 for each file)
   ┌──────────────────────────────┐
   │ Uploading 3 files...         │
   │ ▓▓▓▓▓▓▓▓▓▓░░░░░░ 60%        │
   │ image1.jpg - 1.2MB           │
   │ image2.jpg - 800KB           │
   │ image3.jpg - 2.1MB           │
   │ [Cancel Upload]              │
   └──────────────────────────────┘
   ↓
4. Auto-extract Metadata
   ↓
5. Show Toast (P27): "3 files uploaded successfully"
```

#### 5.1.3 Version History Panel (C5)

**UI Specification**:

```
┌─────────────────────────────────────────────────────────────┐
│ Version History                                    [✕ Close]│
├─────────────────────────────────────────────────────────────┤
│ Timeline View                 [Timeline] [Tree] [Compare]   │
│                                                               │
│  ● Now (Editing)                                             │
│  │                                                            │
│  ● 2 minutes ago - Auto-saved                               │
│  │ ├─ You: Added image to introduction                      │
│  │ └─ 234 chars added, 12 deleted                           │
│  │                                                            │
│  ● 15 minutes ago - Saved by Alex                           │
│  │ ├─ Alex: Updated heading structure                       │
│  │ └─ [View] [Restore]                                      │
│  │                                                            │
│  ● 1 hour ago - Published                                   │
│  │ ├─ You: Published version 1.2                            │
│  │ └─ 🏷️ Tag: v1.2-prod                                    │
│  │                                                            │
│  ● Yesterday - Major revision                               │
│    ├─ Sarah: Rewrote section 3                              │
│    └─ [View] [Restore] [Branch]                             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Diff View**:

```
Side-by-side comparison:
┌──────────────────────────┬──────────────────────────┐
│ Version 1.1 (Yesterday) │ Version 1.2 (Current)   │
├──────────────────────────┼──────────────────────────┤
│ # Introduction           │ # Introduction           │
│                          │                          │
│ This is the old text.    │ This is the new text.    │
│ ▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂     │ ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔     │
│ (removed line)           │                          │
│                          │ (new paragraph added)    │
│                          │ ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔     │
└──────────────────────────┴──────────────────────────┘
Legend: ▂ Removed  ▔ Added  ▦ Modified
```

### 5.2 Feedback Components

#### 5.2.1 Toast/Notification System (P27)

**Specifications**:

```typescript
type ToastType = 'info' | 'success' | 'warning' | 'error'

interface Toast {
  id: string
  type: ToastType
  message: string
  duration: number // milliseconds, 0 = manual dismiss
  action?: {
    label: string
    handler: () => void
  }
}
```

**Visual Design**:

```
Position: Top-right corner
Max Concurrent: 3 (queue others)
Animation: Slide in from right, fade out

┌────────────────────────────────────┐
│ ✓ Post published successfully      │
│   View post  [✕]                   │
└────────────────────────────────────┘
  ▓▓▓▓▓▓▓▓▓▓▓░░░░░░░  ← Auto-dismiss timer

Types:
┌────────────────────────────────────┐
│ ℹ Info notification                │
└────────────────────────────────────┘
┌────────────────────────────────────┐
│ ✓ Success notification             │
└────────────────────────────────────┘
┌────────────────────────────────────┐
│ ⚠ Warning notification             │
└────────────────────────────────────┘
┌────────────────────────────────────┐
│ ✕ Error notification               │
│   Try again  [✕]                   │
└────────────────────────────────────┘
```

**Usage Rules** (P.P27):
- Auto-dismiss: 3s (info), 4s (success), 5s (warning), manual (error)
- Non-blocking: Never modal, overlay only
- Type indication: Color + icon
- Actionable: Optional CTA button
- Queueing: Stack if >3, show sequentially

#### 5.2.2 Progress Indicator System (P28)

**Types**:

1. **Determinate Progress Bar**
```
Uploading file (45%)
▓▓▓▓▓▓▓▓▓░░░░░░░░░░░  45%
Est. 12s remaining
[Cancel]
```

2. **Indeterminate Spinner**
```
  ⟳  Processing...
```

3. **Skeleton Loader**
```
┌─────────────────────────────┐
│ ▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░  │
│ ▓▓▓▓░░░░░░░░░░░░░░░░░░░░░  │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░  │
└─────────────────────────────┘
```

**Properties** (P.P28):
- Accurate: Real progress, not fake
- Smooth: 60fps animation
- Cancellable: Always provide abort option
- Informative: Show ETA and current operation

#### 5.2.3 Status Bar/Indicator (P26)

**Bottom Status Bar**:

```
┌─────────────────────────────────────────────────────────────┐
│ ✓ Saved 2s ago  |  1,234 words  |  ⚠ 2 warnings  |  🌐 Online│
└─────────────────────────────────────────────────────────────┘
```

**Indicators**:
- Save status: Saving... / Saved / Error
- Word/character count
- Validation status
- Connection status
- Collaboration status (N users editing)

**Properties** (P.P26):
- Always visible: Fixed at bottom
- Non-intrusive: Small, unobtrusive
- Quick update: Real-time information

### 5.3 Navigation Components

#### 5.3.1 Command Palette (P2)

**Trigger**: ⌘K (Mac) / Ctrl+K (Windows)

**UI**:

```
┌─────────────────────────────────────────────────────────────┐
│  🔍 Type a command or search...                              │
├─────────────────────────────────────────────────────────────┤
│  Recent                                                       │
│  ├─ 📄 Edit "About Us" page                                  │
│  ├─ 🖼️  Open Media Library                                   │
│  └─ 👥 View Team Members                                     │
│                                                               │
│  Suggestions                                                  │
│  ├─ ✏️  Create new post                           ⌘N        │
│  ├─ 🚀 Publish changes                            ⌘⇧P       │
│  ├─ 🔍 Search all content                         ⌘/        │
│  └─ ⚙️  Open settings                             ⌘,        │
└─────────────────────────────────────────────────────────────┘
```

**Features**:
- Fuzzy search across all actions
- Keyboard shortcuts display
- Recent commands
- Contextual suggestions
- Quick navigation to any content

#### 5.3.2 Sidebar Navigation

**Collapsible Left Sidebar**:

```
┌──────────────────┐
│ 🏠 Dashboard     │ ← Active
├──────────────────┤
│ 📝 Content    ▼  │ ← Expanded
│   ├─ All         │
│   ├─ Pages       │
│   ├─ Posts       │
│   └─ Drafts (3)  │ ← Badge for count
├──────────────────┤
│ 🖼️  Media        │
├──────────────────┤
│ 🔗 Structure     │
├──────────────────┤
│ 👥 Users         │
├──────────────────┤
│ ⚙️  Settings     │
├──────────────────┤
│                  │
│ [◁ Collapse]     │ ← Toggle button
└──────────────────┘
```

**Collapsed State**:

```
┌──┐
│🏠│
├──┤
│📝│ ← Tooltip on hover
├──┤
│🖼️ │
├──┤
│🔗│
├──┤
│👥│
├──┤
│⚙️ │
├──┤
│  │
│▷ │
└──┘
```

### 5.4 Data Visualization Components

#### 5.4.1 Content Graph Visualizer

**Interactive Graph** (C1):

```
Canvas-based visualization:
- Force-directed layout
- Pan and zoom
- Hover for details
- Click to navigate
- Filter by type
- Highlight paths

Legend:
● Pages (blue)
● Posts (green)  
● Media (orange)
● External Links (gray)

Lines:
─── Parent-child (thick)
- - Reference (dashed)
••• Tag relationship (dotted)
```

#### 5.4.2 Analytics Dashboard

**Widgets**:

```
┌─────────────┬─────────────┬─────────────┐
│ Page Views  │ New Content │ Active Users│
│   12,345    │     45      │     12      │
│   +15% ↑    │    +2       │    -3 ↓     │
└─────────────┴─────────────┴─────────────┘

┌─────────────────────────────────────────┐
│ Content Performance (Last 30 days)      │
│                                          │
│  Page Views                              │
│  ▂▄▆█▅▇▆▄▃▅▆█▇▅▃▂▄▆▅▄▃▂▄▆█▇▅▄▃  │
│                                          │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Top Content                              │
│ 1. About Us        1,234 views   +12%   │
│ 2. Services        1,102 views   +8%    │
│ 3. Blog Post       892 views     +25%   │
└─────────────────────────────────────────┘
```

---

## 6. Interaction Patterns & Workflows

### 6.1 Core Workflows

#### 6.1.1 Quick Content Creation

**Flow**:

```
1. ⌘N (Quick create)
   ↓
2. Template picker modal
   ┌────────────────────────────────┐
   │ Create New Content             │
   │                                 │
   │ Templates:                      │
   │ [📄 Blank Page]                │
   │ [📝 Blog Post]                 │
   │ [📰 News Article]              │
   │ [🎨 Landing Page]              │
   │                                 │
   │ [Cancel]      [Start Writing] │
   └────────────────────────────────┘
   ↓
3. Editor opens with template
   ↓
4. Auto-save begins
   ↓
5. Real-time validation
```

#### 6.1.2 Bulk Operations

**Multi-select Actions**:

```
Content List with selections:
☑ [Page 1]     Modified 2 days ago    Sarah
☑ [Page 2]     Modified 1 week ago    Alex
☐ [Page 3]     Modified 1 month ago   You
☑ [Post 1]     Modified today         Sarah

Bulk Actions Bar (appears on selection):
┌─────────────────────────────────────────────────┐
│ 3 items selected                                │
│ [Publish] [Archive] [Delete] [Move] [Tag]      │
└─────────────────────────────────────────────────┘
```

#### 6.1.3 Drag-and-Drop Operations

**Supported Operations**:

1. **Reorder content blocks** (in editor)
   - Drag handle appears on hover
   - Drop zones highlight
   - Smooth animation

2. **Media upload** (anywhere)
   - Drop zone overlay on drag enter
   - Multiple file support
   - Progress for each file

3. **Content organization** (sidebar/tree view)
   - Drag pages to reorder
   - Drop on folder to move
   - Visual feedback

4. **Reference creation** (editor)
   - Drag content from sidebar to editor
   - Creates link or embed
   - Smart type detection

### 6.2 Validation & Error Handling

#### 6.2.1 Inline Validation (P11)

**Real-time Feedback**:

```
Editor with validation:

# Welcome to Our Site

This is a paragraph with a [broken link].
                         ~~~~~~~~~~~~
                         ⚠ Link target not found
                         [Fix] [Ignore]

![Missing alt text](image.jpg)
  ~~~~~~~~~~~~~~~~~~
  ⚠ Accessibility: Add alt text
  [Add Alt Text] [Learn More]

## Heading Level Skipped  ← H2 after H4
    ~~~~~~~~~~~~~~~~~~~~
    ℹ Skipped heading level (accessibility issue)
    [Fix Automatically] [Dismiss]
```

**Validation Levels**:

- 🔴 Error (blocking): Broken references, required fields missing
- 🟡 Warning (non-blocking): Accessibility issues, SEO suggestions  
- 🔵 Info: Best practice recommendations

#### 6.2.2 Error Recovery Flow (F6)

**Network Error**:

```
1. Detect connection loss
   ↓
2. Show toast: "Connection lost. Working offline."
   ↓
3. Queue changes locally (IndexedDB)
   ↓
4. Continue editing (optimistic UI)
   ↓
5. Reconnect detected
   ↓
6. Sync changes
   ┌────────────────────────────────┐
   │ Syncing changes...             │
   │ ▓▓▓▓▓▓▓▓░░░░░  65%           │
   │ 3 of 5 changes synced          │
   └────────────────────────────────┘
   ↓
7. Conflict detection
   ↓
8. IF conflict → Show resolution UI
   ELSE → Success toast
```

**Conflict Resolution UI**:

```
┌─────────────────────────────────────────────────────────┐
│ Merge Conflict Detected                                  │
├─────────────────────────────────────────────────────────┤
│ Your changes conflict with Alex's recent edit.          │
│                                                           │
│ Your Version:              Alex's Version:               │
│ "Hello world"              "Hello there"                 │
│                                                           │
│ [Keep Mine] [Keep Theirs] [Merge Both] [View Diff]      │
└─────────────────────────────────────────────────────────┘
```

### 6.3 Keyboard Shortcuts

**Global Shortcuts**:

```
⌘K / Ctrl+K       Command palette
⌘N / Ctrl+N       New content
⌘S / Ctrl+S       Save
⌘/ / Ctrl+/       Search
⌘, / Ctrl+,       Settings
⌘Z / Ctrl+Z       Undo
⌘⇧Z / Ctrl+Y      Redo
Esc               Close modal/cancel
```

**Editor Shortcuts**:

```
⌘B / Ctrl+B       Bold
⌘I / Ctrl+I       Italic
⌘K / Ctrl+K       Insert link
⌘⌥1-6 / Ctrl+Alt+1-6   Heading level
⌘⇧7 / Ctrl+Shift+7     Numbered list
⌘⇧8 / Ctrl+Shift+8     Bullet list
⌘⇧E / Ctrl+Shift+E     Code block
/                  Block menu
```

**Navigation Shortcuts**:

```
G then H          Go to home/dashboard
G then C          Go to content
G then M          Go to media
G then S          Go to settings
```

### 6.4 Responsive Behaviors

#### 6.4.1 Desktop (1920px+)

```
┌─────────────────────────────────────────────────────────────┐
│ [Logo] Navigation                    [Search] [🔔] [@User]  │
├────────┬─────────────────────────────────────────┬──────────┤
│        │                                          │          │
│ Side   │         Main Content Area               │ Context  │
│ Nav    │                                          │ Panel    │
│        │                                          │          │
│ (240px)│              (flexible)                  │ (320px)  │
│        │                                          │          │
│        │                                          │          │
└────────┴─────────────────────────────────────────┴──────────┘
```

#### 6.4.2 Tablet (768px - 1024px)

```
┌─────────────────────────────────────┐
│ [☰] Logo         [Search] [🔔] [@] │
├─────────────────────────────────────┤
│                                      │
│         Main Content Area            │
│          (full width)                │
│                                      │
│  Sidebar: Off-canvas (hamburger)    │
│  Context: Bottom sheet or hidden    │
│                                      │
└─────────────────────────────────────┘
```

#### 6.4.3 Mobile (< 768px)

```
┌──────────────────────┐
│ [☰]  Logo      [@]   │
├──────────────────────┤
│                      │
│   Main Content       │
│   (full width)       │
│                      │
│   Simplified UI      │
│   Touch-optimized    │
│                      │
├──────────────────────┤
│  [Home] [+] [Search] │
└──────────────────────┘
Bottom Tab Bar
```

**Mobile Optimizations**:
- Touch targets ≥ 44px
- Simplified navigation
- Swipe gestures
- Native-like interactions
- Optimistic UI updates
- Offline support

---

## 7. Visual Design System

### 7.1 Design Tokens

#### 7.1.1 Color System

**Primary Colors**:

```css
/* Brand Colors */
--color-primary-50:  #F0F9FF;   /* Lightest */
--color-primary-100: #E0F2FE;
--color-primary-200: #BAE6FD;
--color-primary-300: #7DD3FC;
--color-primary-400: #38BDF8;
--color-primary-500: #0EA5E9;   /* Primary */
--color-primary-600: #0284C7;
--color-primary-700: #0369A1;
--color-primary-800: #075985;
--color-primary-900: #0C4A6E;   /* Darkest */

/* Semantic Colors */
--color-success: #10B981;   /* Green */
--color-warning: #F59E0B;   /* Amber */
--color-error: #EF4444;     /* Red */
--color-info: #3B82F6;      /* Blue */

/* Neutral Colors */
--color-gray-50:  #F9FAFB;
--color-gray-100: #F3F4F6;
--color-gray-200: #E5E7EB;
--color-gray-300: #D1D5DB;
--color-gray-400: #9CA3AF;
--color-gray-500: #6B7280;
--color-gray-600: #4B5563;
--color-gray-700: #374151;
--color-gray-800: #1F2937;
--color-gray-900: #111827;
```

**Usage**:

```
Backgrounds:
- Primary: --color-gray-50 (light mode), --color-gray-900 (dark mode)
- Secondary: --color-gray-100 / --color-gray-800
- Elevated (cards): white / --color-gray-800

Text:
- Primary: --color-gray-900 / --color-gray-50
- Secondary: --color-gray-600 / --color-gray-400
- Tertiary: --color-gray-500 / --color-gray-500

Borders:
- Default: --color-gray-200 / --color-gray-700
- Strong: --color-gray-300 / --color-gray-600

Interactive:
- Default: --color-primary-500
- Hover: --color-primary-600
- Active: --color-primary-700
- Disabled: --color-gray-300 / --color-gray-700
```

#### 7.1.2 Typography

**Font Families**:

```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'Fira Code', 'Monaco', 'Courier New', monospace;
```

**Type Scale**:

```css
--text-xs:   0.75rem;   /* 12px */
--text-sm:   0.875rem;  /* 14px */
--text-base: 1rem;      /* 16px */
--text-lg:   1.125rem;  /* 18px */
--text-xl:   1.25rem;   /* 20px */
--text-2xl:  1.5rem;    /* 24px */
--text-3xl:  1.875rem;  /* 30px */
--text-4xl:  2.25rem;   /* 36px */
--text-5xl:  3rem;      /* 48px */
```

**Font Weights**:

```css
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

**Line Heights**:

```css
--leading-tight: 1.25;    /* Headings */
--leading-normal: 1.5;    /* Body text */
--leading-relaxed: 1.75;  /* Long-form content */
```

#### 7.1.3 Spacing System

**Base Unit**: 4px (0.25rem)

```css
--space-0: 0;
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
--space-24: 6rem;     /* 96px */
```

**Component Spacing**:

```
Button padding: --space-3 --space-6  (12px 24px)
Input padding: --space-3 --space-4   (12px 16px)
Card padding: --space-6              (24px)
Section margin: --space-12           (48px)
```

#### 7.1.4 Shadows & Elevation

```css
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
--shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
```

**Usage**:

```
Elevation 0: No shadow (inline elements)
Elevation 1: --shadow-sm (buttons, inputs)
Elevation 2: --shadow-md (cards, dropdowns)
Elevation 3: --shadow-lg (modals, popovers)
Elevation 4: --shadow-xl (command palette)
Elevation 5: --shadow-2xl (notifications overlay)
```

#### 7.1.5 Border Radius

```css
--radius-none: 0;
--radius-sm: 0.25rem;   /* 4px - buttons, inputs */
--radius-md: 0.5rem;    /* 8px - cards */
--radius-lg: 0.75rem;   /* 12px - modals */
--radius-xl: 1rem;      /* 16px - images */
--radius-2xl: 1.5rem;   /* 24px - special cards */
--radius-full: 9999px;  /* Pills, avatars */
```

#### 7.1.6 Animation & Transitions

```css
/* Durations */
--duration-fast: 150ms;
--duration-normal: 250ms;
--duration-slow: 350ms;

/* Easing Functions */
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);

/* Common Transitions */
--transition-base: all var(--duration-normal) var(--ease-in-out);
--transition-colors: color, background-color, border-color var(--duration-fast) var(--ease-in-out);
--transition-transform: transform var(--duration-normal) var(--ease-out);
```

**Animation Guidelines**:
- Micro-interactions: 150ms (hover, focus)
- UI transitions: 250ms (modals, dropdowns)
- Page transitions: 350ms (navigation)
- Reduce motion for accessibility (prefers-reduced-motion)

### 7.2 Component Styles

#### 7.2.1 Buttons

**Variants**:

```
Primary (Filled):
┌────────────────┐
│  Save Changes  │  ← bg: primary-500, text: white
└────────────────┘

Secondary (Outlined):
┌────────────────┐
│    Cancel      │  ← border: gray-300, text: gray-700
└────────────────┘

Ghost (Text only):
Learn More →        ← text: primary-500, no bg/border

Danger (Destructive):
┌────────────────┐
│     Delete     │  ← bg: error-500, text: white
└────────────────┘
```

**States**:

```css
.button {
  /* Default */
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-md);
  font-weight: var(--font-medium);
  transition: var(--transition-colors);
}

.button-primary {
  background: var(--color-primary-500);
  color: white;
}

.button-primary:hover {
  background: var(--color-primary-600);
}

.button-primary:active {
  background: var(--color-primary-700);
  transform: translateY(1px);
}

.button-primary:disabled {
  background: var(--color-gray-300);
  cursor: not-allowed;
  opacity: 0.6;
}

.button-primary:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}
```

**Sizes**:

```
Small:  py-2 px-4  text-sm   (8px 16px, 14px text)
Medium: py-3 px-6  text-base (12px 24px, 16px text)
Large:  py-4 px-8  text-lg   (16px 32px, 18px text)
```

#### 7.2.2 Form Inputs

**Text Input**:

```css
.input {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--color-gray-300);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  transition: var(--transition-colors);
}

.input:focus {
  outline: none;
  border-color: var(--color-primary-500);
  ring: 2px var(--color-primary-100);
}

.input:disabled {
  background: var(--color-gray-100);
  cursor: not-allowed;
}

.input.error {
  border-color: var(--color-error);
}

.input.success {
  border-color: var(--color-success);
}
```

**Visual States**:

```
Default:
┌─────────────────────────────────┐
│ Enter text...                   │
└─────────────────────────────────┘

Focus:
┌─────────────────────────────────┐
│ Typing text...|                 │  ← Blue border + ring
└─────────────────────────────────┘

Error:
┌─────────────────────────────────┐
│ Invalid email                   │  ← Red border
└─────────────────────────────────┘
⚠ Please enter a valid email

Success:
┌─────────────────────────────────┐
│ user@example.com          ✓     │  ← Green border + checkmark
└─────────────────────────────────┘

Disabled:
┌─────────────────────────────────┐
│ Cannot edit                     │  ← Gray background
└─────────────────────────────────┘
```

#### 7.2.3 Cards

```css
.card {
  background: white;
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
  transition: var(--transition-base);
}

.card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.card-interactive {
  cursor: pointer;
}

.card-interactive:hover {
  border-color: var(--color-primary-300);
}
```

#### 7.2.4 Modals

```css
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1000;
}

.modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-2xl);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow: auto;
  z-index: 1001;
}

.modal-header {
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-gray-200);
}

.modal-body {
  padding: var(--space-6);
}

.modal-footer {
  padding: var(--space-6);
  border-top: 1px solid var(--color-gray-200);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
}
```

**Modal Sizes**:

```
Small:  max-width: 400px   (confirmations)
Medium: max-width: 600px   (forms)
Large:  max-width: 800px   (content previews)
Full:   max-width: 95vw    (editors)
```

### 7.3 Dark Mode

**Color Adjustments**:

```css
@media (prefers-color-scheme: dark) {
  :root {
    /* Backgrounds */
    --bg-primary: var(--color-gray-900);
    --bg-secondary: var(--color-gray-800);
    --bg-elevated: var(--color-gray-800);
    
    /* Text */
    --text-primary: var(--color-gray-50);
    --text-secondary: var(--color-gray-400);
    
    /* Borders */
    --border-default: var(--color-gray-700);
    
    /* Shadows (enhanced for dark mode) */
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.3);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.5);
  }
}
```

**Dark Mode Principles**:
1. Reduce pure black (#000) → Use dark gray (gray-900)
2. Reduce contrast (89% vs 100%)
3. Enhance shadows for depth
4. Adjust saturations (slightly desaturate colors)
5. Provide manual toggle (don't rely only on system preference)

---

## 8. Technical Implementation Guidelines

### 8.1 Frontend Architecture

**Tech Stack**:

```
Framework: React 18+ with TypeScript
State: Zustand + React Query
Routing: React Router v6
Styling: Tailwind CSS + CSS Modules
Editor: Lexical (Facebook's editor framework)
Real-time: WebSocket + operational transform
Build: Vite
Testing: Vitest + React Testing Library
```

**Project Structure**:

```
src/
├── app/
│   ├── layouts/           # Layout components
│   ├── pages/             # Route pages
│   └── routes.tsx         # Route configuration
├── features/
│   ├── editor/            # Editor feature
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── store/
│   │   └── utils/
│   ├── media/             # Media library feature
│   ├── collaboration/     # Real-time collab
│   └── ...
├── shared/
│   ├── components/        # Shared UI components
│   ├── hooks/             # Shared hooks
│   ├── utils/             # Utilities
│   ├── types/             # TypeScript types
│   └── constants/         # Constants
├── services/
│   ├── api/               # API client
│   ├── validation/        # Validation (P11)
│   └── parser/            # Parser (P10)
└── styles/
    ├── tokens.css         # Design tokens
    └── globals.css        # Global styles
```

### 8.2 State Management

**Pattern**: Feature-based stores

```typescript
// Editor store (Zustand)
interface EditorStore {
  // State
  content: Block[]
  selection: Selection
  history: {
    past: Block[][]
    future: Block[][]
  }
  
  // Actions (Command Pattern - P30)
  executeCommand: (cmd: Command) => Promise<void>
  undo: () => void
  redo: () => void
  updateContent: (content: Block[]) => void
  
  // Validation (P11)
  validationErrors: ValidationError[]
  validate: () => Promise<ValidationResult>
  
  // Collaboration (F5)
  collaborators: Collaborator[]
  applyRemoteChange: (change: Change) => void
}

const useEditorStore = create<EditorStore>((set, get) => ({
  content: [],
  selection: null,
  history: { past: [], future: [] },
  
  executeCommand: async (cmd) => {
    const result = await cmd.execute()
    if (result.success) {
      set(state => ({
        content: result.content,
        history: {
          past: [...state.history.past, state.content],
          future: []
        }
      }))
    }
  },
  
  undo: () => {
    const { history, content } = get()
    if (history.past.length === 0) return
    
    const previous = history.past[history.past.length - 1]
    set({
      content: previous,
      history: {
        past: history.past.slice(0, -1),
        future: [content, ...history.future]
      }
    })
  },
  
  // ... other actions
}))
```

**Server State**: React Query

```typescript
// Fetch content with caching
const useContent = (id: string) => {
  return useQuery({
    queryKey: ['content', id],
    queryFn: () => api.content.get(id),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Mutation with optimistic updates
const useUpdateContent = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: UpdateContentDto) => api.content.update(data),
    onMutate: async (newData) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries(['content', newData.id])
      
      // Snapshot previous value
      const previous = queryClient.getQueryData(['content', newData.id])
      
      // Optimistically update
      queryClient.setQueryData(['content', newData.id], newData)
      
      return { previous }
    },
    onError: (err, newData, context) => {
      // Rollback on error
      queryClient.setQueryData(['content', newData.id], context.previous)
    },
    onSettled: (data, error, variables) => {
      // Refetch
      queryClient.invalidateQueries(['content', variables.id])
    }
  })
}
```

### 8.3 Real-Time Collaboration (F5)

**Operational Transform Implementation**:

```typescript
interface Operation {
  type: 'insert' | 'delete' | 'retain'
  position: number
  content?: string
  length?: number
}

class OTEngine {
  // Transform operation against another
  transform(op1: Operation, op2: Operation): Operation {
    // Operational Transform logic
    // Handle concurrent edits
  }
  
  // Apply operation to document
  apply(doc: Block[], op: Operation): Block[] {
    // Apply transformation
  }
  
  // Compose operations
  compose(op1: Operation, op2: Operation): Operation {
    // Combine operations
  }
}

// WebSocket integration
class CollaborationService {
  private ws: WebSocket
  private otEngine: OTEngine
  private pendingOps: Operation[] = []
  private revision: number = 0
  
  connect(documentId: string) {
    this.ws = new WebSocket(`wss://api.cms.com/collab/${documentId}`)
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      
      switch (message.type) {
        case 'operation':
          this.handleRemoteOperation(message.operation)
          break
        case 'cursor':
          this.handleCursorUpdate(message.cursor)
          break
        case 'presence':
          this.handlePresenceUpdate(message.presence)
          break
      }
    }
  }
  
  sendOperation(op: Operation) {
    this.ws.send(JSON.stringify({
      type: 'operation',
      operation: op,
      revision: this.revision
    }))
    
    this.pendingOps.push(op)
  }
  
  handleRemoteOperation(remoteOp: Operation) {
    // Transform pending operations
    let transformedRemote = remoteOp
    
    for (const pending of this.pendingOps) {
      transformedRemote = this.otEngine.transform(transformedRemote, pending)
    }
    
    // Apply to local document
    const newContent = this.otEngine.apply(
      editorStore.getState().content,
      transformedRemote
    )
    
    editorStore.getState().updateContent(newContent)
    this.revision++
  }
}
```

### 8.4 Validation System (P11)

**Multi-level Validation**:

```typescript
// Validation pipeline
class ValidationPipeline {
  private validators: Validator[] = []
  
  addValidator(validator: Validator) {
    this.validators.push(validator)
  }
  
  async validate(content: Content): Promise<ValidationResult> {
    const errors: ValidationError[] = []
    const warnings: ValidationWarning[] = []
    const suggestions: ValidationSuggestion[] = []
    
    for (const validator of this.validators) {
      const result = await validator.validate(content)
      
      errors.push(...result.errors)
      warnings.push(...result.warnings)
      suggestions.push(...result.suggestions)
    }
    
    return {
      valid: errors.length === 0,
      errors,
      warnings,
      suggestions
    }
  }
}

// Example validators
class LinkValidator implements Validator {
  async validate(content: Content): Promise<ValidationResult> {
    const errors: ValidationError[] = []
    
    // Find all links
    const links = this.extractLinks(content)
    
    for (const link of links) {
      // Check if internal link exists
      if (link.type === 'internal') {
        const exists = await api.content.exists(link.target)
        if (!exists) {
          errors.push({
            type: 'broken-link',
            severity: 'error',
            message: `Link target not found: ${link.target}`,
            position: link.position,
            fix: {
              label: 'Remove link',
              action: () => this.removeLink(link)
            }
          })
        }
      }
      
      // Check external links
      if (link.type === 'external') {
        try {
          await fetch(link.url, { method: 'HEAD' })
        } catch {
          errors.push({
            type: 'broken-link',
            severity: 'warning',
            message: `External link may be broken: ${link.url}`,
            position: link.position
          })
        }
      }
    }
    
    return { errors, warnings: [], suggestions: [] }
  }
}

class AccessibilityValidator implements Validator {
  async validate(content: Content): Promise<ValidationResult> {
    const warnings: ValidationWarning[] = []
    const suggestions: ValidationSuggestion[] = []
    
    // Check images have alt text
    const images = this.extractImages(content)
    for (const image of images) {
      if (!image.alt) {
        warnings.push({
          type: 'missing-alt-text',
          severity: 'warning',
          message: 'Image missing alt text',
          position: image.position,
          fix: {
            label: 'Add alt text',
            action: () => this.promptForAltText(image)
          }
        })
      }
    }
    
    // Check heading hierarchy
    const headings = this.extractHeadings(content)
    const hierarchy = this.checkHeadingHierarchy(headings)
    if (!hierarchy.valid) {
      warnings.push({
        type: 'heading-hierarchy',
        severity: 'info',
        message: 'Heading levels should not skip',
        position: hierarchy.position,
        fix: {
          label: 'Fix automatically',
          action: () => this.fixHeadingHierarchy(headings)
        }
      })
    }
    
    return { errors: [], warnings, suggestions }
  }
}
```

### 8.5 Parser Pipeline (P10)

**Content Transformation**:

```typescript
// Lexer: Tokenize input
class Lexer {
  tokenize(input: string): Token[] {
    const tokens: Token[] = []
    let position = 0
    
    while (position < input.length) {
      // Match patterns
      if (this.matchHeading(input, position)) {
        tokens.push(this.consumeHeading(input, position))
      } else if (this.matchLink(input, position)) {
        tokens.push(this.consumeLink(input, position))
      } // ... other patterns
      
      position++
    }
    
    return tokens
  }
}

// Parser: Build AST
class Parser {
  parse(tokens: Token[]): AST {
    const root: ASTNode = { type: 'root', children: [] }
    let current = 0
    
    while (current < tokens.length) {
      const node = this.parseNode(tokens, current)
      root.children.push(node)
      current = node.end
    }
    
    return root
  }
  
  parseNode(tokens: Token[], start: number): ASTNode {
    const token = tokens[start]
    
    switch (token.type) {
      case 'heading':
        return this.parseHeading(tokens, start)
      case 'paragraph':
        return this.parseParagraph(tokens, start)
      case 'list':
        return this.parseList(tokens, start)
      // ... other node types
    }
  }
}

// Transformer: Apply plugins
class Transformer {
  private plugins: Plugin[] = []
  
  addPlugin(plugin: Plugin) {
    this.plugins.push(plugin)
  }
  
  transform(ast: AST): AST {
    let transformed = ast
    
    for (const plugin of this.plugins) {
      transformed = plugin.transform(transformed)
    }
    
    return transformed
  }
}

// Renderer: Generate output
class Renderer {
  render(ast: AST, format: 'html' | 'markdown' | 'json'): string {
    switch (format) {
      case 'html':
        return this.renderHTML(ast)
      case 'markdown':
        return this.renderMarkdown(ast)
      case 'json':
        return JSON.stringify(ast, null, 2)
    }
  }
  
  renderHTML(node: ASTNode): string {
    switch (node.type) {
      case 'heading':
        return `<h${node.level}>${this.renderChildren(node.children)}</h${node.level}>`
      case 'paragraph':
        return `<p>${this.renderChildren(node.children)}</p>`
      case 'link':
        return `<a href="${node.url}">${this.renderChildren(node.children)}</a>`
      // ... other nodes
    }
  }
}

// Complete pipeline
class ContentPipeline {
  private lexer = new Lexer()
  private parser = new Parser()
  private transformer = new Transformer()
  private renderer = new Renderer()
  
  async process(input: string, format: 'html' | 'markdown' | 'json'): Promise<string> {
    // 1. Tokenize
    const tokens = this.lexer.tokenize(input)
    
    // 2. Parse
    const ast = this.parser.parse(tokens)
    
    // 3. Transform
    const transformed = this.transformer.transform(ast)
    
    // 4. Validate
    const validation = await validator.validate(transformed)
    if (!validation.valid) {
      throw new ValidationError(validation.errors)
    }
    
    // 5. Render
    return this.renderer.render(transformed, format)
  }
}
```

### 8.6 Search & Indexing (P13)

**Indexer Implementation**:

```typescript
// Search index
interface SearchIndex {
  addDocument(doc: Document): Promise<void>
  updateDocument(doc: Document): Promise<void>
  removeDocument(id: string): Promise<void>
  search(query: SearchQuery): Promise<SearchResults>
}

// Meilisearch integration
class SearchService implements SearchIndex {
  private client: MeiliSearch
  private indexName = 'content'
  
  constructor() {
    this.client = new MeiliSearch({
      host: 'http://localhost:7700',
      apiKey: process.env.MEILISEARCH_KEY
    })
    
    this.setupIndex()
  }
  
  private async setupIndex() {
    const index = this.client.index(this.indexName)
    
    // Configure searchable attributes
    await index.updateSearchableAttributes([
      'title',
      'content',
      'tags',
      'author'
    ])
    
    // Configure filterable attributes
    await index.updateFilterableAttributes([
      'type',
      'status',
      'author',
      'created_at',
      'updated_at'
    ])
    
    // Configure sortable attributes
    await index.updateSortableAttributes([
      'created_at',
      'updated_at',
      'title'
    ])
  }
  
  async addDocument(doc: Document): Promise<void> {
    const index = this.client.index(this.indexName)
    
    await index.addDocuments([{
      id: doc.id,
      title: doc.title,
      content: this.extractText(doc.content),
      type: doc.type,
      status: doc.status,
      author: doc.author.name,
      tags: doc.tags,
      created_at: doc.createdAt.getTime(),
      updated_at: doc.updatedAt.getTime()
    }])
  }
  
  async search(query: SearchQuery): Promise<SearchResults> {
    const index = this.client.index(this.indexName)
    
    // Build filter
    const filters = []
    if (query.type) filters.push(`type = ${query.type}`)
    if (query.status) filters.push(`status = ${query.status}`)
    if (query.author) filters.push(`author = ${query.author}`)
    
    // Search
    const results = await index.search(query.text, {
      filter: filters.join(' AND '),
      sort: query.sort ? [`${query.sort.field}:${query.sort.order}`] : undefined,
      limit: query.limit || 20,
      offset: query.offset || 0,
      attributesToHighlight: ['title', 'content'],
      highlightPreTag: '<mark>',
      highlightPostTag: '</mark>'
    })
    
    return {
      hits: results.hits.map(hit => ({
        id: hit.id,
        title: hit.title,
        excerpt: hit._formatted.content,
        type: hit.type,
        url: `/content/${hit.id}`
      })),
      total: results.estimatedTotalHits,
      processingTime: results.processingTimeMs
    }
  }
}
```

### 8.7 Performance Optimizations

**Code Splitting**:

```typescript
// Lazy load routes
const DashboardPage = lazy(() => import('./pages/Dashboard'))
const EditorPage = lazy(() => import('./pages/Editor'))
const MediaPage = lazy(() => import('./pages/Media'))

// Route configuration
const routes = [
  {
    path: '/',
    element: <Suspense fallback={<LoadingSpinner />}>
      <DashboardPage />
    </Suspense>
  },
  {
    path: '/editor/:id',
    element: <Suspense fallback={<EditorSkeleton />}>
      <EditorPage />
    </Suspense>
  }
]
```

**Virtual Scrolling**:

```typescript
// For large lists (media library, content list)
import { useVirtualizer } from '@tanstack/react-virtual'

function ContentList({ items }: { items: Content[] }) {
  const parentRef = useRef<HTMLDivElement>(null)
  
  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 80, // Item height
    overscan: 5 // Render extra items
  })
  
  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
        {virtualizer.getVirtualItems().map(virtualRow => (
          <ContentItem
            key={items[virtualRow.index].id}
            content={items[virtualRow.index]}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualRow.size}px`,
              transform: `translateY(${virtualRow.start}px)`
            }}
          />
        ))}
      </div>
    </div>
  )
}
```

**Debouncing & Throttling**:

```typescript
// Debounce search input
const debouncedSearch = useDebouncedCallback(
  (query: string) => {
    searchService.search({ text: query })
  },
  500 // Wait 500ms after user stops typing
)

// Throttle auto-save
const throttledSave = useThrottledCallback(
  (content: Content) => {
    api.content.save(content)
  },
  5000 // Save at most every 5 seconds
)
```

### 8.8 Backend API Design

**RESTful Endpoints**:

```
Content:
GET    /api/content              List content (with filters)
POST   /api/content              Create content
GET    /api/content/:id          Get content
PUT    /api/content/:id          Update content
DELETE /api/content/:id          Delete content
GET    /api/content/:id/versions Get version history

Media:
GET    /api/media                List media
POST   /api/media/upload         Upload media
GET    /api/media/:id            Get media
PUT    /api/media/:id            Update metadata
DELETE /api/media/:id            Delete media

Search:
GET    /api/search               Search content
POST   /api/search/reindex       Reindex content

Collaboration:
WebSocket /ws/collab/:documentId Real-time editing

Users:
GET    /api/users                List users
POST   /api/users                Create user
GET    /api/users/:id            Get user
PUT    /api/users/:id            Update user

Settings:
GET    /api/settings             Get settings
PUT    /api/settings             Update settings
```

**GraphQL Alternative**:

```graphql
type Query {
  content(id: ID!): Content
  contents(
    filter: ContentFilter
    sort: SortInput
    pagination: PaginationInput
  ): ContentConnection
  
  media(id: ID!): Media
  mediaItems(filter: MediaFilter): [Media!]!
  
  search(query: String!, filters: SearchFilters): SearchResults
}

type Mutation {
  createContent(input: CreateContentInput!): Content!
  updateContent(id: ID!, input: UpdateContentInput!): Content!
  deleteContent(id: ID!): Boolean!
  
  uploadMedia(file: Upload!): Media!
  updateMedia(id: ID!, input: UpdateMediaInput!): Media!
  
  publish(id: ID!): Content!
  unpublish(id: ID!): Content!
}

type Subscription {
  contentUpdated(id: ID!): Content!
  collaboratorJoined(documentId: ID!): Collaborator!
  collaboratorLeft(documentId: ID!): Collaborator!
}

type Content {
  id: ID!
  title: String!
  content: JSON!
  type: ContentType!
  status: ContentStatus!
  author: User!
  versions: [Version!]!
  metadata: JSON
  createdAt: DateTime!
  updatedAt: DateTime!
}
```

---

## 9. Accessibility & Performance

### 9.1 Accessibility (WCAG 2.1 AA)

#### 9.1.1 Keyboard Navigation

**Focus Management**:

```typescript
// Trap focus in modals
function Modal({ isOpen, onClose, children }) {
  const modalRef = useRef<HTMLDivElement>(null)
  
  useEffect(() => {
    if (!isOpen) return
    
    const focusableElements = modalRef.current?.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    
    if (!focusableElements?.length) return
    
    const firstElement = focusableElements[0] as HTMLElement
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement
    
    firstElement.focus()
    
    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return
      
      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement.focus()
          e.preventDefault()
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement.focus()
          e.preventDefault()
        }
      }
    }
    
    document.addEventListener('keydown', handleTab)
    return () => document.removeEventListener('keydown', handleTab)
  }, [isOpen])
  
  return (
    <div
      ref={modalRef}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      {children}
    </div>
  )
}
```

**Skip Links**:

```html
<a href="#main-content" class="skip-link">
  Skip to main content
</a>

<style>
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--color-primary-500);
  color: white;
  padding: 8px;
  text-decoration: none;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
</style>
```

#### 9.1.2 Screen Reader Support

**ARIA Labels**:

```html
<!-- Buttons -->
<button aria-label="Save document">
  <SaveIcon />
</button>

<!-- Status updates -->
<div role="status" aria-live="polite">
  Document saved successfully
</div>

<!-- Form fields -->
<label for="title">Title</label>
<input
  id="title"
  type="text"
  aria-required="true"
  aria-invalid={hasError}
  aria-describedby="title-error"
/>
{hasError && (
  <span id="title-error" role="alert">
    Title is required
  </span>
)}

<!-- Loading states -->
<div role="status" aria-live="polite" aria-busy="true">
  <span class="sr-only">Loading content...</span>
  <Spinner />
</div>
```

**Screen Reader Only Content**:

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

#### 9.1.3 Color Contrast

**Minimum Ratios**:
- Normal text: 4.5:1
- Large text (18pt+): 3:1
- UI components: 3:1

**Validation**:

```typescript
function checkContrast(foreground: string, background: string): boolean {
  const ratio = calculateContrastRatio(foreground, background)
  return ratio >= 4.5 // WCAG AA for normal text
}

// Automatically adjust colors if contrast is insufficient
function ensureContrast(fg: string, bg: string): string {
  if (checkContrast(fg, bg)) return fg
  
  // Darken or lighten foreground until contrast is sufficient
  return adjustColorForContrast(fg, bg, 4.5)
}
```

### 9.2 Performance Targets

#### 9.2.1 Core Web Vitals

**Targets**:
- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms
- **CLS (Cumulative Layout Shift)**: < 0.1

**Optimization Strategies**:

```typescript
// Lazy load images
<img
  src={image.url}
  loading="lazy"
  decoding="async"
  width={image.width}
  height={image.height}
  alt={image.alt}
/>

// Preload critical resources
<link rel="preload" href="/fonts/inter.woff2" as="font" crossorigin />

// Code splitting
const HeavyComponent = lazy(() => import('./HeavyComponent'))

// Prefetch on hover
<Link
  to="/editor"
  onMouseEnter={() => {
    import('./pages/Editor')
  }}
>
  Open Editor
</Link>
```

#### 9.2.2 Bundle Size

**Targets**:
- Initial bundle: < 200 KB (gzipped)
- Lazy chunks: < 50 KB each
- Total JS: < 1 MB

**Analysis**:

```bash
# Analyze bundle
npm run build -- --analyze

# Check bundle size
bundlesize:
  - path: "./dist/*.js"
    maxSize: "200 KB"
```

#### 9.2.3 Runtime Performance

**Metrics**:
- Time to Interactive: < 3.5s
- Interaction to Next Paint: < 200ms
- API Response Time: < 300ms (p95)

**Monitoring**:

```typescript
// Performance monitoring
class PerformanceMonitor {
  measureInteraction(name: string, fn: () => void) {
    const start = performance.now()
    
    fn()
    
    requestAnimationFrame(() => {
      const duration = performance.now() - start
      
      this.report({
        metric: 'interaction',
        name,
        duration,
        timestamp: Date.now()
      })
      
      if (duration > 200) {
        console.warn(`Slow interaction: ${name} took ${duration}ms`)
      }
    })
  }
  
  measureAPI(endpoint: string, duration: number) {
    this.report({
      metric: 'api',
      endpoint,
      duration,
      timestamp: Date.now()
    })
  }
}
```

---

## 10. Future Enhancements

### 10.1 Phase 2 Features

#### 10.1.1 AI-Powered Features (P16)

**Content Generation**:
- AI writing assistant
- Auto-generate summaries
- SEO optimization suggestions
- Content improvement recommendations

**Smart Features**:
- Automatic tagging
- Related content suggestions
- Image alt text generation
- Accessibility fixes

#### 10.1.2 Advanced Collaboration

**Real-time Features**:
- Video/audio calls in editor
- Inline commenting with threads
- Mention notifications (@user)
- Collaborative cursors with names

**Workflow Management**:
- Approval workflows
- Content review process
- Editorial calendar
- Task assignments

#### 10.1.3 Multi-Site Management

**Features**:
- Manage multiple sites from one dashboard
- Shared content library
- Cross-site publishing
- White-label options

### 10.2 Phase 3 Features

#### 10.2.1 Marketplace

**Plugin System**:
- Third-party plugin marketplace
- Custom field types
- Custom blocks
- Integration connectors

#### 10.2.2 Advanced Analytics

**Features**:
- Content performance analytics
- A/B testing
- Heatmaps
- User journey tracking

#### 10.2.3 Headless CMS API

**Features**:
- GraphQL API
- Content delivery API
- Webhooks
- SDK for popular frameworks

---

## Appendix

### A. Design Checklist

**Before Development**:
- [ ] User flows documented
- [ ] Wireframes approved
- [ ] Design system tokens defined
- [ ] Component library started
- [ ] Accessibility audit planned

**During Development**:
- [ ] Design tokens implemented
- [ ] Components match designs
- [ ] Responsive breakpoints tested
- [ ] Keyboard navigation works
- [ ] Screen reader tested

**Before Launch**:
- [ ] WCAG 2.1 AA compliance verified
- [ ] Performance targets met
- [ ] Cross-browser testing complete
- [ ] User testing completed
- [ ] Documentation finished

### B. Resources

**Design Tools**:
- Figma: [figma.com](https://figma.com)
- Contrast Checker: [webaim.org/resources/contrastchecker/](https://webaim.org/resources/contrastchecker/)
- WAVE: [wave.webaim.org](https://wave.webaim.org)

**Development**:
- React: [react.dev](https://react.dev)
- TypeScript: [typescriptlang.org](https://typescriptlang.org)
- Tailwind CSS: [tailwindcss.com](https://tailwindcss.com)
- Lexical: [lexical.dev](https://lexical.dev)

**References**:
- WCAG 2.1: [w3.org/WAI/WCAG21/quickref/](https://www.w3.org/WAI/WCAG21/quickref/)
- MDN Web Docs: [developer.mozilla.org](https://developer.mozilla.org)
- Inclusive Components: [inclusive-components.design](https://inclusive-components.design)

---

**Document End**

*For questions or clarifications, contact the UX/UI team.*

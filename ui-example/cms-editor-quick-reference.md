# CMS Editor - Quick Reference Guide
**Version:** 2.0  
**Last Updated:** November 23, 2025

---

## 🎯 Project Overview

A formal pattern-based CMS with graph-structured content, real-time collaboration, and AI assistance.

**Key Features:**
- Block-based rich text editor
- Graph content model (C1)
- Version history with time-travel (C5)
- Real-time collaboration (F5)
- AI-powered suggestions (P16)
- Full-text search (P13)
- Multi-level validation (P11)

---

## 🏗️ Tech Stack

```
Frontend:  React 18 + TypeScript + Vite
State:     Zustand (local) + React Query (server)
Styling:   Tailwind CSS
Editor:    Lexical
Backend:   Node.js + Express
Database:  PostgreSQL (primary) + Neo4j (graph)
Cache:     Redis
Search:    Meilisearch
Storage:   S3 / Object Storage
Real-time: WebSocket + Operational Transform
```

---

## 📁 Project Structure

```
cms-editor/
├── frontend/
│   ├── src/
│   │   ├── app/              # App shell & routing
│   │   ├── features/         # Feature modules
│   │   │   ├── editor/
│   │   │   ├── media/
│   │   │   ├── collaboration/
│   │   │   └── search/
│   │   ├── shared/           # Shared components & utilities
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── utils/
│   │   │   └── types/
│   │   ├── services/         # External services
│   │   │   ├── api/
│   │   │   ├── validation/
│   │   │   └── parser/
│   │   └── styles/           # Global styles & tokens
│   └── public/
├── backend/
│   ├── src/
│   │   ├── api/              # REST/GraphQL endpoints
│   │   ├── services/         # Business logic
│   │   ├── models/           # Data models
│   │   ├── middleware/       # Auth, validation, etc.
│   │   └── utils/
│   └── tests/
└── docs/                     # Documentation
```

---

## 🎨 Design System Tokens

### Colors
```css
/* Primary */
--color-primary-500: #0EA5E9;
--color-primary-600: #0284C7; /* Hover */
--color-primary-700: #0369A1; /* Active */

/* Semantic */
--color-success: #10B981;
--color-warning: #F59E0B;
--color-error: #EF4444;
--color-info: #3B82F6;

/* Neutrals */
--color-gray-50:  #F9FAFB;  /* Light backgrounds */
--color-gray-900: #111827;  /* Dark text */
```

### Typography
```css
--font-sans: 'Inter', sans-serif;
--font-mono: 'Fira Code', monospace;

--text-sm:   0.875rem;  /* 14px */
--text-base: 1rem;      /* 16px */
--text-lg:   1.125rem;  /* 18px */
--text-xl:   1.25rem;   /* 20px */
```

### Spacing (4px base unit)
```css
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-4: 1rem;     /* 16px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
```

---

## 🔧 Core Patterns Implementation

### 1. Graph Structure (C1)

```typescript
interface ContentGraph {
  nodes: Map<string, ContentNode>
  edges: Map<string, ContentEdge>
  
  traverse(nodeId: string, depth: number): ContentNode[]
  neighbors(nodeId: string): ContentNode[]
  path(from: string, to: string): ContentNode[]
}

// Usage
const relatedContent = graph.traverse(currentPage.id, 2)
const linkedPages = graph.neighbors(currentPage.id)
```

### 2. Document/Artifact (C2)

```typescript
interface Document {
  id: string
  type: 'page' | 'post' | 'custom'
  title: string
  content: Block[]
  metadata: Metadata
  version: Version
  history: VersionHistory
  permissions: Permissions
}

type Block = 
  | { type: 'paragraph', content: RichText }
  | { type: 'heading', level: 1..6, content: RichText }
  | { type: 'image', src: string, alt: string }
  | { type: 'code', language: string, code: string }
```

### 3. Command Pattern (P30)

```typescript
interface Command {
  execute(): Promise<Result>
  undo(): Promise<void>
  redo(): Promise<void>
}

class InsertTextCommand implements Command {
  constructor(
    private editor: Editor,
    private text: string,
    private position: number
  ) {}
  
  async execute() {
    this.editor.insertText(this.text, this.position)
  }
  
  async undo() {
    this.editor.deleteText(this.position, this.text.length)
  }
  
  async redo() {
    this.editor.insertText(this.text, this.position)
  }
}
```

### 4. Validation Pipeline (P11)

```typescript
class ValidationPipeline {
  async validate(content: Content): Promise<ValidationResult> {
    const validators = [
      new SyntaxValidator(),
      new LinkValidator(),
      new AccessibilityValidator(),
      new BusinessRuleValidator()
    ]
    
    const errors: ValidationError[] = []
    const warnings: ValidationWarning[] = []
    
    for (const validator of validators) {
      const result = await validator.validate(content)
      errors.push(...result.errors)
      warnings.push(...result.warnings)
    }
    
    return {
      valid: errors.length === 0,
      errors,
      warnings
    }
  }
}
```

### 5. Operational Transform (F5)

```typescript
class OTEngine {
  transform(op1: Operation, op2: Operation): Operation {
    // Transform op1 against op2
    // Ensures convergence in concurrent editing
  }
  
  apply(doc: Block[], op: Operation): Block[] {
    // Apply operation to document
  }
  
  compose(op1: Operation, op2: Operation): Operation {
    // Combine sequential operations
  }
}
```

---

## 🔌 API Endpoints

### Content
```
GET    /api/content              # List content
POST   /api/content              # Create content
GET    /api/content/:id          # Get content
PUT    /api/content/:id          # Update content
DELETE /api/content/:id          # Delete content
GET    /api/content/:id/versions # Get versions
POST   /api/content/:id/publish  # Publish content
```

### Media
```
GET    /api/media                # List media
POST   /api/media/upload         # Upload media
GET    /api/media/:id            # Get media
PUT    /api/media/:id            # Update metadata
DELETE /api/media/:id            # Delete media
```

### Search
```
GET    /api/search?q=...&filters=... # Search content
POST   /api/search/reindex            # Reindex
```

### Real-time
```
WebSocket /ws/collab/:documentId  # Collaboration
```

---

## 💾 Database Schema (Quick Ref)

```sql
-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  name VARCHAR NOT NULL,
  role VARCHAR NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Content
CREATE TABLE content (
  id UUID PRIMARY KEY,
  type VARCHAR NOT NULL,
  title VARCHAR NOT NULL,
  slug VARCHAR UNIQUE NOT NULL,
  content JSONB NOT NULL,
  metadata JSONB,
  status VARCHAR NOT NULL,
  author_id UUID REFERENCES users(id),
  parent_id UUID REFERENCES content(id),
  published_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Content Versions
CREATE TABLE content_versions (
  id UUID PRIMARY KEY,
  content_id UUID REFERENCES content(id),
  version_number INT NOT NULL,
  content_snapshot JSONB NOT NULL,
  diff JSONB,
  author_id UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Graph Relationships
CREATE TABLE content_relations (
  id UUID PRIMARY KEY,
  from_content_id UUID REFERENCES content(id),
  to_content_id UUID REFERENCES content(id),
  relation_type VARCHAR NOT NULL,
  metadata JSONB
);

-- Indexes
CREATE INDEX idx_content_slug ON content(slug);
CREATE INDEX idx_content_status ON content(status);
CREATE INDEX idx_content_author ON content(author_id);
CREATE INDEX idx_versions_content ON content_versions(content_id);
```

---

## 🎯 State Management

### Local State (Zustand)
```typescript
// Editor store
const useEditorStore = create<EditorStore>((set) => ({
  content: [],
  selection: null,
  history: { past: [], future: [] },
  
  executeCommand: async (cmd) => { /* ... */ },
  undo: () => { /* ... */ },
  redo: () => { /* ... */ }
}))
```

### Server State (React Query)
```typescript
// Fetch content
const { data, isLoading } = useQuery({
  queryKey: ['content', id],
  queryFn: () => api.content.get(id),
  staleTime: 5 * 60 * 1000
})

// Update content
const mutation = useMutation({
  mutationFn: (data) => api.content.update(data),
  onSuccess: () => {
    queryClient.invalidateQueries(['content'])
  }
})
```

---

## 🚀 Performance Targets

- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms
- **CLS (Cumulative Layout Shift)**: < 0.1
- **Initial Bundle**: < 200 KB (gzipped)
- **Time to Interactive**: < 3.5s
- **API Response**: < 300ms (p95)

### Optimization Techniques
- Code splitting (lazy load routes)
- Virtual scrolling (large lists)
- Image optimization (lazy loading, WebP)
- API response caching (React Query)
- Debouncing (search, auto-save)
- Service workers (offline support)

---

## ♿ Accessibility Checklist

- [ ] Keyboard navigation (Tab, Enter, Escape)
- [ ] Focus management (trap focus in modals)
- [ ] Skip links ("Skip to main content")
- [ ] ARIA labels (buttons, forms, status)
- [ ] Color contrast (4.5:1 minimum)
- [ ] Screen reader announcements (aria-live)
- [ ] Alt text for images
- [ ] Form validation messages
- [ ] Error handling with clear messages

---

## 🎨 Component Examples

### Button
```tsx
<Button
  variant="primary"
  size="medium"
  onClick={handleClick}
  disabled={isLoading}
>
  Save Changes
</Button>
```

### Toast (P27)
```tsx
toast.success('Content published successfully', {
  action: {
    label: 'View',
    onClick: () => navigate(`/content/${id}`)
  }
})
```

### Progress Bar (P28)
```tsx
<ProgressBar
  value={uploadProgress}
  max={100}
  label="Uploading..."
  onCancel={handleCancel}
/>
```

### Modal
```tsx
<Modal
  isOpen={isOpen}
  onClose={onClose}
  title="Confirm Delete"
  size="medium"
>
  <p>Are you sure you want to delete this content?</p>
  <Modal.Footer>
    <Button variant="secondary" onClick={onClose}>
      Cancel
    </Button>
    <Button variant="danger" onClick={handleDelete}>
      Delete
    </Button>
  </Modal.Footer>
</Modal>
```

---

## ⌨️ Keyboard Shortcuts

### Global
- `⌘K` / `Ctrl+K`: Command palette
- `⌘N` / `Ctrl+N`: New content
- `⌘S` / `Ctrl+S`: Save
- `⌘/` / `Ctrl+/`: Search
- `⌘Z` / `Ctrl+Z`: Undo
- `⌘⇧Z` / `Ctrl+Y`: Redo

### Editor
- `⌘B` / `Ctrl+B`: Bold
- `⌘I` / `Ctrl+I`: Italic
- `⌘K` / `Ctrl+K`: Insert link
- `/`: Block menu
- `⌘⌥1-6`: Heading levels

### Navigation
- `G` then `H`: Dashboard
- `G` then `C`: Content
- `G` then `M`: Media

---

## 🧪 Testing Strategy

### Unit Tests
```typescript
// Component test
test('Button renders correctly', () => {
  render(<Button>Click me</Button>)
  expect(screen.getByRole('button')).toHaveTextContent('Click me')
})

// Hook test
test('useContent fetches content', async () => {
  const { result } = renderHook(() => useContent('123'))
  await waitFor(() => expect(result.current.isSuccess).toBe(true))
  expect(result.current.data).toBeDefined()
})
```

### Integration Tests
```typescript
// User flow test
test('User can create and publish content', async () => {
  render(<App />)
  
  // Navigate to editor
  await userEvent.click(screen.getByText('New Content'))
  
  // Enter content
  await userEvent.type(screen.getByLabelText('Title'), 'Test Post')
  await userEvent.type(screen.getByRole('textbox'), 'Content here')
  
  // Publish
  await userEvent.click(screen.getByText('Publish'))
  
  // Verify
  expect(await screen.findByText('Published successfully')).toBeInTheDocument()
})
```

### E2E Tests (Playwright)
```typescript
test('Complete content workflow', async ({ page }) => {
  await page.goto('/editor')
  await page.fill('[placeholder="Title"]', 'E2E Test Post')
  await page.fill('[contenteditable]', 'Test content')
  await page.click('button:has-text("Publish")')
  await expect(page.locator('.toast-success')).toBeVisible()
})
```

---

## 🐛 Common Issues & Solutions

### Issue: State not updating
```typescript
// ❌ Wrong (mutating state)
state.content.push(newBlock)

// ✅ Correct (immutable update)
set(state => ({
  content: [...state.content, newBlock]
}))
```

### Issue: Memory leak in useEffect
```typescript
// ❌ Wrong (no cleanup)
useEffect(() => {
  const interval = setInterval(autoSave, 5000)
}, [])

// ✅ Correct (with cleanup)
useEffect(() => {
  const interval = setInterval(autoSave, 5000)
  return () => clearInterval(interval)
}, [])
```

### Issue: Race condition in async
```typescript
// ❌ Wrong (race condition)
const fetchData = async () => {
  const data = await api.fetch()
  setState(data)
}

// ✅ Correct (abort controller)
const fetchData = async () => {
  const controller = new AbortController()
  
  try {
    const data = await api.fetch({ signal: controller.signal })
    setState(data)
  } catch (error) {
    if (error.name === 'AbortError') return
    handleError(error)
  }
  
  return () => controller.abort()
}
```

---

## 📚 Resources

### Documentation
- React: https://react.dev
- TypeScript: https://typescriptlang.org
- Tailwind CSS: https://tailwindcss.com
- Lexical: https://lexical.dev
- React Query: https://tanstack.com/query

### Tools
- Figma: https://figma.com
- GitHub: https://github.com
- VS Code: https://code.visualstudio.com

### Learning
- Patterns: https://patterns.dev
- A11y: https://inclusive-components.design
- Performance: https://web.dev

---

## 🚦 Development Workflow

### 1. Start Development Server
```bash
# Frontend
cd frontend
npm run dev

# Backend
cd backend
npm run dev

# Database
docker-compose up -d
```

### 2. Create Feature Branch
```bash
git checkout -b feature/new-feature
```

### 3. Make Changes & Test
```bash
npm test
npm run lint
npm run type-check
```

### 4. Commit & Push
```bash
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
```

### 5. Create Pull Request
- Describe changes
- Link to issue
- Request review
- Wait for CI to pass

### 6. Deploy
```bash
# Staging
npm run deploy:staging

# Production (after approval)
npm run deploy:production
```

---

## 🔐 Security Checklist

- [ ] Input validation on all forms
- [ ] Output encoding (XSS prevention)
- [ ] CSRF tokens on state-changing requests
- [ ] JWT tokens in HTTPOnly cookies
- [ ] Rate limiting on API endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] Content Security Policy (CSP) headers
- [ ] HTTPS only (TLS 1.3)
- [ ] Sensitive data encryption
- [ ] Regular security audits

---

## 📞 Support & Contact

**Team Contacts:**
- Product: product@cms-editor.com
- Engineering: eng@cms-editor.com
- Design: design@cms-editor.com

**Links:**
- Documentation: https://docs.cms-editor.com
- Issue Tracker: https://github.com/cms-editor/issues
- Slack: #cms-editor

---

**Quick Reference Guide Version 2.0**  
*For detailed information, refer to the complete UX/UI Specification and Technical Architecture documents.*

### C2. Document/Artifact

**Definition C2:**
$D = (id, content, metadata, version)$

- $id : ID$ is unique identifier
- $content : Content$ is document body
- $metadata : Metadata$ is key-value properties
- $version : Version$ is version information

**Properties:**

**P.C2.1 (Editability):**
```
edit(D, Δ) → D'
where Δ : Delta and D'.version.number = D.version.number + 1
```

**P.C2.2 (Versionability):**
```
∀t: ∃D': checkout(D, t) = D'
where D'.version.timestamp = t
```

**P.C2.3 (Serializability):**
```
deserialize(serialize(D)) = D
```

**Operations:**

1. **Edit:**
   ```
   edit(D: Document, Δ: Delta) → Document
   ```
   ```
   edit(D: Document, Δ: Delta) → Document
      = D' where D'.content = apply(D.content, Δ)
               ∧ D'.version = next_version(D.version, Δ)
   ```

2. **Checkout Version:**
   ```
   checkout(D: Document, v: Version) → Document
   ```
   ```
   checkout(D: Document, v: Version) → Document
      = D' where D'.content = reconstruct(D.history, v)
   ```

3. **Merge:**
   ```
   merge(D₁: Document, D₂: Document) → Document | Conflict
   ```
   ```
   merge(D₁: Document, D₂: Document) → Document | Conflict
      = three-way merge with common ancestor
   ```

**Manifestations:**
- Text documents (Markdown, Word)
- Source code files
- Proofs (Lean, Coq)
- CAD models (parametric designs)
- Content blocks (CMS)

---

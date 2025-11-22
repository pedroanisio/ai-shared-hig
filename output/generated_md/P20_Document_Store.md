### P20. Document Store

**Definition P20:**
$D = (collections, documents, queries, indices)$

- $documents : Set⟨Document⟩$ is schema-free documents

**Type Definitions:**
```
Document := Map⟨String, Value⟩  // JSON-like structure
Value := String | ℕ | ℝ | 𝔹 | null | Sequence⟨Value⟩ | Map⟨String,Value⟩
Query := (filters: Map⟨Path, Predicate⟩, projection: Set⟨Path⟩)
```

**Properties:**

**P.P20.1 (Schema-Free):**
```
Documents in same collection can have different structures
```

**P.P20.2 (Nested Data):**
```
Documents can contain nested objects and arrays
```

**Operations:**

1. **Find:**
   ```
   find({age: {$gt: 25}, city: "NYC"}) → Set⟨Document⟩
   ```
   ```
   find({age: {$gt: 25}, city: "NYC"}) → Set⟨Document⟩
   ```

2. **Insert:**
   ```
   insert(collection, document) → Effect
   ```
   ```
   insert(collection, document) → Effect
   ```

3. **Update:**
   ```
   update(query, changes) → Effect
   ```
   ```
   update(query, changes) → Effect
   ```

**Manifestations:**
- Note storage (Notion, Roam)
- Configuration (JSON files)
- Log aggregation
- CMS content

---

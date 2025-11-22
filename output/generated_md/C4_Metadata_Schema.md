### C4. Metadata Schema

**Definition C4:**
$M = (schema, data, validators)$

- $data : Map⟨String, Value⟩$ is actual metadata
- $validators : Map⟨String, Predicate⟩$ is validation rules

**Properties:**

**P.C4.1 (Type Safety):**
```
∀k ∈ keys(data): type(data[k]) = schema[k]
```

**P.C4.2 (Validation):**
```
valid(M) ⇔ ∀k ∈ keys(data): validators[k](data[k])
```

**P.C4.3 (Extensibility):**
```
extend(M, k, v) → M' where keys(M'.data) = keys(M.data) ∪ {k}
```

**Operations:**

1. **Add Field:**
   ```
   add(M: Metadata, k: String, v: Value) → Metadata
   ```
   ```
   add(M: Metadata, k: String, v: Value) → Metadata
      = M' where M'.data[k] = v
               ∧ validate(M'.schema[k], v)
   ```

2. **Query:**
   ```
   query(M: Metadata, pred: Predicate) → 𝔹
   ```
   ```
   query(M: Metadata, pred: Predicate) → 𝔹
      = pred(M.data)
   ```

3. **Index:**
   ```
   index(docs: Set⟨Document⟩, field: String) → Map⟨Value, Set⟨Document⟩⟩
   ```
   ```
   index(docs: Set⟨Document⟩, field: String) → Map⟨Value, Set⟨Document⟩⟩
      = group documents by field value
   ```

**Manifestations:**
- Tags (blog posts, notes)
- Properties (CAD features)
- Attributes (HTML elements)
- Annotations (PDF, code comments)
- Labels (issue tracking)

---

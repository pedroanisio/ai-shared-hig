### P13. Indexer/Query Engine

**Definition P13:**
$I = (data, index, query\_processor, update)$

- $data : Set⟨Item⟩$ is data being indexed
- $index : Index$ is index structure (inverted index, B-tree, etc.)

**Type Definitions:**
```
Index := InvertedIndex | BTree | HashMap | RTree | KDTree
Query := (predicates: Sequence⟨Predicate⟩, order: Order, limit: ℕ)
Predicate := (field: String, op: Operator, value: Value)
Operator := Eq | Lt | Gt | Contains | ...
```

**Properties:**

**P.P13.1 (Index Consistency):**
```
∀item ∈ data: item in index
data changes → index updated
```

**P.P13.2 (Query Performance):**
```
query(index) ≪ query(data)  // Much faster than linear scan
```

**P.P13.3 (Space Trade-off):**
```
space(index) = O(|data|)  // Linear space overhead
```

**Operations:**

1. **Build Index:**
   ```
   build_index(data: Set⟨Item⟩) → Index
   ```
   ```
   build_index(data: Set⟨Item⟩) → Index
      = index := empty_index()
        for item in data:
          for field in indexed_fields:
            value := extract(item, field)
            index[field][value] := index[field][value] ∪ {item}
        return index
   ```

2. **Query:**
   ```
   query(q: Query) → Sequence⟨Item⟩
   ```
   ```
   query(q: Query) → Sequence⟨Item⟩
      = candidates := index_lookup(q.predicates[0])  // Use index for first predicate
        results := filter(candidates, q.predicates[1:])  // Filter rest
        results := sort(results, q.order)
        return take(results, q.limit)
   ```

3. **Update Index:**
   ```
   update_item(old: Item, new: Item) → Effect
   ```
   ```
   update_item(old: Item, new: Item) → Effect
      = for field in indexed_fields:
          old_val := extract(old, field)
          new_val := extract(new, field)
          if old_val ≠ new_val:
            index[field][old_val] := index[field][old_val] ∖ {old}
            index[field][new_val] := index[field][new_val] ∪ {new}
   ```

4. **Inverted Index (Text):**
   ```
   token → {documents containing token}
   ```
   ```
   token → {documents containing token}
      Example: "hello" → {doc1, doc5, doc8}
   ```

5. **B-Tree (Range Queries):**
   ```
   Sorted key → value
   ```
   ```
   Sorted key → value
      Efficient for range queries: find(x, y)
   ```

6. **Spatial Index (Geometric):**
   ```
   R-Tree or KD-Tree
      Efficient for spatial queries: near(point, radius)
   ```

7. **Graph Index:**
   ```
   node → {adjacent nodes}
   ```
   ```
   node → {adjacent nodes}
      Efficient for graph traversal
   ```

**Manifestations:**
- Full-text search (documents)
- Graph indexes (knowledge graphs)
- Symbol tables (code)
- Spatial indexes (GIS)

---

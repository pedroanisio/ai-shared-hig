### P8. Search-Based Navigation

**Definition P8:**
$S = (query, index, results, ranker)$

- $query : String$ is search query
- $index : Index⟨Item⟩$ is searchable index
- $results : Sequence⟨Item⟩$ is ranked results

**Properties:**

**P.P8.1 (Real-Time Results):**
```
type(query[0..n]) → results updated within 100ms
```

**P.P8.2 (Fuzzy Matching):**
```
query = "fle" matches "file", "filter", "flexible"
```

**P.P8.3 (Ranking):**
```
results sorted by ranker(item, query) descending
```

**Operations:**

1. **Search:**
   ```
   search(q: String) → Sequence⟨Item⟩
   ```
   ```
   search(q: String) → Sequence⟨Item⟩
      = candidates := fuzzy_match(index, q)
        scores := map(candidates, λitem: ranker(item, q))
        sort(zip(candidates, scores), by: score, desc)
        → take(20)
   ```

2. **Update Index:**
   ```
   index(items: Set⟨Item⟩) → Effect
   ```
   ```
   index(items: Set⟨Item⟩) → Effect
      = for item in items:
          tokens := tokenize(item)
          for token in tokens:
            inverted_index[token] := inverted_index[token] ∪ {item}
   ```

3. **Rank:**
   ```
   ranker(item: Item, query: String) → ℝ
   ```
   ```
   ranker(item: Item, query: String) → ℝ
      = w₁·string_similarity(item.name, query)
        + w₂·recency_score(item.timestamp)
        + w₃·frequency_score(item.access_count)
   ```

**Manifestations:**
- File search (Spotlight, Everything)
- Theorem search (Lean libraries)
- Command palette (editors)
- Symbol search (code navigation)

---

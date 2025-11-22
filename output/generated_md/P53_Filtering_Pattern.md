### P53. Filtering Pattern

**Definition P53:**
$F = (data, filters, active, result, facets)$

- $data : Set⟨Item⟩$ is full dataset
- $filters : Map⟨String, Filter⟩$ is available filters
- $active : Map⟨String, FilterValue⟩$ is active filters
- $result : Set⟨Item⟩$ is filtered result

**Type Definitions:**
```
Filter := (
FilterType := Range | Select | MultiSelect | Search | Boolean
FilterValue := Value | Range(min, max) | Set⟨Value⟩
Facet := Map⟨Value, ℕ⟩  // value → count
```

**Properties:**

**P.P53.1 (Result Computation):**
```
result = {item ∈ data : ∀(k, v) ∈ active: filters[k].apply(item, v)}
```

**P.P53.2 (Facet Accuracy):**
```
facets[filter_k][value_v] = |{item ∈ result : item[k] = value_v}|
```

**P.P53.3 (Filter Composition):**
```
Multiple filters combined with AND (intersection)
Multi-select within filter combined with OR (union)
```

**Operations:**

1. **Apply Filter:**
   ```
   apply_filter(filter_name: String, value: FilterValue) → Effect
   ```
   ```
   apply_filter(filter_name: String, value: FilterValue) → Effect
      = active[filter_name] := value
        result := compute_result(data, active)
        facets := compute_facets(result, filters)
        notify_observers(result)
   ```

2. **Compute Result:**
   ```
   compute_result(data: Set⟨Item⟩, active: Map⟨String, FilterValue⟩) → Set⟨Item⟩
   ```
   ```
   compute_result(data: Set⟨Item⟩, active: Map⟨String, FilterValue⟩) → Set⟨Item⟩
      = filter(data, λitem:
          ∀(k, v) ∈ active: filters[k].apply(item, v)
        )
   ```

3. **Compute Facets:**
   ```
   compute_facets(result: Set⟨Item⟩, filters: Map⟨String, Filter⟩) → Map⟨String, Facet⟩
   ```
   ```
   compute_facets(result: Set⟨Item⟩, filters: Map⟨String, Filter⟩) → Map⟨String, Facet⟩
      = {
          (filter_name, {
            (value, count(result, λitem: item[filter_name] = value))
            for value in possible_values(filter_name)
          })
          for filter_name in keys(filters)
        }
   ```

4. **Clear Filters:**
   ```
   clear() → Effect
   ```
   ```
   clear() → Effect
      = active := {}
        result := data
        facets := compute_facets(result, filters)
   ```

5. **Range Filter:**
   ```
   Price: $0 - $1000
      apply(item, (min, max)) = min ≤ item.price ≤ max
   ```

6. **Multi-Select Filter:**
   ```
   Colors: [✓ Red] [✓ Blue] [ ] Green
      apply(item, selected) = item.color ∈ selected
   ```

7. **Search Filter:**
   ```
   Search: "laptop"
      apply(item, query) = contains(item.name, query, case_insensitive)
   ```

8. **Boolean Filter:**
   ```
   [✓] In Stock Only
      apply(item, true) = item.in_stock
   ```

**Manifestations:**
- E-commerce product filters
- Search result filters
- Data table column filters
- Email filters
- Log viewers

---

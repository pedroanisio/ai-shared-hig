### P54. Sorting Pattern

**Definition P54:**
$S = (data, columns, order, comparator)$

- $data : Sequence⟨Item⟩$ is dataset
- $columns : Sequence⟨Column⟩$ is sortable columns
- $order : Sequence⟨(Column, Direction)⟩$ is sort specification
- $comparator : Item × Item → \{-1, 0, 1\}$ is comparison function

**Type Definitions:**
```
Column := (name: String, type: Type, extract: Item → Value)
Direction := Asc | Desc
Order := Sequence⟨(Column, Direction)⟩  // Multi-column sort
```

**Properties:**

**P.P54.1 (Stable Sort):**
```
Items with equal sort keys maintain their original relative order
```

**P.P54.2 (Multi-Column Sort):**
```
Sort by order[0], then order[1] for ties, then order[2], ...
```

**P.P54.3 (Type-Aware Comparison):**
```
comparator respects type semantics:
Numeric: 2 < 10
String: "a" < "b" (lexicographic)
Date: older < newer
```

**Operations:**

1. **Sort Data:**
   ```
   sort(data: Sequence⟨Item⟩, order: Order) → Sequence⟨Item⟩
   ```
   ```
   sort(data: Sequence⟨Item⟩, order: Order) → Sequence⟨Item⟩
      = stable_sort(data, composite_comparator(order))
   ```

2. **Composite Comparator:**
   ```
   composite_comparator(order: Order) → Comparator
   ```
   ```
   composite_comparator(order: Order) → Comparator
      = λ(item1, item2):
          for (column, direction) in order:
            val1 := column.extract(item1)
            val2 := column.extract(item2)
            cmp := compare(val1, val2, column.type)
            if cmp ≠ 0:
              return cmp · (direction = Asc ? 1 : -1)
          return 0  // All keys equal
   ```

3. **Toggle Sort:**
   ```
   toggle_sort(column: Column) → Effect
   ```
   ```
   toggle_sort(column: Column) → Effect
      = if order[0].column = column:
          order[0].direction := flip(order[0].direction)
        else:
          order := [(column, Asc)] ++ order
        data := sort(data, order)
   ```

4. **Clear Sort:**
   ```
   clear_sort() → Effect
   ```
   ```
   clear_sort() → Effect
      = order := []
        data := original_data
   ```

5. **Single Column:**
   ```
   Click column header → sort by that column
   ```
   ```
   Click column header → sort by that column
      Click again → reverse direction
   ```

6. **Multi-Column (Shift-Click):**
   ```
   Click column → primary sort
   ```
   ```
   Click column → primary sort
      Shift+Click another → secondary sort
      Shift+Click third → tertiary sort
   ```

7. **Drag to Reorder:**
   ```
   Drag column headers to specify sort priority
   Name ▲     (sorted ascending)
   Price ▼    (sorted descending)
   Date       (not sorted)
   Name ▲(1) Price ▼(2)  (multi-column with priority)
   ```

**Manifestations:**
- Data tables
- File explorers
- Email clients
- Spreadsheets
- Admin panels

---

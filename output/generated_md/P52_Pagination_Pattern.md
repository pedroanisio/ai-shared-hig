### P52. Pagination Pattern

**Definition P52:**
$P = (data, page, size, total, nav)$

- $data : Sequence⟨Item⟩$ is full dataset
- $page : ℕ$ is current page number (1-indexed)
- $size : ℕ$ is items per page
- $total : ℕ$ is total item count

**Type Definitions:**
```
Navigation := {
```

**Properties:**

**P.P52.1 (Page Calculation):**
```
total_pages = ⌈total / size⌉
page ∈ [1, total_pages]
```

**P.P52.2 (Item Range):**
```
current_items = data[(page-1)·size : page·size]
```

**P.P52.3 (Boundary Checks):**
```
has_prev ⇔ page > 1
has_next ⇔ page < total_pages
```

**Operations:**

1. **Get Page:**
   ```
   get_page(page_num: ℕ) → Sequence⟨Item⟩
   ```
   ```
   get_page(page_num: ℕ) → Sequence⟨Item⟩
      = start := (page_num - 1) · size
        end := min(start + size, total)
        return data[start:end]
   ```

2. **Navigate:**
   ```
   next() → Effect
   ```
   ```
   next() → Effect
      = if page < total_pages:
          page := page + 1
          load_page(page)
      prev() → Effect
      = if page > 1:
          page := page - 1
          load_page(page)
      goto(p: ℕ) → Effect
      = if 1 ≤ p ≤ total_pages:
          page := p
          load_page(p)
   ```

3. **Change Page Size:**
   ```
   set_page_size(new_size: ℕ) → Effect
   ```
   ```
   set_page_size(new_size: ℕ) → Effect
      = size := new_size
        page := 1  // Reset to first page
        load_page(1)
   ```

4. **Offset-Based (Traditional):**
   ```
   Query: SELECT * FROM items LIMIT size OFFSET (page-1)*size
      Pros: Can jump to any page
      Cons: Performance degrades with large offsets
   ```

5. **Cursor-Based (API):**
   ```
   Query: SELECT * FROM items WHERE id > cursor LIMIT size
      cursor := last_item.id
      Pros: Consistent performance
      Cons: Can't jump to arbitrary page
   ```

6. **Infinite Scroll:**
   ```
   Scroll to bottom → load_next_page() → append to list
   ```
   ```
   Scroll to bottom → load_next_page() → append to list
      Pros: Smooth UX
      Cons: No page bookmarks, harder navigation
   ```

7. **Numbered:**
   ```
   [< Prev] [1] [2] [3] ... [10] [Next >]
   ```

8. **Simple:**
   ```
   [< Previous] Page 3 of 10 [Next >]
   ```

9. **Load More:**
   ```
   [Show 25 more items]
   ```

**Manifestations:**
- Search results
- Product listings
- Data tables
- Blog archives
- API responses

---

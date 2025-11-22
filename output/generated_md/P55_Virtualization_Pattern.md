### P55. Virtualization Pattern

**Definition P55:**
$V = (data, viewport, item\_height, buffer, visible)$

- $data : Sequence⟨Item⟩$ is full dataset
- $viewport : Rectangle$ is visible area
- $buffer : ℕ$ is number of items to pre-render beyond viewport
- $visible : Sequence⟨Item⟩$ is currently rendered items

**Properties:**

**P.P55.1 (Minimal Rendering):**
```
|visible| ≪ |data|
Only render items in viewport ± buffer
```

**P.P55.2 (Scroll Performance):**
```
scroll_event → update_visible() completes in < 16ms
```

**P.P55.3 (Memory Efficiency):**
```
memory_usage = O(|visible|), not O(|data|)
```

**P.P55.4 (Content Height):**
```
total_height = ∑_{item ∈ data} item_height(item)
```

**Operations:**

1. **Calculate Visible Items:**
   ```
   calculate_visible(scroll_top: ℝ) → (start: ℕ, end: ℕ)
   ```
   ```
   calculate_visible(scroll_top: ℝ) → (start: ℕ, end: ℕ)
      = start_idx := binary_search(data, λi:
          cumulative_height(data[0:i]) ≥ scroll_top - buffer_height
        )
        end_idx := binary_search(data, λi:
          cumulative_height(data[0:i]) ≥ scroll_top + viewport.height + buffer_height
        )
        return (start_idx, end_idx)
   ```

2. **Update On Scroll:**
   ```
   on_scroll(scroll_top: ℝ) → Effect
   ```
   ```
   on_scroll(scroll_top: ℝ) → Effect
      = (start, end) := calculate_visible(scroll_top)
        visible := data[start:end]
        offset := cumulative_height(data[0:start])
        render(visible, offset)
   ```

3. **Handle Variable Heights:**
   ```
   For variable item heights:
        - Maintain height cache: Map⟨ℕ, ℝ⟩
        - Estimate unknown heights
        - Measure rendered items
        - Update cache and reflow if necessary
   ```

4. **Fixed Height:**
   ```
   All items same height
      Simplest and most performant
   ```

5. **Variable Height (Estimated):**
   ```
   Estimate heights before rendering
      Adjust on actual measurement
   ```

6. **Dynamic Height:**
   ```
   Measure items as they render
      Maintain running height cache
      Update scroll container size
   1. Overscan buffer:
      Render N items beyond viewport
      Reduces blank areas during fast scroll
   2. Debounced updates:
      Wait τ ms after scroll stops
      Reduces re-renders during scroll
   3. Recycled DOM:
      Reuse DOM nodes for different items
      Reduces GC pressure
   4. Intersection Observer:
      Use native API for visibility detection
      Better performance than scroll events
   ```

**Manifestations:**
- Large lists (1000+ items)
- Data grids
- Feed viewers (social media)
- Log viewers
- File explorers

---

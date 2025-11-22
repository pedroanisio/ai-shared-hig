### P9. Backlinks/References

**Definition P9:**
$L = (forward_links, reverse_index, display)$

- $forward_links : Map⟨Item, Set⟨Item⟩⟩$ is explicit links
- $reverse_index : Map⟨Item, Set⟨Item⟩⟩$ is backlinks

**Properties:**

**P.P9.1 (Symmetry):**
```
item₁ ∈ forward_links[item₂] ⇔ item₂ ∈ reverse_index[item₁]
```

**P.P9.2 (Bidirectional Navigation):**
```
view(item) → display backlinks and forward links
```

**P.P9.3 (Auto-Update):**
```
add_link(A, B) → reverse_index[B] := reverse_index[B] ∪ {A}
```

**Operations:**

1. **Get Backlinks:**
   ```
   backlinks(item: Item) → Set⟨Item⟩
   ```
   ```
   backlinks(item: Item) → Set⟨Item⟩
      = reverse_index[item] | ∅
   ```

2. **Get Forward Links:**
   ```
   forward_links(item: Item) → Set⟨Item⟩
   ```
   ```
   forward_links(item: Item) → Set⟨Item⟩
      = forward_links[item] | ∅
   ```

3. **Update Index:**
   ```
   update_index(item: Item, links: Set⟨Item⟩) → Effect
   ```
   ```
   update_index(item: Item, links: Set⟨Item⟩) → Effect
      = old_links := forward_links[item]
        removed := old_links ∖ links
        added := links ∖ old_links
        for r in removed:
          reverse_index[r] := reverse_index[r] ∖ {item}
        for a in added:
          reverse_index[a] := reverse_index[a] ∪ {item}
        forward_links[item] := links
   ```

**Manifestations:**
- Backlinks panel (Roam Research, Obsidian)
- References (IDEs)
- Usages (code analysis)
- Dependencies (package managers)
- Citations (academic papers)

---

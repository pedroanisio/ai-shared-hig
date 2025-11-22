### P3. Hierarchical Navigator

**Definition P3:**
$N = (tree, selection, expansion, breadcrumb)$

- $tree : Tree⟨Node⟩$ is hierarchy
- $selection : Node | null$ is current selection
- $expansion : Set⟨Node⟩$ is expanded nodes
- $breadcrumb : Sequence⟨Node⟩$ is path to selection

**Properties:**

**P.P3.1 (Parent-Child Visibility):**
```
visible(n) ⇒ visible(parent(n))
Expanding parent makes children visible.
```

**P.P3.2 (Breadcrumb Consistency):**
```
breadcrumb = path_from_root(tree, selection)
```

**P.P3.3 (Lazy Loading):**
```
expand(n) → load_children(n) only when n first expanded
```

**Operations:**

1. **Expand Node:**
   ```
   expand(n: Node) → Effect
   ```
   ```
   expand(n: Node) → Effect
      = if n ∉ expansion:
          expansion := expansion ∪ {n}
          load_children(n) if children(n) = unloaded
          render(tree)
   ```

2. **Select Node:**
   ```
   select(n: Node) → Effect
   ```
   ```
   select(n: Node) → Effect
      = selection := n
        breadcrumb := compute_path(root, n)
        notify_observers(n)
   ```

3. **Navigate:**
   ```
   navigate(direction: Direction) → Effect
   ```
   ```
   navigate(direction: Direction) → Effect
      = case direction of
          Down → select(next_visible(selection))
          Up → select(prev_visible(selection))
          Right → expand(selection) ; select(first_child(selection))
          Left → collapse(selection) | select(parent(selection))
   ```

**Manifestations:**
- File explorer (OS file browser)
- Feature tree (CAD)
- Theorem library (Lean)
- Layer panel (Photoshop)
- Outline view (Word)

---

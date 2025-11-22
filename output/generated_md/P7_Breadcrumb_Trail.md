### P7. Breadcrumb Trail

**Definition P7:**
$B = (path, separators, actions)$

- $path : Sequence⟨Node⟩$ is current location path
- $separators : String$ is visual separators (e.g., " / ")

**Properties:**

**P.P7.1 (Hierarchical Path):**
```
path = [root, child₁, child₂, ..., current]
where childᵢ ∈ children(childᵢ₋₁)
```

**P.P7.2 (Clickable Ancestors):**
```
∀n ∈ path: click(n) → navigate_to(n)
```

**P.P7.3 (Auto-Update):**
```
navigate(new_location) → path := compute_path(root, new_location)
```

**Operations:**

1. **Compute Path:**
   ```
   compute_path(root: Node, target: Node) → Sequence⟨Node⟩
   ```
   ```
   compute_path(root: Node, target: Node) → Sequence⟨Node⟩
      = if target = root:
          [root]
        else:
          compute_path(root, parent(target)) ++ [target]
   ```

2. **Navigate:**
   ```
   navigate(node: Node) → Effect
   ```
   ```
   navigate(node: Node) → Effect
      = set_location(node)
        path := compute_path(root, node)
        render(breadcrumb)
   ```

**Manifestations:**
- File path (OS, web)
- Navigation chain (multi-step processes)
- Context path (hierarchical views)

---

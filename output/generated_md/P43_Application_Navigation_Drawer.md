### P43. Application Navigation Drawer

**Definition P43:**
$D = (S_{43}, C, O, \alpha_{43}, \omega_{43}, \pi_{43})$

- $\alpha_{43} : S_{43} \times S_{43} → Animation$ is **transition animation**

**Properties:**

**P.P43.1 (State Machine):**
```
Transitions:
collapsed ↔ expanded
expanded ↔ pinned
collapsed ↔ pinned
```

**P.P43.2 (Space Management):**
```
available_width = viewport.width - (σ₄₃ ∈ {expanded, pinned} ? ω₄₃ : 0)
```

**P.P43.3 (Overlay Behavior):**
```
O(σ₄₃) = true ⇔ σ₄₃ = expanded
```

**Operations:**

1. **Toggle:**
   ```
   toggle() → Effect
   ```
   ```
   toggle() → Effect
      = σ₄₃ := case σ₄₃ of
                 collapsed → expanded
                 expanded → collapsed
                 pinned → pinned (no change)
        animate(α₄₃(old_state, σ₄₃))
   ```

2. **Pin:**
   ```
   pin() → Effect
   ```
   ```
   pin() → Effect
      = σ₄₃ := pinned
        O := false
        persist("drawer.pinned", true)
   ```

3. **Navigate:**
   ```
   navigate(item: Item) → Effect
   ```
   ```
   navigate(item: Item) → Effect
      = route := π₄₃(item)
        goto(route)
        if mobile(): σ₄₃ := collapsed
   ```

**Manifestations:**
- Gmail sidebar
- VS Code activity bar
- Mobile hamburger menus
- CMS tool selector

---

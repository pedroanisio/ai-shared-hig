### P45. Drag and Drop Interaction

**Definition P45:**
$D = (S, T, G, F, \phi_{45}, \psi_{45})$

- $G : S → Ghost$ is **ghost element function**
- $F : S \times T → \{\text{accept}, \text{reject}\}$ is **acceptance predicate**
- $\phi_{45} : S \times T → Effect$ is **drop handler**

**Properties:**

**P.P45.1 (State Machine):**
```
idle → dragging → over_target → idle (on drop)
dragging → idle (on cancel)
```

**P.P45.2 (Ghost Visibility):**
```
visible(G(s)) ⇔ ψ₄₅ ∈ {dragging, over_target}
```

**P.P45.3 (Target Validation):**
```
∀s ∈ S, t ∈ T: F(s,t) = accept ⇒ highlight(t) when over(s,t)
```

**Operations:**

1. **Start Drag:**
   ```
   drag_start(s: Source, event: Event) → Effect
   ```
   ```
   drag_start(s: Source, event: Event) → Effect
      = ψ₄₅ := dragging
        ghost := G(s)
        create(ghost)
        data := serialize(s)
   ```

2. **Drop:**
   ```
   drop(s: Source, t: Target) → Effect
   ```
   ```
   drop(s: Source, t: Target) → Effect
      = if F(s, t) = accept:
          φ₄₅(s, t)
          commit()
          ψ₄₅ := idle
   ```

**Manifestations:**
- Reorder tabs
- Move files
- Drag blocks to reorder
- Kanban cards

---

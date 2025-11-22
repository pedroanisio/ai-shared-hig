### P39. Contextual Action Menu

**Definition P39:**
$M = (T, C, A, \pi_{39}, \sigma_{39}, \delta_{39})$

- $\pi_{39} : A \times C → \{\text{visible}, \text{hidden}, \text{disabled}\}$ is **availability**
- $\sigma_{39} : M → \{\text{open}, \text{closed}\}$ is **state**
- $\delta_{39} : M → \mathbb{R}^2$ is **positioning function**

**Properties:**

**P.P39.1 (Context Dependency):**
```
∀a ∈ A: π₃₉(a, C) determines visibility
```

**P.P39.2 (Mutual Exclusivity):**
```
∀m₁, m₂ ∈ Menus: m₁ ≠ m₂ ⇒ ¬(σ₃₉(m₁) = open ∧ σ₃₉(m₂) = open)
```

**P.P39.3 (Auto-Dismiss):**
```
σ₃₉(M) = open ∧ click(outside(M)) ⇒ σ₃₉(M) := closed
```

**Operations:**

1. **Open Menu:**
   ```
   open(T: Element, C: Context) → Effect
   ```
   ```
   open(T: Element, C: Context) → Effect
      = σ₃₉ := open
        position := δ₃₉(T, viewport)
        actions_visible := filter(A, λa: π₃₉(a, C) ≠ hidden)
        render(M, position, actions_visible)
   ```

2. **Execute Action:**
   ```
   execute(a: Action) → Effect
   ```
   ```
   execute(a: Action) → Effect
      = if π₃₉(a, C) ≠ disabled:
          perform(a, C)
          σ₃₉ := closed
   ```

**Manifestations:**
- Three-dot menu
- Right-click context menu
- Kebab menu (⋮)
- More actions dropdown

---

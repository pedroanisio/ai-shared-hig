### P42. Tooltip/Hint System

**Definition P42:**
$H = (T, C, \tau_{42}, \rho_{42}, \delta_{42}, \kappa_{42})$

- $C : T → String$ is **content function**
- $\rho_{42} : T \times Viewport → \mathbb{R}^2$ is **positioning**

**Properties:**

**P.P42.1 (Delayed Appearance):**
```
hover(T, t₀) ∧ continuous(hover, τ₄₂^show) ⇒ visible(H, t₀ + τ₄₂^show)
```

**P.P42.2 (Immediate Dismissal):**
```
¬hover(T) ⇒ hidden(H) within τ₄₂^hide
```

**P.P42.3 (Viewport Containment):**
```
bounds(H) ⊆ viewport ∨ adjust(ρ₄₂(T))
```

**Operations:**

1. **Show Tooltip:**
   ```
   show(T: Element) → Effect
   ```
   ```
   show(T: Element) → Effect
      = schedule(display(H), τ₄₂^show)
        position := ρ₄₂(T, viewport)
        content := C(T)
        render(H, position, content)
   ```

2. **Position:**
   ```
   ρ₄₂(T: Element, vp: Viewport) → Point
   ```
   ```
   ρ₄₂(T: Element, vp: Viewport) → Point
      = preferred := (T.center_x, T.bottom + gap)
        if fits(preferred, vp):
          preferred
        else:
          find_best_position([below, above, right, left], T, vp)
   τ₄₂^show ∈ [200ms, 800ms]  (typical: 500ms)
   τ₄₂^hide ∈ [0ms, 200ms]     (typical: 100ms)
   κ₄₂ ∈ [50, 100] characters
   ```

**Manifestations:**
- Icon button hints
- Abbreviated text expansion
- Keyboard shortcut hints
- Help text for controls

---

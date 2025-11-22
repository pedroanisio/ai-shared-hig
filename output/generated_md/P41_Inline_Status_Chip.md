### P41. Inline Status Chip

**Definition P41:**
$S = (I, L, \theta_{41}, \sigma_{41}, \alpha_{41})$

- $\sigma_{41} : States → Styles$ is **styling function**
- $\alpha_{41} : Chip → Action$ is optional **click action**

**Properties:**

**P.P41.1 (State-Style Coupling):**
```
∀θ ∈ States: style(S) = σ₄₁(θ)
```

**P.P41.2 (Compactness):**
```
width(S) ≤ 20·fontSize ∧ height(S) ≤ 2·fontSize
```

**P.P41.3 (Color Semantics):**
```
σ₄₁(success) = green
σ₄₁(warning) = yellow
σ₄₁(error) = red
σ₄₁(info) = blue
```

**Operations:**

1. **Update State:**
   ```
   set_state(θ_new: State) → Effect
   ```
   ```
   set_state(θ_new: State) → Effect
      = θ₄₁ := θ_new
        apply_style(σ₄₁(θ_new))
   ```

2. **Render:**
   ```
   render(S: Chip) → Component
   ```
   ```
   render(S: Chip) → Component
      = HStack([
          if I ≠ null then Icon(I),
          Text(L),
        ], style: σ₄₁(θ₄₁))
   ```

**Manifestations:**
- "AI: Partial" warning chip
- "✓ Saved" success chip
- "⏱ Syncing..." info chip
- "❌ 2 errors" error chip

---

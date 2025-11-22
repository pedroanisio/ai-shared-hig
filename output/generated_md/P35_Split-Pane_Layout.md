### P35. Split-Pane Layout

**Definition P35:**
$S = (P, D, R, \delta_{35}, \sigma_{35})$

- $\sigma_{35} : P → \{\text{visible}, \text{collapsed}\}$ is **state function**

**Properties:**

**P.P35.1 (Size Conservation):**
```
∑_{p ∈ P, σ₃₅(p) = visible} R(p) = 1
```

**P.P35.2 (Adjacency Constraints):**
```
∀p_i, p_j ∈ P: δ₃₅(p_i, p_j) = splitter ⇔ adjacent(p_i, p_j)
```

**P.P35.3 (Minimum Size Constraint):**
```
∀p ∈ P: R(p) ≥ R_min(p) ∨ σ₃₅(p) = collapsed
```

**Operations:**

1. **Resize:**
   ```
   resize(p_i: Pane, p_j: Pane, Δ: ℝ) → Effect
   ```
   ```
   resize(p_i: Pane, p_j: Pane, Δ: ℝ) → Effect
      = if R_min(p_i) ≤ R(p_i) + Δ ≤ R_max(p_i):
          R(p_i) := R(p_i) + Δ
          R(p_j) := R(p_j) - Δ
   ```

2. **Toggle Collapse:**
   ```
   toggle(p: Pane) → Effect
   ```
   ```
   toggle(p: Pane) → Effect
      = σ₃₅(p) := if σ₃₅(p) = visible then collapsed else visible
        redistribute_space()
   ```

3. **Persist Layout:**
   ```
   persist(S) → Storage
   ```
   ```
   persist(S) → Storage
      = save({pane_id: R(pane), state: σ₃₅(pane)} for pane in P)
   ```

**Manifestations:**
- 3-column CMS editor
- VS Code panels
- Split terminal windows
- IDE layouts

---

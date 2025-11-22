### P38. Badge/Indicator Pattern

**Definition P38:**
$B = (H, v, \rho_{38}, \sigma_{38}, \tau_{38})$

- $\rho_{38} : H → \mathbb{R}^2$ is **position function**
- $\sigma_{38} : v → Style$ is **styling function**

**Properties:**

**P.P38.1 (Overlay Positioning):**
```
bounds(B) ∩ bounds(H) ≠ ∅ ∧ bounds(B) ⊄ interior(bounds(H))
```

**P.P38.2 (Z-Index Ordering):**
```
z(B) > z(H) > z(siblings(H))
```

**P.P38.3 (Value Thresholding):**
```
display(v) = if v ≤ 99 then v else "99+"
```

**Operations:**

1. **Update Value:**
   ```
   update(v_new: ℕ) → Effect
   ```
   ```
   update(v_new: ℕ) → Effect
      = v := v_new
        animate(scale, τ₃₈)
        apply_style(σ₃₈(v))
   ```

2. **Increment:**
   ```
   increment(Δ: ℕ) → Effect
   ```
   ```
   increment(Δ: ℕ) → Effect
      = update(v + Δ)
   ```

**Manifestations:**
- Unread count
- "Recent 2" badge
- Warning count
- Online status dot

---

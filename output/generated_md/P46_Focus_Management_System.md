### P46. Focus Management System

**Definition P46:**
$F = (O, \tau_{46}, R, I, S)$

- $O : UI → Sequence⟨Element⟩$ is **focus order function**
- $\tau_{46} : Element → \{\text{tabbable}, \text{not\_tabbable}\}$ is **tabbability**
- $R : Modal → Element$ is **focus restoration function**
- $I : Element → VisualIndicator$ is **indicator rendering**

**Properties:**

**P.P46.1 (Tab Order Consistency):**
```
O(UI) = [e₁, ..., eₙ] where ∀i: tabindex(eᵢ) ≤ tabindex(eᵢ₊₁)
```

**P.P46.2 (Tabbability Rules):**
```
τ₄₆(e) = tabbable ⇔ visible(e) ∧ ¬disabled(e) ∧ interactive(e)
```

**P.P46.3 (Trap Containment):**
```
∀s ∈ S: focus(e) ∧ e ∉ s ⇒ redirect_focus(first_tabbable(s))
```

**Operations:**

1. **Move Focus Forward:**
   ```
   next_focus() → Effect
   ```
   ```
   next_focus() → Effect
      = order := O(active_scope)
        index := indexOf(focused, order)
        focus(order[(index + 1) mod |order|])
   ```

2. **Trap Focus:**
   ```
   trap(modal: Modal) → Effect
   ```
   ```
   trap(modal: Modal) → Effect
      = S := descendants(modal)
        R(modal) := currently_focused
        focus(first_tabbable(S))
   ```

**Manifestations:**
- Modal dialog focus trap
- Keyboard navigation
- Skip links
- Accessible widgets

---

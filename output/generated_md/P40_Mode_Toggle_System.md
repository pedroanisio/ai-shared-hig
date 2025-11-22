### P40. Mode Toggle System

**Definition P40:**
$T = (M, m_0, \delta_{40}, \phi_{40}, \iota_{40})$

- $\delta_{40} : M \times M → \{\text{allowed}, \text{forbidden}\}$ is **transition function**

**Properties:**

**P.P40.1 (Mutual Exclusivity):**
```
∀t: ∃!m ∈ M: active(m, t)
```

**P.P40.2 (Transition Atomicity):**
```
transition(m_i, m_j) succeeds ⇔ δ₄₀(m_i, m_j) = allowed
```

**P.P40.3 (UI Consistency):**
```
active(m) ⇒ UI = φ₄₀(m)
```

**Operations:**

1. **Toggle Mode:**
   ```
   toggle(m_target: Mode) → Effect
   ```
   ```
   toggle(m_target: Mode) → Effect
      = if δ₄₀(m_current, m_target) = allowed:
          save_state(m_current)
          m_current := m_target
          apply_ui(φ₄₀(m_target))
          restore_state(m_target)
   ```

2. **Cycle Modes:**
   ```
   cycle() → Effect
   ```
   ```
   cycle() → Effect
      = index := indexOf(M, m_current)
        toggle(M[(index + 1) mod |M|])
   ```

**Manifestations:**
- Auto-scroll toggle
- Edit vs Preview
- Tool modes
- View modes

---

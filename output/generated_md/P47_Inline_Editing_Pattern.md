### P47. Inline Editing Pattern

**Definition P47:**
$E = (M, \sigma_{47}, \tau_{47}, \phi_{47}, \psi_{47})$

- $\tau_{47} : Event → M$ is **trigger function**
- $\phi_{47} : Value \times Value → Effect$ is **commit handler**
- $\psi_{47} : () → Effect$ is **cancel handler**

**Properties:**

**P.P47.1 (Mode Exclusivity):**
```
|{m : active(m)}| = 1
```

**P.P47.2 (Position Preservation):**
```
bounds(view) ≈ bounds(edit)
```

**P.P47.3 (Validation Gate):**
```
commit(v) succeeds ⇔ valid(v)
```

**Operations:**

1. **Enter Edit Mode:**
   ```
   activate() → Effect
   ```
   ```
   activate() → Effect
      = value_original := value
        σ₄₇ := edit
        render_input()
        focus(input)
        select_all(input)
   ```

2. **Commit Changes:**
   ```
   commit() → Effect
   ```
   ```
   commit() → Effect
      = v_new := get_input_value()
        if valid(v_new):
          φ₄₇(value_original, v_new)
          value := v_new
          σ₄₇ := view
   ```

3. **Cancel Edit:**
   ```
   cancel() → Effect
   ```
   ```
   cancel() → Effect
      = ψ₄₇()
        value := value_original
        σ₄₇ := view
   ```

**Manifestations:**
- Click paragraph to edit
- Spreadsheet cell editing
- Filename rename
- Tag editing

---

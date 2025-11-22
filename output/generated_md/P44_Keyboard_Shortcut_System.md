### P44. Keyboard Shortcut System

**Definition P44:**
$K = (B, M, H, C, P)$

- $B : KeyCombo → Action$ is **binding map**
- $H : Action → String$ is **hint display function**
- $C : KeyCombo \times KeyCombo → \mathbb{B}$ is **conflict detector**
- $P : Platform → KeyMapping$ is **platform mapping**

**Properties:**

**P.P44.1 (Binding Uniqueness):**
```
∀k₁, k₂: k₁ ≠ k₂ ⇒ B(k₁) ≠ B(k₂) ∨ scope(k₁) ∩ scope(k₂) = ∅
```

**P.P44.2 (Platform Mapping):**
```
P(Mac): Ctrl ↦ Cmd, Alt ↦ Option
P(Windows): identity
P(Linux): identity
```

**P.P44.3 (Scope Hierarchy):**
```
priority(component) > priority(modal) > priority(global)
```

**Operations:**

1. **Register Binding:**
   ```
   register(combo: KeyCombo, action: Action, scope: Scope) → Effect
   ```
   ```
   register(combo: KeyCombo, action: Action, scope: Scope) → Effect
      = if ¬∃k: C(combo, k):
          B[combo] := (action, scope)
   ```

2. **Handle Keypress:**
   ```
   handle(event: KeyEvent) → Effect
   ```
   ```
   handle(event: KeyEvent) → Effect
      = combo := extract_combo(event)
        if combo ∈ dom(B):
          preventDefault(event)
          B[combo].action()
   ```

3. **Display Hint:**
   ```
   H(action: Action) → String
   ```
   ```
   H(action: Action) → String
      = format(P(current_platform), key_combo(action))
   ```

**Manifestations:**
- Ctrl+S (save)
- Ctrl+Z/Y (undo/redo)
- Ctrl+F (search)
- Esc (close dialog)

---

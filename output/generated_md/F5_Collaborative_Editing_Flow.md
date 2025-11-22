### F5. Collaborative Editing Flow

**Definition F5:**
$E = (U, D, O, T, M, \delta_{F5})$

- $T : O \times O → O$ is **transformation function**

**Properties:**

**P.F5.1 (Convergence):**
```
∀u_i, u_j ∈ U: lim_{t→∞} D_{u_i}(t) = D_{u_j}(t)
```

**P.F5.2 (Causality Preservation):**
```
op₁ → op₂ ⇒ apply(op₁) happens before apply(op₂)
```

**P.F5.3 (Intention Preservation):**
```
effect(op, D_u) = intention(user(op))
```

**Operations:**

1. **Local Edit:**
   ```
   edit(user: User, op: Operation) → Effect
   ```
   ```
   edit(user: User, op: Operation) → Effect
      = D_user := apply(op, D_user)
        broadcast(op, user)
   ```

2. **Receive Remote Edit:**
   ```
   receive(op: Operation, u_remote: User) → Effect
   ```
   ```
   receive(op: Operation, u_remote: User) → Effect
      = op' := transform(op, local_ops)
        D := apply(op', D)
   ```

3. **Transform:**
   ```
   T(op₁, op₂) = adjust op₁ for effects of op₂
   Concurrent inserts at same position:
     Use user ID as tiebreaker
   Delete vs Modify:
     Delete wins
   ```

**Manifestations:**
- Google Docs
- Figma multiplayer
- VS Code Live Share
- Notion collaboration

---

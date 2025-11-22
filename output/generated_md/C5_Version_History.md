### C5. Version History

**Definition C5:**
$H = (states, deltas, branches)$

- $states : Sequence⟨State⟩$ is sequence of states
- $deltas : Sequence⟨Delta⟩$ is sequence of changes

**Properties:**

**P.C5.1 (Immutability):**
```
∀s ∈ states: s is immutable once committed
```

**P.C5.2 (Reconstructability):**
```
∀i: states[i] = apply_all(states[0], deltas[1..i])
```

**P.C5.3 (Branching):**
```
branch(s, name) creates new branch from state s
```

**Operations:**

1. **Checkout:**
   ```
   checkout(H: History, t: Time) → State
   ```
   ```
   checkout(H: History, t: Time) → State
      = states[max{i : states[i].timestamp ≤ t}]
   ```

2. **Diff:**
   ```
   diff(H: History, t₁: Time, t₂: Time) → Delta
   ```
   ```
   diff(H: History, t₁: Time, t₂: Time) → Delta
      = compute difference between states at t₁ and t₂
   ```

3. **Revert:**
   ```
   revert(H: History, t: Time) → History
   ```
   ```
   revert(H: History, t: Time) → History
      = H' where H'.states = H.states + [checkout(H, t)]
   ```

**Manifestations:**
- Edit history (Google Docs)
- Git commits
- Feature sequence (CAD timeline)
- Proof versions (Lean)
- Database transaction log

---

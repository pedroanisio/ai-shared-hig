### C1. Graph Structure

**Definition C1:**
$G = (N, E, \lambda_n, \lambda_e)$

- $\lambda_n : N → Label_n$ is **node labeling function**
- $\lambda_e : E → Label_e$ is **edge labeling function**

**Properties:**

**P.C1.1 (Connectivity):**
```
connected(G) ⇔ ∀n₁, n₂ ∈ N: ∃ path from n₁ to n₂
```

**P.C1.2 (Cycle Detection):**
```
acyclic(G) ⇔ ¬∃ path: n → ... → n
```

**Operations:**

1. **Traverse:**
   ```
   traverse(n: N, depth: ℕ) → Set⟨N⟩
   ```
   ```
   traverse(n: N, depth: ℕ) → Set⟨N⟩
      = {n' ∈ N : distance(n, n') ≤ depth}
   ```

2. **Neighbors:**
   ```
   neighbors(n: N) → Set⟨N⟩
   ```
   ```
   neighbors(n: N) → Set⟨N⟩
      = {n' ∈ N : (n, n') ∈ E ∨ (n', n) ∈ E}
   ```

3. **Path:**
   ```
   path(n₁: N, n₂: N) → Sequence⟨N⟩ | null
   ```
   ```
   path(n₁: N, n₂: N) → Sequence⟨N⟩ | null
      = shortest path from n₁ to n₂, or null if none exists
   ```

**Manifestations:**
- Knowledge graphs
- File trees
- Feature history (CAD)
- Axiom dependencies (proof assistants)
- Part hierarchies (engineering)
- Social networks
- Dependency graphs

---

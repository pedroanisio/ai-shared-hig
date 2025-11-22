### P49. Multi-Step Form (Wizard) Pattern

**Definition P49:**
$W = (steps, current, data, nav, progress)$

- $steps : Sequence⟨Step⟩$ is form steps
- $current : ℕ$ is active step index

**Type Definitions:**
```
Step := (title: String, fields: Set⟨Field⟩, validate: () → 𝔹)
Navigation := {prev: () → Effect, next: () → Effect, goto: ℕ → Effect}
```

**Properties:**

**P.P49.1 (Sequential Progress):**
```
can_advance(step) ⇔ valid(steps[current])
```

**P.P49.2 (Data Accumulation):**
```
complete(step_i) ⇒ data := data ∪ extract_values(step_i)
```

**P.P49.3 (State Persistence):**
```
Navigate away → persist(data, current)
Return → restore(data, current)
```

**P.P49.4 (Non-Linear Navigation):**
```
∀i < current: can_goto(i)  // Can revisit completed steps
```

**Operations:**

1. **Next Step:**
   ```
   next() → Effect
   ```
   ```
   next() → Effect
      = if validate(steps[current]):
          data := data ∪ extract_values(steps[current])
          if current < |steps| - 1:
            current := current + 1
            render(steps[current])
          else:
            submit(data)
   ```

2. **Previous Step:**
   ```
   prev() → Effect
   ```
   ```
   prev() → Effect
      = if current > 0:
          current := current - 1
          render(steps[current])
   ```

3. **Go To Step:**
   ```
   goto(index: ℕ) → Effect
   ```
   ```
   goto(index: ℕ) → Effect
      = if index ≤ max_completed_step:
          current := index
          render(steps[index])
   ```

4. **Calculate Progress:**
   ```
   progress() → (ℕ, ℕ)
   ```
   ```
   progress() → (ℕ, ℕ)
      = (current + 1, |steps|)
   ```

5. **Linear:**
   ```
   [=====>      ] 50% (Step 2 of 4)
   ```

6. **Stepped:**
   ```
   1. Details ✓
      2. Payment ← (current)
      3. Review
      4. Confirm
   ```

7. **Breadcrumb:**
   ```
   Home > Personal Info > Payment > Review
   ```

**Manifestations:**
- Checkout flow (e-commerce)
- Onboarding wizard
- Setup assistant
- Multi-page survey
- Installation wizard

---

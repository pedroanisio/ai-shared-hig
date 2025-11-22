### P28. Progress Indicator

**Definition P28:**
$P = (current, total, label, eta, state)$

- $current : ℕ$ is completed work
- $total : ℕ$ is total work
- $eta : Time$ is estimated completion time
- $state : \{\text{running}, \text{paused}, \text{complete}, \text{error}\}$ is status

**Properties:**

**P.P28.1 (Monotonic Progress):**
```
current only increases: currentₜ₊₁ ≥ currentₜ
```

**P.P28.2 (Accurate Estimation):**
```
eta = now + (total - current) / rate
where rate = current / (now - start_time)
```

**P.P28.3 (Visual Feedback):**
```
percentage = current / total
display: progress bar, percentage, time remaining
```

**Operations:**

1. **Update Progress:**
   ```
   update(new_current: ℕ) → Effect
   ```
   ```
   update(new_current: ℕ) → Effect
      = current := new_current
        percentage := current / total
        eta := estimate_completion()
        render(progress_bar)
   ```

2. **Estimate Completion:**
   ```
   estimate_completion() → Time
   ```
   ```
   estimate_completion() → Time
      = elapsed := now - start_time
        rate := current / elapsed
        remaining := (total - current) / rate
        return now + remaining
   ```

3. **Complete:**
   ```
   complete() → Effect
   ```
   ```
   complete() → Effect
      = current := total
        state := complete
        render(progress_bar)
        schedule(hide, 2000)  // Hide after 2s
   ```

4. **Determinate:**
   ```
   Total known: [=========>    ] 75% (3 of 4 items)
   ```

5. **Indeterminate:**
   ```
   Total unknown: [<===>        ] Processing...
   ```

6. **Stepped:**
   ```
   Discrete steps: Step 2 of 5: "Processing data"
   ```

**Manifestations:**
- File upload/download
- Build progress
- Test execution
- Verification progress
- Installation progress

---

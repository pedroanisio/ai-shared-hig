### P67. Progressive Disclosure by AI Pattern

**Definition P67:**
A progressive disclosure system is a tuple $D = (H_{info}, score_{rel}, \sigma_{disc}, T)$ where:
- $H_{info} : Hierarchy⟨Information⟩$ is the complete information hierarchy
- $score_{rel} : (Information, Context) \to \mathbb{R}$ scores relevance
- $\sigma_{disc} : Strategy$ determines disclosure timing and sequencing
- $T : Time \to Revealed$ tracks what has been disclosed when

**Type Definitions:**
```
Information := (content: Content, level: ℕ, dependencies: Set⟨Information⟩)
Context := (user: User, task: Task, comprehension: Level)
Strategy := Immediate | OnDemand | Gradual | Adaptive
Revealed := Map⟨Information, Timestamp⟩
```

**Properties:**

**P.P67.1 (Relevance-Ordered Disclosure):**
```
∀i1, i2 ∈ H_info:
  score_rel(i1, ctx) > score_rel(i2, ctx) ⇒ T(i1) ≤ T(i2)
  Higher relevance disclosed earlier
```

**P.P67.2 (Dependency Preservation):**
```
∀i ∈ H_info:
  dependencies(i) ⊆ Revealed(T(i))
  Prerequisites disclosed before dependent information
```

**P.P67.3 (Cognitive Load Management):**
```
∀t: |Revealed(t) - Revealed(t-1)| ≤ threshold
Information released at digestible rate
Prevents overwhelming user
```

**Operations:**

1. **Compute Disclosure Order:**
   ```
   compute_order(H_info: Hierarchy, ctx: Context) → Sequence⟨Information⟩
   = scored := [(i, score_rel(i, ctx)) for i in H_info]
     sorted := topological_sort(scored, dependencies)
     return [i for (i, score) in sorted if score > threshold]
   ```

2. **Disclose Next:**
   ```
   disclose_next(ctx: Context, revealed: Revealed) → Information | null
   = candidates := filter_undisclosed(H_info, revealed)
     if empty(candidates): return null
     
     eligible := [i for i in candidates 
                  if dependencies(i) ⊆ revealed]
     if empty(eligible): return null
     
     next := argmax(eligible, λi.score_rel(i, ctx))
     if score_rel(next, ctx) < threshold_min: return null
     
     return next
   ```

3. **Adapt Disclosure Rate:**
   ```
   adapt_rate(comprehension: Level, feedback: Feedback) → Effect
   = if comprehension = Low:
       slow_disclosure_rate()
       simplify_next_items()
     else if comprehension = High ∧ user_engaged:
       accelerate_disclosure()
       include_advanced_details()
   ```

**Specializations:**
- Tutorial systems (skill-based disclosure)
- Documentation explorers (need-based disclosure)
- Configuration wizards (context-based disclosure)

**Manifestations:**
- Claude's iterative explanation expansion
- GPT-4 step-by-step problem solving
- Perplexity's progressive source disclosure
- Notion AI's expandable suggestions
- GitHub Copilot's incremental completions

---



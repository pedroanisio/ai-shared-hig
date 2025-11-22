### P16. Suggestion/Recommendation System

**Definition P16:**
$S = (context, model, candidates, ranker)$

- $context : Context$ is current state/situation

**Type Definitions:**
```
Suggestion := (content: Content, confidence: ℝ, source: Source)
Context := (user: User, location: Location, history: History, ...)
Model := learned patterns and preferences
```

**Properties:**

**P.P16.1 (Non-Blocking):**
```
Suggestions appear asynchronously, don't block user input
```

**P.P16.2 (Accept/Reject):**
```
User can accept, reject, or ignore suggestions
```

**P.P16.3 (Learning):**
```
User actions → update model → improve future suggestions
```

**Operations:**

1. **Generate Suggestions:**
   ```
   suggest(context: Context) → Sequence⟨Suggestion⟩
   ```
   ```
   suggest(context: Context) → Sequence⟨Suggestion⟩
      = candidates := generate_candidates(context, model)
        scored := map(candidates, λs: (s, ranker(s, context)))
        sorted := sort(scored, by: score, desc)
        return take(sorted, 5)
   ```

2. **Accept Suggestion:**
   ```
   accept(suggestion: Suggestion) → Effect
   ```
   ```
   accept(suggestion: Suggestion) → Effect
      = apply(suggestion.content)
        feedback(positive, suggestion)
        model := update(model, context, suggestion, accepted)
   ```

3. **Reject Suggestion:**
   ```
   reject(suggestion: Suggestion) → Effect
   ```
   ```
   reject(suggestion: Suggestion) → Effect
      = dismiss(suggestion)
        feedback(negative, suggestion)
        model := update(model, context, suggestion, rejected)
   score(suggestion, context) = 
     w₁·relevance(suggestion, context)
     + w₂·confidence(suggestion)
     + w₃·frequency(suggestion, history)
     + w₄·recency(suggestion)
     - w₅·redundancy(suggestion, already_shown)
   ```

**Manifestations:**
- AI code suggestions (Copilot)
- Autocomplete
- Code actions (quick fixes)
- Tactic hints (Lean)
- Search suggestions

---

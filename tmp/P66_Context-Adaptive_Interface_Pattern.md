### P66. Context-Adaptive Interface Pattern

**Definition P66:**
A context-adaptive interface is a tuple $A = (U_{state}, T_{ctx}, T_{ui}, R_{adapt})$ where:
- $U_{state} : UserState$ tracks user context, behavior, and preferences
- $T_{ctx} : Context \to ContextVector$ transforms context into features
- $T_{ui} : UI \times ContextVector \to UI'$ transforms interface based on context
- $R_{adapt} : Rules$ defines adaptation strategies and constraints

**Type Definitions:**
```
UserState := (task: Task, expertise: Level, history: Sequence⟨Action⟩, preferences: Prefs)
ContextVector := Vector⟨ℝ⟩
Level := Novice | Intermediate | Expert
Task := (goal: Goal, phase: Phase, complexity: ℕ)
Adaptation := (target: UIElement, transform: Transform, priority: ℕ)
```

**Properties:**

**P.P66.1 (Context Sensitivity):**
```
∀ctx1, ctx2: ctx1 ≠ ctx2 ⇒ T_ui(UI, T_ctx(ctx1)) ≠ T_ui(UI, T_ctx(ctx2))
Different contexts produce different interfaces
```

**P.P66.2 (Graceful Adaptation):**
```
∀t: T_ui(UI(t), ctx(t)) → T_ui(UI(t+1), ctx(t+1))
Smooth transitions, no jarring changes
Animation and preview for major shifts
```

**P.P66.3 (User Override):**
```
∀adaptation ∈ Adaptations:
  user_can_reject(adaptation) ∨ user_can_lock(UI_element)
  Adaptation is assistive, not forced
```

**Operations:**

1. **Detect Context Change:**
   ```
   detect_change(state: UserState) → Context
   = current_ctx := T_ctx(state)
     if significant_change(current_ctx, prev_ctx):
       trigger_adaptation(current_ctx)
     prev_ctx := current_ctx
     return current_ctx
   ```

2. **Compute Adaptation:**
   ```
   compute_adaptation(ctx: Context, ui: UI) → Sequence⟨Adaptation⟩
   = features := T_ctx(ctx)
     candidates := []
     for element in ui:
       if should_adapt(element, features, R_adapt):
         transform := select_transform(element, features)
         priority := compute_priority(element, ctx)
         candidates.append(Adaptation(element, transform, priority))
     return sort_by_priority(candidates)
   ```

3. **Apply Adaptation:**
   ```
   apply(adaptations: Sequence⟨Adaptation⟩) → Effect
   = for adaptation in adaptations:
       if not user_locked(adaptation.target):
         preview := show_preview(adaptation)
         if auto_apply ∨ user_approves(preview):
           animate_transition(adaptation.target, adaptation.transform)
           apply_transform(adaptation.target, adaptation.transform)
   ```

**Specializations:**
- Expertise-based simplification/enhancement
- Task-phase interface adaptation
- Device/viewport responsive adaptation
- Accessibility adaptive interfaces

**Manifestations:**
- Microsoft Office ribbon context-aware tabs
- IDE context-aware code completion
- E-commerce personalized layouts
- Adaptive learning platforms
- AI-driven dashboard customization

---



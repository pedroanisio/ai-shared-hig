### P64. Generative UI Pattern

**Definition P64:**
A generative UI is a tuple $G = (T_{lib}, ctx, gen, render, stream)$ where:
- $T_{lib} : ComponentLibrary$ is the available UI component library
- $ctx : Context$ captures user state, task, and domain information
- $gen : Context \times T_{lib} \to ComponentTree$ generates UI structure from AI reasoning
- $render : ComponentTree \to UI$ instantiates components into interface
- $stream : TokenStream \to \Delta UI$ applies incremental updates during LLM generation

**Type Definitions:**
```
Context := (user: User, task: Task, domain: Domain, history: History)
ComponentTree := Tree⟨Component⟩
Component := (type: String, props: Props, children: Sequence⟨Component⟩)
TokenStream := Sequence⟨Token⟩
ΔUI := (operation: Insert | Update | Delete, target: Component, value: Component)
```

**Properties:**

**P.P64.1 (Dynamic Generation):**
```
∀ctx ∈ Context: gen(ctx, T_lib) produces UI optimized for ctx
UI adapts to user needs, not fixed templates
```

**P.P64.2 (Streaming Rendering):**
```
∀token ∈ stream: UI updates incrementally
Progressive disclosure during generation
No blocking wait for complete response
```

**P.P64.3 (Context-Aware Composition):**
```
∀c1, c2 ∈ ComponentTree:
  c1 ≠ c2 if context differs
  gen selects components based on task semantics
```

**Operations:**

1. **Generate UI from Context:**
   ```
   generate(ctx: Context) → ComponentTree
   = analysis := analyze_context(ctx)
     components := select_components(analysis, T_lib)
     tree := compose_tree(components, ctx)
     return tree
   ```

2. **Stream Component Updates:**
   ```
   stream_update(tokens: TokenStream) → Effect
   = for token in tokens:
       delta := interpret_token(token)
       apply_delta(delta)
       render_incremental(delta)
   ```

3. **Adapt to Context Change:**
   ```
   adapt(ctx_new: Context, ui_current: UI) → UI
   = diff := compute_context_diff(ctx_current, ctx_new)
     if requires_regeneration(diff):
       return generate(ctx_new)
     else:
       return patch_ui(ui_current, diff)
   ```

**Specializations:**
- Form generators (dynamic field selection)
- Dashboard composers (metric-driven layouts)
- Wizard flows (context-aware step generation)

**Manifestations:**
- Vercel AI SDK streamUI function
- OpenAI function calling for UI generation
- Anthropic Claude with UI components
- Custom LLM-to-React generators
- Dynamic form builders

---



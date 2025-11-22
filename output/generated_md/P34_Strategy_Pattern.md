### P34. Strategy Pattern

**Definition P34:**
$S = (interface, implementations, selector, current)$

- $implementations : Map⟨ID, Implementation⟩$ is concrete strategies
- $current : Implementation$ is active strategy

**Type Definitions:**
```
Interface := Set⟨MethodSignature⟩
Implementation := (id: ID, methods: Map⟨String, Function⟩)
Context := Map⟨String, Value⟩  // Decision criteria
```

**Properties:**

**P.P34.1 (Interface Compatibility):**
```
∀impl ∈ implementations: implements(impl, interface)
```

**P.P34.2 (Hot-Swappable):**
```
Can change strategy at runtime without recompilation
```

**Operations:**

1. **Select Strategy:**
   ```
   select_strategy(context: Context) → Implementation
   ```
   ```
   select_strategy(context: Context) → Implementation
      = id := selector(context)
        return implementations[id]
   ```

2. **Execute:**
   ```
   execute(method: String, args: Sequence⟨Value⟩) → Value
   ```
   ```
   execute(method: String, args: Sequence⟨Value⟩) → Value
      = return current.methods[method](args)
   ```

3. **Register Strategy:**
   ```
   register(impl: Implementation) → Effect
   ```
   ```
   register(impl: Implementation) → Effect
      = validate(impl, interface)
        implementations[impl.id] := impl
   ```

**Manifestations:**
- File format handlers
- Solver algorithms
- Rendering engines
- Compression algorithms

---

### P15. Reasoning Chain

**Definition P15:**
$R = (steps, state, deps, result)$

- $steps : Sequence⟨Step⟩$ is reasoning steps
- $result : Result$ is final conclusion

**Type Definitions:**
```
Step := (id: ℕ, operation: Operation, inputs: Set⟨ℕ⟩, output: Value)
Operation := Infer | Deduce | Calculate | Verify | ...
State := Map⟨String, Value⟩  // Variable bindings
```

**Properties:**

**P.P15.1 (Sequential Dependency):**
```
step_i depends on step_j ⇒ j < i (executed before)
```

**P.P15.2 (State Evolution):**
```
state[i+1] = apply(step[i], state[i])
```

**P.P15.3 (Conclusion Derivation):**
```
result derived from state[|steps|]
```

**Operations:**

1. **Add Step:**
   ```
   add_step(operation: Operation, inputs: Set⟨ℕ⟩) → ℕ
   ```
   ```
   add_step(operation: Operation, inputs: Set⟨ℕ⟩) → ℕ
      = step_id := |steps|
        step := Step(step_id, operation, inputs, unknown)
        steps := steps ++ [step]
        return step_id
   ```

2. **Execute Chain:**
   ```
   execute() → Result
   ```
   ```
   execute() → Result
      = state[0] := initial_state
        for i in 0..|steps|:
          input_values := {state[j][steps[j].output] : j ∈ steps[i].inputs}
          output := steps[i].operation(input_values)
          state[i+1] := state[i] ∪ {steps[i].output: output}
        return state[|steps|]
   ```

**Manifestations:**
- AI reasoning (chain-of-thought)
- Proof derivation
- Build pipelines
- Computation traces

---

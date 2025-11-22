### P11. Validator/Checker

**Definition P11:**
$V = (rules, input, report, severity)$

- $rules : Set⟨Rule⟩$ is validation rules
- $input : Data$ is data to validate
- $report : Sequence⟨Violation⟩$ is found violations

**Type Definitions:**
```
Rule := (name: String, check: Data → Sequence⟨Violation⟩)
Violation := (rule: Rule, location: Location, message: String)
Level := Error | Warning | Info
```

**Properties:**

**P.P11.1 (Completeness):**
```
All rules are checked for all applicable data
```

**P.P11.2 (Correctness):**
```
report contains only actual violations (no false positives)
```

**P.P11.3 (Actionability):**
```
Each violation includes location and fix suggestion
```

**Operations:**

1. **Validate:**
   ```
   validate(data: Data) → Report
   ```
   ```
   validate(data: Data) → Report
      = violations := []
        for rule in rules:
          violations := violations ++ rule.check(data)
        return Report(violations, sort_by_severity)
   ```

2. **Add Rule:**
   ```
   add_rule(rule: Rule, level: Level) → Effect
   ```
   ```
   add_rule(rule: Rule, level: Level) → Effect
      = rules := rules ∪ {rule}
        severity[rule] := level
   ```

**Manifestations:**
- Proof checkers (Lean, Coq)
- Type checkers
- Constraint validators
- Linters

---

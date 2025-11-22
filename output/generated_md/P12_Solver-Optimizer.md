### P12. Solver/Optimizer

**Definition P12:**
$S = (constraints, variables, objective, algorithm)$

- $constraints : Set⟨Constraint⟩$ is problem constraints
- $variables : Set⟨Variable⟩$ is decision variables
- $objective : Variables → ℝ$ is optimization objective (optional)
- $algorithm : Problem → Solution | Infeasible$ is solving algorithm

**Type Definitions:**
```
Constraint := (type: ConstraintType, expr: Expression)
ConstraintType := Equality | Inequality | Boundary
Variable := (name: String, domain: Domain, value: Value | Unknown)
Domain := Continuous(min, max) | Discrete(values: Set⟨Value⟩)
```

**Properties:**

**P.P12.1 (Soundness):**
```
solution satisfies all constraints ∨ return infeasible
```

**P.P12.2 (Optimality):**
```
If optimization: solution maximizes/minimizes objective (or is local optimum)
```

**P.P12.3 (Completeness):**
```
If solution exists, algorithm finds it (eventually)
```

**Operations:**

1. **Solve:**
   ```
   solve(problem: Problem) → Solution | Infeasible
   ```
   ```
   solve(problem: Problem) → Solution | Infeasible
      = assignment := algorithm(constraints, variables, objective)
        if verify(assignment, constraints):
          return Solution(assignment)
        else:
          return Infeasible
   ```

2. **Add Constraint:**
   ```
   add_constraint(c: Constraint) → Effect
   ```
   ```
   add_constraint(c: Constraint) → Effect
      = constraints := constraints ∪ {c}
        invalidate_cache()
   - SAT solvers (Boolean constraints)
   - SMT solvers (theories)
   - Linear programming (LP)
   - Constraint propagation
   - Backtracking search
   ```

**Manifestations:**
- Constraint solvers (CAD)
- Parametric solvers (engineering)
- Theorem provers (mathematics)
- Layout engines (CSS Grid)

---

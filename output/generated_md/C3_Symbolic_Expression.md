### C3. Symbolic Expression

**Definition C3:**
$T = (root, children)$

- $root : Symbol$ is root node (operator or value)
- $children : Sequence⟨Tree⟩$ is child expressions

**Properties:**

**P.C3.1 (Parseability):**
```
parse(serialize(T)) = T
```

**P.C3.2 (Evaluability):**
```
∀T, context: eval(T, context) → Value | Error
```

**P.C3.3 (Transformability):**
```
∃transform: simplify(T) = T' where semantics(T) = semantics(T')
∧ complexity(T') ≤ complexity(T)
```

**Operations:**

1. **Parse:**
   ```
   parse(s: String) → Tree | ParseError
   ```
   ```
   parse(s: String) → Tree | ParseError
      = construct AST from string representation
   ```

2. **Evaluate:**
   ```
   eval(T: Tree, context: Map⟨String,Value⟩) → Value
   ```
   ```
   eval(T: Tree, context: Map⟨String,Value⟩) → Value
      = case T.root of
          Literal(v) → v
          Variable(x) → context[x]
          Operator(op) → op(map(eval, T.children))
   ```

3. **Simplify:**
   ```
   simplify(T: Tree) → Tree
   ```
   ```
   simplify(T: Tree) → Tree
      = apply rewrite rules until fixpoint
   ```

**Manifestations:**
- Mathematical formulas (LaTeX, MathML)
- Code AST (Python, JavaScript)
- Constraints (SMT-LIB)
- Queries (SQL, GraphQL)
- Tags/taxonomies

---

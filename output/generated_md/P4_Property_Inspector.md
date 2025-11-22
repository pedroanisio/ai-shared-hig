### P4. Property Inspector

**Definition P4:**
$I = (selection, fields, validators, commit)$

- $selection : Element | null$ is inspected object
- $fields : Map⟨String, Field⟩$ is editable properties

**Properties:**

**P.P4.1 (Selection-Driven):**
```
selection changes → reload_fields(selection)
```

**P.P4.2 (Validation Before Commit):**
```
commit(field, value) succeeds ⇔ validators[field](value) = valid
```

**P.P4.3 (Immediate or Delayed Commit):**
```
Mode 1 (immediate): onChange → commit
Mode 2 (delayed): onChange → stage, onBlur → commit
```

**Operations:**

1. **Load Properties:**
   ```
   load(element: Element) → Map⟨String, Value⟩
   ```
   ```
   load(element: Element) → Map⟨String, Value⟩
      = {(k, v) : k ∈ properties(element), v = element[k]}
   ```

2. **Validate Field:**
   ```
   validate(field: String, value: Value) → ValidationResult
   ```
   ```
   validate(field: String, value: Value) → ValidationResult
      = validators[field](value)
   ```

3. **Commit Change:**
   ```
   commit(field: String, value: Value) → Effect
   ```
   ```
   commit(field: String, value: Value) → Effect
      = if validate(field, value) = valid:
          selection[field] := value
          update_dependents(field)
          notify_observers(selection)
   ```

**Manifestations:**
- Properties panel (design tools)
- Inspector (browser DevTools)
- Settings panel (applications)
- Attributes editor (HTML editors)

---

### P50. Form Dependency Pattern

**Definition P50:**
$D = (fields, deps, update, cascade)$

- $fields : Map⟨String, Field⟩$ is form fields

**Type Definitions:**
```
Dependency := (source: String, targets: Set⟨String⟩,
```

**Properties:**

**P.P50.1 (Dependency Graph):**
```
deps forms a DAG (no circular dependencies)
```

**P.P50.2 (Automatic Updates):**
```
change(field_A) ∧ field_B ∈ deps[field_A] ⇒ update(field_B)
```

**P.P50.3 (Conditional Visibility):**
```
visible(field) = evaluate(visibility_condition, form_data)
```

**P.P50.4 (Value Computation):**
```
computed_field.value = compute(dependencies.values)
```

**Operations:**

1. **Register Dependency:**
   ```
   add_dependency(source: String, target: String, rule: Rule) → Effect
   ```
   ```
   add_dependency(source: String, target: String, rule: Rule) → Effect
      = deps[source] := deps[source] ∪ {target}
        rules[(source, target)] := rule
        validate_acyclic(deps)
   ```

2. **Update Field:**
   ```
   update_field(field: String, value: Value) → Effect
   ```
   ```
   update_field(field: String, value: Value) → Effect
      = fields[field].value := value
        if cascade:
          for target in deps[field]:
            rule := rules[(field, target)]
            new_value := rule(value)
            update_field(target, new_value)
   ```

3. **Compute Derived Value:**
   ```
   compute_derived(field: String) → Value
   ```
   ```
   compute_derived(field: String) → Value
      = sources := {f : field ∈ deps[f]}
        values := map(sources, λf: fields[f].value)
        compute_function[field](values)
   ```

4. **Conditional Visibility:**
   ```
   Field "Other" visible only if "Category" = "Other"
      deps["category"] := {"other_field"}
      rules[("category", "other_field")] := 
        λval: {visible: val = "Other"}
   ```

5. **Value Computation:**
   ```
   Total = Subtotal + Tax
      deps["subtotal"] := {"total"}
      deps["tax"] := {"total"}
      rules[("subtotal"|"tax", "total")] := 
        λ_: subtotal + tax
   ```

6. **Cascading Defaults:**
   ```
   Country → State → City
   ```
   ```
   Country → State → City
      Changing country resets state and city
      Changing state resets city
   ```

7. **Dynamic Options:**
   ```
   Category → Subcategory options
   ```
   ```
   Category → Subcategory options
      deps["category"] := {"subcategory"}
      rules[("category", "subcategory")] := 
        λcat: {options: get_subcategories(cat)}
   ```

**Manifestations:**
- Address forms (country→state→city)
- Product configurators
- Tax calculators
- Dynamic pricing forms
- Conditional survey questions

---

### P48. Form Validation Pattern

**Definition P48:**
$V = (fields, rules, state, errors)$

- $fields : Map⟨String, Field⟩$ is form fields
- $rules : Map⟨String, Validator⟩$ is validation rules

**Type Definitions:**
```
Field := (value: Value, dirty: 𝔹, touched: 𝔹)
Validator := Value → ValidationResult
ValidationResult := Valid | Invalid(errors: Sequence⟨String⟩)
ValidationState := Pristine | Valid | Invalid | Validating
```

**Properties:**

**P.P48.1 (Eager Validation):**
```
field.dirty ∧ field.touched ⇒ validate(field) on change
```

**P.P48.2 (Form-Level Validation):**
```
valid(form) ⇔ ∀f ∈ fields: state[f] ∈ {Valid, Pristine}
```

**P.P48.3 (Async Validation):**
```
validate_async(field) → ValidationResult (eventually)
state[field] = Validating during execution
```

**P.P48.4 (Cross-Field Validation):**
```
validate_group([field₁, field₂, ...]) → ValidationResult
Example: password confirmation
```

**Operations:**

1. **Validate Field:**
   ```
   validate(field_name: String) → ValidationResult
   ```
   ```
   validate(field_name: String) → ValidationResult
      = value := fields[field_name].value
        validator := rules[field_name]
        result := validator(value)
        state[field_name] := case result of
          Valid → Valid
          Invalid(errs) → Invalid
        errors[field_name] := result.errors
        return result
   ```

2. **Validate Form:**
   ```
   validate_form() → 𝔹
   ```
   ```
   validate_form() → 𝔹
      = results := map(keys(fields), validate)
        return all(results, λr: r = Valid)
   ```

3. **Register Rule:**
   ```
   register_rule(field: String, rule: Validator) → Effect
   ```
   ```
   register_rule(field: String, rule: Validator) → Effect
      = rules[field] := compose_validators(rules[field], rule)
   ```

4. **Built-in Validators:**
   ```
   required(value: Value) → ValidationResult
   ```
   ```
   required(value: Value) → ValidationResult
      = if value ≠ null ∧ value ≠ "":
          Valid
        else:
          Invalid(["This field is required"])
      min_length(n: ℕ) → Validator
      = λvalue: if length(value) ≥ n:
                  Valid
                else:
                  Invalid([f"Minimum length is {n}"])
      email(value: String) → ValidationResult
      = if matches(value, email_regex):
          Valid
        else:
          Invalid(["Invalid email address"])
      custom(predicate: Value → 𝔹, message: String) → Validator
      = λvalue: if predicate(value):
                  Valid
                else:
                  Invalid([message])
   ```

5. **On Submit:**
   ```
   Validate all fields when form submitted
      Show all errors at once
   ```

6. **On Blur:**
   ```
   Validate field when it loses focus
      Show errors immediately
   ```

7. **On Change:**
   ```
   Validate field on every keystroke
      Show errors after field touched
   ```

8. **Hybrid (Recommended):**
   ```
   First error: on blur
      Subsequent: on change (immediate feedback)
   ```

**Manifestations:**
- Registration forms
- Login forms
- Settings panels
- Data entry forms
- Survey forms

---

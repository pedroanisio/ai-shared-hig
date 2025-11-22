### P60. Input Sanitization Pattern

**Definition P60:**
$S = (validators, sanitizers, encoders, rules)$

**Type Definitions:**
```
InputType := Text | HTML | SQL | URL | Email | ...
Validator := Input → ValidationResult
Sanitizer := Input → SanitizedInput
Encoder := Input → EncodedOutput
SecurityRule := (pattern: Regex, action: Block | Sanitize | Warn)
```

**Properties:**

**P.P60.1 (Defense in Depth):**
```
Multiple layers: validate → sanitize → encode
```

**P.P60.2 (Whitelist Over Blacklist):**
```
Allow known-good patterns rather than blocking known-bad
```

**P.P60.3 (Context-Appropriate Encoding):**
```
HTML context → HTML encode
SQL context → Parameterized queries
URL context → URL encode
```

**Operations:**

1. **Validate Input:**
   ```
   validate(input: Input, type: InputType) → ValidationResult
   ```
   ```
   validate(input: Input, type: InputType) → ValidationResult
      = validator := validators[type]
        result := validator(input)
        if result = Invalid:
          log_security_event("Invalid input", input, type)
        return result
   ```

2. **Sanitize Input:**
   ```
   sanitize(input: Input, type: InputType) → Input
   ```
   ```
   sanitize(input: Input, type: InputType) → Input
      = sanitizer := sanitizers[type]
        return sanitizer(input)
   ```

3. **Encode Output:**
   ```
   encode(input: Input, context: Context) → String
   ```
   ```
   encode(input: Input, context: Context) → String
      = encoder := encoders[context]
        return encoder(input)
   ```

4. **XSS (Cross-Site Scripting):**
   ```
   Vulnerability: <script>alert('xss')</script>
      Defense:
        - Validate: Allow only expected characters
        - Sanitize: Remove script tags
        - Encode: &lt;script&gt; in HTML context
      encode_html(text: String) → String
      = replace(text, [
          ("<", "&lt;"),
          (">", "&gt;"),
          ("&", "&amp;"),
          ("\"", "&quot;"),
          ("'", "&#x27;")
        ])
   ```

5. **SQL Injection:**
   ```
   Vulnerability: '; DROP TABLE users; --
      Defense:
        - Use parameterized queries (prepared statements)
        - Never concatenate user input into SQL
        - Validate input type
      Safe:
        query = "SELECT * FROM users WHERE id = ?"
        execute(query, [user_input])
      Unsafe:
        query = "SELECT * FROM users WHERE id = " + user_input
   ```

6. **Path Traversal:**
   ```
   Vulnerability: ../../etc/passwd
      Defense:
        - Validate: Only allow alphanumeric + safe chars
        - Sanitize: Remove .. and /
        - Use whitelist of allowed paths
      sanitize_path(path: String) → String
      = normalized := normalize(path)
        if contains(normalized, "..") ∨ starts_with(normalized, "/"):
          throw SecurityException("Invalid path")
        return join(base_dir, normalized)
   ```

7. **Command Injection:**
   ```
   Vulnerability: ; rm -rf /
      Defense:
        - Never pass user input to shell
        - Use language APIs instead of shell commands
        - Validate against whitelist
      Safe:
        delete_file(filename)  // Use API
      Unsafe:
        exec("rm " + filename)  // Shell command
   ```

8. **LDAP Injection:**
   ```
   Vulnerability: *)(uid=*))(|(uid=*
      Defense:
        - Escape special characters: * ( ) \ / NUL
        - Use parameterized LDAP queries
      escape_ldap(input: String) → String
      = replace(input, [
          ("*", "\\2a"),
          ("(", "\\28"),
          (")", "\\29"),
          ("\\", "\\5c"),
          ("/", "\\2f")
        ])
   Email:
     pattern: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
   URL:
     pattern: ^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$
     validate_protocol: must be http or https
   Username:
     pattern: ^[a-zA-Z0-9_-]{3,20}$
     length: 3-20 characters
     chars: alphanumeric, underscore, hyphen
   Phone:
     pattern: ^\+?[1-9]\d{1,14}$
     format: E.164 international format
   ```

**Manifestations:**
- Form input validation
- API input sanitization
- Template rendering (auto-escaping)
- Database query builders

---

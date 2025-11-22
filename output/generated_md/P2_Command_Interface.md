### P2. Command Interface

**Definition P2:**
$I = (input, parser, executor, history)$

- $input : String$ is command text
- $history : Sequence⟨String⟩$ is command history

**Properties:**

**P.P2.1 (Parse-Execute Cycle):**
```
input → parse → validate → execute → feedback
```

**P.P2.2 (History Navigation):**
```
↑ key → previous(history)
↓ key → next(history)
```

**P.P2.3 (Autocomplete):**
```
partial_input → suggest(completions)
where completions ⊆ valid_commands
```

**Operations:**

1. **Parse Command:**
   ```
   parse(s: String) → Command | ParseError
   ```
   ```
   parse(s: String) → Command | ParseError
      = tokenize(s) → match_pattern → construct_command
   ```

2. **Execute:**
   ```
   execute(cmd: Command) → Result
   ```
   ```
   execute(cmd: Command) → Result
      = case cmd.type of
          Search(query) → search_engine(query)
          Create(type) → create_object(type)
          Delete(id) → delete_object(id)
   ```

3. **Suggest Completions:**
   ```
   suggest(partial: String) → Sequence⟨String⟩
   ```
   ```
   suggest(partial: String) → Sequence⟨String⟩
      = filter(valid_commands, λc: startsWith(c, partial))
        → sort_by_frequency
        → take(10)
   ```

**Manifestations:**
- Search bar (Google, Spotlight)
- Command line (Terminal, bash)
- Command palette (VS Code Ctrl+Shift+P)
- Query input (SQL clients)

---

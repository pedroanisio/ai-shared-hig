### P30. Command Pattern

**Definition P30:**
$C = (commands, executor, undo\_stack, redo\_stack)$

- $commands : Sequence⟨Command⟩$ is executed commands

**Type Definitions:**
```
Command := (execute: () → Effect, undo: () → Effect, redo: () → Effect)
```

**Properties:**

**P.P30.1 (Reversibility):**
```
∀cmd: undo(execute(cmd)) returns to pre-execution state
```

**P.P30.2 (Command History):**
```
All executed commands pushed to undo_stack
```

**P.P30.3 (Redo Invalidation):**
```
New command execution → clear redo_stack
```

**Operations:**

1. **Execute:**
   ```
   execute(cmd: Command) → Effect
   ```
   ```
   execute(cmd: Command) → Effect
      = cmd.execute()
        undo_stack := push(undo_stack, cmd)
        redo_stack := empty()  // Clear redo on new action
   ```

2. **Undo:**
   ```
   undo() → Effect
   ```
   ```
   undo() → Effect
      = if ¬empty(undo_stack):
          cmd := pop(undo_stack)
          cmd.undo()
          redo_stack := push(redo_stack, cmd)
   ```

3. **Redo:**
   ```
   redo() → Effect
   ```
   ```
   redo() → Effect
      = if ¬empty(redo_stack):
          cmd := pop(redo_stack)
          cmd.redo()
          undo_stack := push(undo_stack, cmd)
   ```

**Manifestations:**
- Undo/redo system
- Macro recording
- Transaction log
- Command history

---

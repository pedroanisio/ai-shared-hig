### P23. Real-Time Sync

**Definition P23:**
$S = (local, remote, diff, merge, conflicts)$

- $local : State$ is local state
- $remote : State$ is remote state

**Type Definitions:**
```
State := Map⟨Path, Value⟩  // Complete state snapshot
Delta := Sequence⟨Change⟩  // Incremental changes
Conflict := (path: Path, local_value: Value, remote_value: Value)
```

**Properties:**

**P.P23.1 (Eventual Consistency):**
```
After quiescence: local = remote
```

**P.P23.2 (Conflict Resolution):**
```
Concurrent changes → detect conflicts → resolve
```

**P.P23.3 (Efficient Sync):**
```
Only send deltas, not full state
```

**Operations:**

1. **Compute Delta:**
   ```
   diff(old: State, new: State) → Delta
   ```
   ```
   diff(old: State, new: State) → Delta
      = changes := []
        for path in keys(old) ∪ keys(new):
          if old[path] ≠ new[path]:
            changes := changes ++ [Change(path, old[path], new[path])]
        return changes
   ```

2. **Apply Delta:**
   ```
   merge(state: State, delta: Delta) → State
   ```
   ```
   merge(state: State, delta: Delta) → State
      = for change in delta:
          if ¬conflict(change, state):
            state[change.path] := change.new_value
          else:
            conflicts := conflicts ++ [Conflict(change.path, state[change.path], change.new_value)]
        return state
   ```

3. **Resolve Conflict:**
   ```
   resolve(conflict: Conflict, strategy: Strategy) → Value
   ```
   ```
   resolve(conflict: Conflict, strategy: Strategy) → Value
      = case strategy of
          LastWriteWins → newer(conflict.local_value, conflict.remote_value)
          ManualResolve → prompt_user(conflict)
          MergeValues → merge_function(conflict.local_value, conflict.remote_value)
   ```

4. **Polling:**
   ```
   Every τ seconds: fetch remote, diff, merge
      Simple but wasteful
   ```

5. **WebSocket:**
   ```
   Persistent connection, push updates
      Real-time, efficient
   ```

6. **Operational Transformation:**
   ```
   Transform operations to account for concurrent edits
      Complex but powerful
   ```

**Manifestations:**
- Collaborative editing
- Live preview
- Cloud sync (Dropbox)
- Multi-device sync

---

### P17. Key-Value Store

**Definition P17:**
$K = (store, get, set, delete)$

- $store : Map⟨Key, Value⟩$ is storage

**Properties:**

**P.P17.1 (Fast Lookup):**
```
get(key) completes in O(1) average time
```

**P.P17.2 (Atomic Operations):**
```
set and delete are atomic
```

**Operations:**

1. **Get:**
   ```
   get(key: Key) → Value | null
   ```
   ```
   get(key: Key) → Value | null
      = store[key] if key ∈ keys(store) else null
   ```

2. **Set:**
   ```
   set(key: Key, value: Value) → Effect
   ```
   ```
   set(key: Key, value: Value) → Effect
      = store[key] := value
   ```

3. **Delete:**
   ```
   delete(key: Key) → Effect
   ```
   ```
   delete(key: Key) → Effect
      = store := store ∖ {key}
   ```

**Manifestations:**
- Cache
- Settings storage
- Session state
- Metadata store

---

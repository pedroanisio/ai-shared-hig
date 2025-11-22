### P56. Cache Strategy Pattern

**Definition P56:**
$C = (storage, policy, ttl, evict)$

- $storage : Map⟨Key, (Value, Metadata)⟩$ is cache store

**Type Definitions:**
```
EvictionPolicy := LRU | LFU | FIFO | TTL | Custom
Metadata := (last_accessed: Time, access_count: ℕ, inserted: Time)
Duration := ℕ  // milliseconds
```

**Properties:**

**P.P56.1 (Bounded Size):**
```
|storage| ≤ max_size
```

**P.P56.2 (Cache Hit):**
```
get(key) → O(1) if key ∈ storage
```

**P.P56.3 (Automatic Eviction):**
```
|storage| = max_size ∧ insert(new_key) → evict() → insert(new_key)
```

**Operations:**

1. **Get (with Cache-Through):**
   ```
   get(key: Key, load: () → Value) → Value
   ```
   ```
   get(key: Key, load: () → Value) → Value
      = if key ∈ storage ∧ ¬expired(key):
          update_metadata(key)
          return storage[key].value
        else:
          value := load()
          set(key, value)
          return value
   ```

2. **Set:**
   ```
   set(key: Key, value: Value) → Effect
   ```
   ```
   set(key: Key, value: Value) → Effect
      = if |storage| = max_size:
          evict()
        storage[key] := (value, Metadata(now(), 0, now()))
   ```

3. **Evict:**
   ```
   evict() → Effect
   ```
   ```
   evict() → Effect
      = victim := select_victim(policy)
        delete storage[victim]
      select_victim(LRU) = key with oldest last_accessed
      select_victim(LFU) = key with lowest access_count
      select_victim(TTL) = oldest expired key
   ```

4. **Cache-Aside:**
   ```
   Application checks cache
      On miss: load from DB, populate cache
      On hit: return cached value
   ```

5. **Read-Through:**
   ```
   Cache automatically loads on miss
      Application only talks to cache
   ```

6. **Write-Through:**
   ```
   Writes go to cache and DB simultaneously
      Ensures consistency
   ```

7. **Write-Behind:**
   ```
   Writes go to cache immediately
      Async writeback to DB
      Better write performance
   ```

**Manifestations:**
- Browser cache
- CDN caching
- Database query cache
- Computed value cache
- Image thumbnails

---

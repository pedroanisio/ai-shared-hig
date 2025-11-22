### P31. Observer Pattern

**Definition P31:**
$O = (subject, observers, notify)$

- $subject : Subject$ is observed object
- $observers : Set⟨Observer⟩$ is listeners

**Type Definitions:**
```
Subject := (state: State, attach: Observer → Effect, detach: Observer → Effect)
Observer := (update: State → Effect)
```

**Properties:**

**P.P31.1 (Loose Coupling):**
```
Subject doesn't know observer details
Observers independent of each other
```

**P.P31.2 (Automatic Updates):**
```
subject.state changes → notify_all_observers()
```

**Operations:**

1. **Attach Observer:**
   ```
   attach(observer: Observer) → Effect
   ```
   ```
   attach(observer: Observer) → Effect
      = observers := observers ∪ {observer}
   ```

2. **Detach Observer:**
   ```
   detach(observer: Observer) → Effect
   ```
   ```
   detach(observer: Observer) → Effect
      = observers := observers ∖ {observer}
   ```

3. **Notify:**
   ```
   notify() → Effect
   ```
   ```
   notify() → Effect
      = for observer in observers:
          observer.update(subject.state)
   ```

**Manifestations:**
- Data binding
- Event listeners
- Reactive subscriptions
- Pub/sub systems

---

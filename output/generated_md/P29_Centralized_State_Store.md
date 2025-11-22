### P29. Centralized State Store

**Definition P29:**
$S = (store, reducers, selectors, subscriptions)$

- $store : State$ is application state (single source of truth)

**Type Definitions:**
```
State := Map⟨String, Value⟩
Action := (type: String, payload: Value)
Reducer := (State, Action) → State
Selector := State → Value
Subscriber := State → Effect
```

**Properties:**

**P.P29.1 (Single Source of Truth):**
```
∃! store: all application state in store
```

**P.P29.2 (Immutable Updates):**
```
reducer(state, action) returns new state, doesn't mutate old state
```

**P.P29.3 (Unidirectional Flow):**
```
action → reducer → new_state → notify_subscribers
```

**Operations:**

1. **Dispatch Action:**
   ```
   dispatch(action: Action) → Effect
   ```
   ```
   dispatch(action: Action) → Effect
      = reducer := reducers[action.type]
        new_state := reducer(store, action)
        store := new_state
        notify_all_subscribers(store)
   ```

2. **Subscribe:**
   ```
   subscribe(subscriber: Subscriber) → UnsubscribeFunc
   ```
   ```
   subscribe(subscriber: Subscriber) → UnsubscribeFunc
      = subscriptions := subscriptions ∪ {subscriber}
        return λ: subscriptions := subscriptions ∖ {subscriber}
   ```

3. **Select:**
   ```
   select(selector_name: String) → Value
   ```
   ```
   select(selector_name: String) → Value
      = selector := selectors[selector_name]
        return selector(store)
   ```

**Manifestations:**
- Redux (JavaScript)
- Vuex (Vue.js)
- Global state (any framework)
- Application model

---

### F6. Error Recovery Flow

**Definition F6:**
An error recovery flow is a tuple $E = (detect, classify, strategy, recover)$ where:
- $detect : Operation → Error | Success$ catches errors
- $classify : Error → ErrorType$ determines error category
- $strategy : ErrorType → RecoveryStrategy$ selects recovery approach
- $recover : (Error, RecoveryStrategy) → Effect$ executes recovery

**Type Definitions:**
```
ErrorType := Transient | Permanent | Recoverable
RecoveryStrategy := Retry(max: ℕ, backoff: Time → Time) | 
                   Fallback(alternative: Operation) | 
                   CircuitBreaker(timeout: Time) | 
                   GracefulDegradation(levels: Sequence⟨Mode⟩) |
                   Report(message: String)
Operation := () → Result | Error
```

**Properties:**

**P.F6.1 (Error Classification):**
```
∀e ∈ Error: classify(e) determines appropriate recovery strategy
Transient → Retry
Permanent → Report
Recoverable → Fallback | GracefulDegradation
```

**P.F6.2 (Recovery Exhaustion):**
```
∀recovery_attempt: attempts ≤ max_attempts ∨ escalate(error)
```

**P.F6.3 (State Safety):**
```
∀e ∈ Error: recover(e) preserves system invariants
No partial state corruption
```

**Operations:**

1. **Retry with Backoff:**
   ```
   retry(operation: Operation, max_attempts: ℕ) → Result | Error
   = attempts := 0
     while attempts < max_attempts:
       try:
         return operation()
       catch error:
         if transient(error):
           wait(2^attempts · base_delay)
           attempts := attempts + 1
         else:
           throw error
     throw MaxAttemptsExceeded
   ```

2. **Circuit Breaker:**
   ```
   circuit_breaker(operation: Operation, threshold: ℕ) → Result | Error
   = state := Closed
     failures := 0
     
     execute():
       case state of
         Closed → 
           try:
             result := operation()
             failures := 0
             return result
           catch error:
             failures := failures + 1
             if failures ≥ threshold:
               state := Open
               schedule_half_open(timeout)
             throw error
         Open → throw CircuitOpenError
         HalfOpen →
           try:
             result := operation()
             state := Closed
             return result
           catch error:
             state := Open
             throw error
   ```

3. **Graceful Degradation:**
   ```
   degrade(levels: Sequence⟨Mode⟩, operation: Mode → Result) → Result
   = for mode in levels:
       try:
         return operation(mode)
       catch error:
         continue
     throw AllModesFailedError
   ```

**Manifestations:**
- Network request retry (HTTP clients with backoff)
- File load fallback (multiple locations/mirrors)
- Service degradation (cache → static → error)
- Database connection pooling (retry on transient failures)
- User retry prompts (try again button)

---


### P61. Unit Test Pattern

**Definition P61:**
$U = (sut, arrange, act, assert, cleanup)$

- $sut : System$ is **system under test** (unit being tested)

**Type Definitions:**
```
System := Function | Class | Module
Context := (mocks: Set⟨Mock⟩, fixtures: Set⟨Fixture⟩, state: State)
Mock := (target: Dependency, behavior: Specification)
Fixture := (data: Data, setup: () → Effect, teardown: () → Effect)
```

**Properties:**

**P.P61.1 (Isolation):**
```
Unit tests run independently
No shared state between tests
```

**P.P61.2 (Fast Execution):**
```
Unit tests complete in milliseconds
No I/O, network, or database
```

**P.P61.3 (Repeatability):**
```
Same input → same output (deterministic)
```

**Manifestations:**
- Unit tests (pytest, Jest, JUnit)
- TDD (Test-Driven Development)
- Component tests
- Function tests

---

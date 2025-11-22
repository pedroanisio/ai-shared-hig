### P62. Integration Test Pattern

**Definition P62:**
$I = (components, interactions, environment, verify)$

- $components : Set⟨Component⟩$ is integrated components
- $interactions : Sequence⟨Interaction⟩$ is component communications
- $environment : Environment$ is test environment (DB, API, etc.)

**Type Definitions:**
```
Component := Service | Module | System
Interaction := (from: Component, to: Component, message: Message)
Environment := (database: DB, services: Set⟨Service⟩, config: Config)
```

**Properties:**

**P.P62.1 (Multiple Components):**
```
Tests interaction between ≥2 real components
```

**P.P62.2 (External Dependencies):**
```
May use real databases, APIs, file systems
Or test doubles (test DB, mock APIs)
```

**Manifestations:**
- API integration tests
- Database integration tests
- Service-to-service tests
- End-to-end user flows

---

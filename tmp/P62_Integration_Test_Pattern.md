### P62. Integration Test Pattern

**Definition P62:**
An integration test is a tuple $I = (components, interactions, environment, verify)$ where:
- $components : Set⟨Component⟩$ are integrated components
- $interactions : Sequence⟨Interaction⟩$ are component communications
- $environment : Environment$ is test environment (DB, API, etc.)
- $verify : () → \mathbb{B}$ checks end-to-end behavior

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

**P.P62.3 (Slower Than Unit Tests):**
```
Execution time: seconds (vs milliseconds for unit tests)
```

**Operations:**

1. **Setup Environment:**
   ```
   setup_environment() → Environment
   = db := create_test_database()
     services := start_test_services()
     config := load_test_config()
     return Environment(db, services, config)
   ```

2. **Execute Integration Test:**
   ```
   execute_integration(test: IntegrationTest, env: Environment) → TestResult
   = setup_data(env.database)
     result := test.run(env)
     verify_state(env)
     return result
   ```

3. **Teardown Environment:**
   ```
   teardown(env: Environment) → Effect
   = env.database.drop()
     env.services.stop()
     cleanup_test_data()
   ```

**Test Structure:**

```
integration_test_user_registration()
  // Setup environment
  = test_db := create_test_database()
    api_client := create_api_client()
    email_service := create_mock_email_service()
    
    // Execute integration flow
    response := api_client.post("/register", {
      username: "newuser",
      email: "new@example.com",
      password: "secure123"
    })
    
    // Verify database state
    user := test_db.query("SELECT * FROM users WHERE username = ?", ["newuser"])
    assert(user ≠ null)
    assert(user.email = "new@example.com")
    
    // Verify email sent
    assert(email_service.sent_count = 1)
    assert(email_service.last_email.to = "new@example.com")
    
    // Cleanup
    test_db.drop()
```

**Integration Strategies:**

1. **Top-Down:**
   ```
   Test from UI/API downward
   Mock lower-level dependencies
   Gradually replace mocks with real implementations
   ```

2. **Bottom-Up:**
   ```
   Test lower-level components first
   Combine into higher-level tests
   Build up to full system
   ```

3. **Big Bang:**
   ```
   Integrate all components at once
   Test entire system
   Risky but fast
   ```

4. **Sandwich (Hybrid):**
   ```
   Test top and bottom layers separately
   Integrate middle layer
   Combine all
   ```

**Test Doubles:**

5. **Stub:**
   ```
   Provides canned responses
   No verification
   
   email_stub := Stub(EmailService)
   email_stub.send() → Success  // Always succeeds
   ```

6. **Mock:**
   ```
   Verifies interactions
   Records calls
   
   email_mock := Mock(EmailService)
   email_mock.send(to, subject, body)
   verify(email_mock.send).called_with("test@example.com", *, *)
   ```

7. **Fake:**
   ```
   Working implementation with shortcuts
   Example: In-memory database
   
   fake_db := InMemoryDatabase()  // Real behavior, no persistence
   ```

8. **Spy:**
   ```
   Real object with recording
   Tracks method calls
   
   email_spy := Spy(RealEmailService)
   email_spy.send(...)  // Actually sends, but records call
   verify(email_spy.send).called()
   ```

**Test Database Strategies:**

```
1. In-Memory Database:
   test_db := SQLite(":memory:")
   Fast but limited features

2. Docker Container:
   test_db := Docker.run("postgres:13")
   Real DB, isolated, clean slate

3. Transaction Rollback:
   begin_transaction()
   run_test()
   rollback()  // Undo all changes

4. Fixtures:
   load_fixtures("test_data.sql")
   run_test()
   truncate_tables()
```

**Manifestations:**
- API integration tests
- Database integration tests
- Service-to-service tests
- End-to-end user flows

---


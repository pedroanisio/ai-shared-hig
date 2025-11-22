### P61. Unit Test Pattern

**Definition P61:**
A unit test is a tuple $U = (sut, arrange, act, assert, cleanup)$ where:
- $sut : System$ is the **system under test** (unit being tested)
- $arrange : () → Context$ sets up test preconditions
- $act : Context → Result$ exercises the unit
- $assert : Result → \mathbb{B}$ verifies expectations
- $cleanup : Context → Effect$ tears down test state

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

**P.P61.4 (Single Assertion Focus):**
```
Each test verifies one behavior
Clear failure messages
```

**Operations:**

1. **Execute Test:**
   ```
   execute_test(test: Test) → TestResult
   = context := test.arrange()
     result := test.act(context)
     passed := test.assert(result)
     test.cleanup(context)
     return TestResult(passed, result, context)
   ```

2. **Run Test Suite:**
   ```
   run_suite(tests: Set⟨Test⟩) → SuiteResult
   = results := []
     for test in tests:
       result := execute_test(test)
       results := results ∪ {result}
     return SuiteResult(results, summary(results))
   ```

3. **Mock Dependency:**
   ```
   mock(dependency: Dependency, behavior: Specification) → Mock
   = mock := Mock(dependency)
     configure(mock, behavior)
     return mock
   ```

**Test Structure (Arrange-Act-Assert):**

```
test_addition() → 𝔹
  // Arrange: Set up test data
  = calculator := Calculator()
    a := 2
    b := 3
    expected := 5
    
    // Act: Exercise the unit
    result := calculator.add(a, b)
    
    // Assert: Verify expectations
    assert(result = expected, "2 + 3 should equal 5")
    
    // Cleanup (if needed)
    cleanup()
```

**Mocking:**

```
Mock dependency behavior:
  mock_database := Mock(Database)
  mock_database.when(get_user(1)).then_return(User(1, "Alice"))
  
  service := UserService(mock_database)
  user := service.get_user(1)
  
  assert(user.name = "Alice")
  verify(mock_database.get_user).called_once_with(1)
```

**Test Patterns:**

1. **Given-When-Then (BDD style):**
   ```
   test_user_login()
     Given: user exists with username "alice" and password "secret"
     When: user logs in with correct credentials
     Then: login succeeds and session is created
   ```

2. **Table-Driven Tests:**
   ```
   test_cases := [
     (input: 2, expected: 4),
     (input: 3, expected: 9),
     (input: 4, expected: 16)
   ]
   
   for (input, expected) in test_cases:
     result := square(input)
     assert(result = expected)
   ```

3. **Parameterized Tests:**
   ```
   @parameterized([
     (2, 3, 5),
     (10, 5, 15),
     (-1, 1, 0)
   ])
   test_addition(a, b, expected)
     result := add(a, b)
     assert(result = expected)
   ```

**Common Assertions:**

```
assert_equal(actual, expected)
assert_not_equal(actual, not_expected)
assert_true(condition)
assert_false(condition)
assert_null(value)
assert_not_null(value)
assert_contains(collection, item)
assert_raises(exception_type, callable)
assert_almost_equal(actual, expected, tolerance)
```

**Manifestations:**
- Unit tests (pytest, Jest, JUnit)
- TDD (Test-Driven Development)
- Component tests
- Function tests

---


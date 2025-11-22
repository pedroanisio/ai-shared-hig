### P63. End-to-End Test Pattern

**Definition P63:**
$E = (scenario, browser, pages, assertions, data)$

- $scenario : UserStory$ is user scenario being tested
- $browser : Browser$ is automated browser
- $data : TestData$ is test data for the scenario

**Type Definitions:**
```
UserStory := (actor: Actor, action: Action, outcome: Outcome)
Browser := (driver: WebDriver, capabilities: Set⟨Capability⟩)
PageObject := (locators: Map⟨String, Locator⟩, actions: Map⟨String, Action⟩)
Locator := CSS(selector: String) | XPath(expression: String) | ID(id: String)
```

**Properties:**

**P.P63.1 (Full System):**
```
Tests complete system from user perspective
Real browser, real UI, real backend
```

**P.P63.2 (User Scenarios):**
```
Tests realistic user workflows
Example: Register → Login → Purchase → Logout
```

**Manifestations:**
- UI automation (Selenium, Playwright, Cypress)
- Acceptance tests
- Smoke tests
- Regression tests

---

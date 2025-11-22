### P63. End-to-End Test Pattern

**Definition P63:**
An E2E test is a tuple $E = (scenario, browser, pages, assertions, data)$ where:
- $scenario : UserStory$ is the user scenario being tested
- $browser : Browser$ is the automated browser
- $pages : Map⟨String, PageObject⟩$ represent UI pages
- $assertions : Sequence⟨Assertion⟩$ verify expected outcomes
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

**P.P63.3 (Slowest Tests):**
```
Execution time: seconds to minutes
Run less frequently than unit/integration tests
```

**Operations:**

1. **Launch Browser:**
   ```
   launch_browser(config: BrowserConfig) → Browser
   = driver := create_webdriver(config.type, config.capabilities)
     browser := Browser(driver, config)
     return browser
   ```

2. **Execute Scenario:**
   ```
   execute_scenario(scenario: UserStory, browser: Browser) → TestResult
   = pages := load_page_objects(browser)
     for step in scenario.steps:
       execute_step(step, pages, browser)
     results := verify_assertions(scenario.assertions)
     return TestResult(results)
   ```

3. **Cleanup Session:**
   ```
   cleanup(browser: Browser) → Effect
   = browser.delete_cookies()
     browser.clear_local_storage()
     browser.quit()
   ```

**Page Object Pattern:**

```
Page objects encapsulate UI structure:

class LoginPage:
  locators = {
    username_input: CSS("#username"),
    password_input: CSS("#password"),
    login_button: CSS("button[type=submit]"),
    error_message: CSS(".error")
  }
  
  def login(username: String, password: String) → Effect:
    this.find(username_input).type(username)
    this.find(password_input).type(password)
    this.find(login_button).click()
  
  def get_error() → String:
    return this.find(error_message).text()

class DashboardPage:
  locators = {
    welcome_message: CSS(".welcome"),
    logout_button: CSS("#logout")
  }
  
  def is_displayed() → 𝔹:
    return this.find(welcome_message).is_visible()
  
  def logout() → Effect:
    this.find(logout_button).click()
```

**E2E Test Example:**

```
e2e_test_user_login_flow()
  // Setup
  = browser := launch_browser(Chrome)
    test_user := create_test_user("testuser", "password123")
    
    // Navigate to login page
    login_page := LoginPage(browser)
    browser.navigate("https://app.example.com/login")
    
    // Execute login
    login_page.login("testuser", "password123")
    
    // Verify redirect to dashboard
    dashboard := DashboardPage(browser)
    assert(dashboard.is_displayed())
    assert(contains(dashboard.welcome_message, "Welcome, testuser"))
    
    // Execute logout
    dashboard.logout()
    
    // Verify redirect to login
    assert(login_page.is_displayed())
    
    // Cleanup
    delete_test_user(test_user)
    browser.quit()
```

**Common Actions:**

```
Browser actions:
  - navigate(url)
  - refresh()
  - back()
  - forward()
  - take_screenshot()
  - execute_script(js)

Element actions:
  - find(locator) → Element
  - click()
  - type(text)
  - clear()
  - submit()
  - select(option)
  - hover()
  - drag_and_drop(source, target)

Waits:
  - wait_for_element(locator, timeout)
  - wait_for_visibility(element, timeout)
  - wait_for_text(element, text, timeout)
  - wait_for_url(url, timeout)

Assertions:
  - assert_visible(element)
  - assert_text(element, expected)
  - assert_url(expected)
  - assert_title(expected)
  - assert_element_count(locator, count)
```

**Best Practices:

```
1. Use Page Objects:
   Encapsulate page structure
   Reusable across tests
   Easier maintenance

2. Explicit Waits:
   Wait for specific conditions
   Don't use sleep()
   Handle async behavior

3. Independent Tests:
   Each test starts from clean state
   No dependencies between tests
   Can run in any order

4. Minimize Test Data:
   Use minimum data needed
   Clean up after test
   Avoid shared test data

5. Stable Locators:
   Use IDs or data attributes
   Avoid brittle CSS selectors
   Don't rely on text content
```

Test Environments:**

```
Headless mode:
  browser := Chrome(headless=true)
  Faster, no GUI
  Good for CI/CD

Grid/Cloud:
  Run tests on multiple browsers in parallel
  Selenium Grid, BrowserStack, Sauce Labs

Docker:
  Consistent environment
  Isolated tests
  Easy CI/CD integration
```

**Manifestations:**
- UI automation (Selenium, Playwright, Cypress)
- Acceptance tests
- Smoke tests
- Regression tests

---


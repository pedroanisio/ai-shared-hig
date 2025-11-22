### P26. Status Bar/Indicator

**Definition P26:**
$S = (indicators, messages, progress, position)$

- $indicators : Map⟨String, Indicator⟩$ is status widgets
- $messages : Queue⟨Message⟩$ is temporary messages
- $position : \{\text{top}, \text{bottom}, \text{left}, \text{right}\}$ is location

**Type Definitions:**
```
Indicator := (icon: Icon, text: String, status: Status, tooltip: String)
Status := Idle | Active | Success | Warning | Error
Message := (text: String, level: Level, timestamp: Time)
Level := Info | Warning | Error
ProgressBar := (label: String, current: ℕ, total: ℕ)
```

**Properties:**

**P.P26.1 (Always Visible):**
```
Status bar persistently visible
```

**P.P26.2 (Non-Intrusive):**
```
Doesn't block interaction with main content
```

**P.P26.3 (Contextual Information):**
```
Shows relevant info for current state/selection
```

**Operations:**

1. **Add Indicator:**
   ```
   add_indicator(id: String, indicator: Indicator) → Effect
   ```
   ```
   add_indicator(id: String, indicator: Indicator) → Effect
      = indicators[id] := indicator
        render(status_bar)
   ```

2. **Show Message:**
   ```
   show_message(text: String, level: Level) → Effect
   ```
   ```
   show_message(text: String, level: Level) → Effect
      = messages := enqueue(messages, Message(text, level, now()))
        schedule(clear_message, 3000)  // Clear after 3s
   ```

3. **Update Progress:**
   ```
   update_progress(id: String, current: ℕ, total: ℕ) → Effect
   ```
   ```
   update_progress(id: String, current: ℕ, total: ℕ) → Effect
      = progress[id].current := current
        progress[id].total := total
        render(progress_bar)
   - Connection status: "🟢 Online" / "🔴 Offline"
   - Sync status: "✓ Synced" / "⏱ Syncing..."
   - Agent status: "🤖 AI: Ready" / "🤖 AI: Thinking..."
   - Selection info: "3 items selected"
   - Cursor position: "Ln 42, Col 18"
   ```

**Manifestations:**
- IDE status bar (VS Code)
- Browser status bar
- Activity indicator (apps)
- Connection status (networks)

---

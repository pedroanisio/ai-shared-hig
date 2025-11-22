### P27. Toast/Notification

**Definition P27:**
$T = (message, duration, dismiss, stack, position)$

- $message : String$ is notification text
- $duration : Duration$ is auto-dismiss time

**Type Definitions:**
```
Duration := ℕ | Infinity  // milliseconds or persistent
Position := TopLeft | TopCenter | TopRight | BottomLeft | BottomCenter | BottomRight
```

**Properties:**

**P.P27.1 (Time-Limited):**
```
toast appears → auto-dismiss after duration (unless duration = ∞)
```

**P.P27.2 (Stackable):**
```
Multiple toasts stack vertically
New toasts push old toasts
```

**P.P27.3 (Non-Modal):**
```
User can interact with app while toast visible
```

**Operations:**

1. **Show Toast:**
   ```
   show(message: String, level: Level, duration: Duration) → Effect
   ```
   ```
   show(message: String, level: Level, duration: Duration) → Effect
      = toast := Toast(message, level, duration, now())
        stack := stack ++ [toast]
        render(stack)
        if duration ≠ ∞:
          schedule(dismiss(toast), duration)
   ```

2. **Dismiss:**
   ```
   dismiss(toast: Toast) → Effect
   ```
   ```
   dismiss(toast: Toast) → Effect
      = stack := stack ∖ {toast}
        animate_out(toast)
        render(stack)
   Info:    Neutral message (blue)
   Success: Operation succeeded (green)
   Warning: Caution needed (yellow)
   Error:   Operation failed (red)
   Info:    3-5 seconds
   Success: 2-3 seconds
   Warning: 5-7 seconds
   Error:   7-10 seconds or manual dismiss
   ```

**Manifestations:**
- Success messages ("✓ Saved")
- Error alerts ("❌ Failed to save")
- Info notifications ("File exported")
- Action confirmations

---

### P6. Palette/Toolbar

**Definition P6:**
$P = (tools, active, mode, layout)$

- $tools : Set⟨Tool⟩$ is available tools
- $active : Tool | null$ is active tool
- $layout : \{\text{horizontal}, \text{vertical}, \text{grid}\}$ is visual layout

**Properties:**

**P.P6.1 (Modal Exclusivity):**
```
mode = exclusive ⇒ |{t ∈ tools : active(t)}| ≤ 1
```

**P.P6.2 (Tool Application):**
```
active(tool) ∧ interact(canvas) → apply(tool, interaction)
```

**P.P6.3 (Keyboard Shortcuts):**
```
∀t ∈ tools: ∃shortcut: key(shortcut) → activate(t)
```

**Operations:**

1. **Select Tool:**
   ```
   select(tool: Tool) → Effect
   ```
   ```
   select(tool: Tool) → Effect
      = if mode = exclusive:
          active := {tool}
        else:
          active := active ∪ {tool}
        cursor := tool.cursor
   ```

2. **Apply Tool:**
   ```
   apply(tool: Tool, event: Event) → Effect
   ```
   ```
   apply(tool: Tool, event: Event) → Effect
      = tool.handler(event)
   ```

3. **Deselect:**
   ```
   deselect() → Effect
   ```
   ```
   deselect() → Effect
      = active := null
        cursor := default
   ```

**Manifestations:**
- Drawing tools (Figma)
- Code actions (VS Code)
- Sketch tools (CAD)
- Formatting toolbar (Word)

---

### P5. Tabbed Workspace

**Definition P5:**
$W = (tabs, active, buffers, state)$

- $tabs : Sequence⟨Tab⟩$ is open tabs
- $active : ℕ$ is active tab index

**Properties:**

**P.P5.1 (Single Active Tab):**
```
∀t: active(t) = (t = tabs[active])
```

**P.P5.2 (Unsaved Warning):**
```
close(tab) ∧ dirty(tab) → confirm("Unsaved changes. Close anyway?")
```

**P.P5.3 (Tab Persistence):**
```
Application restart → restore(tabs, active)
```

**Operations:**

1. **Open Tab:**
   ```
   open(item: Item) → Effect
   ```
   ```
   open(item: Item) → Effect
      = if ∃tab: tab.item = item:
          activate(tab)
        else:
          tabs := tabs ++ [Tab(item)]
          buffers[tab] := load(item)
          activate(tab)
   ```

2. **Switch Tab:**
   ```
   switch(index: ℕ) → Effect
   ```
   ```
   switch(index: ℕ) → Effect
      = save_state(tabs[active])
        active := index
        restore_state(tabs[index])
        focus(tabs[index])
   ```

3. **Close Tab:**
   ```
   close(index: ℕ) → Effect
   ```
   ```
   close(index: ℕ) → Effect
      = if dirty(tabs[index]):
          if confirm_close():
            remove(tabs, index)
            activate(max(0, index - 1))
        else:
          remove(tabs, index)
          activate(max(0, index - 1))
   ```

**Manifestations:**
- Editor tabs (VS Code)
- Document tabs (browsers)
- Multi-file editing (IDEs)
- Chat tabs (messaging apps)

---

### P36. Selection-Driven Panel

**Definition P36:**
A selection-driven panel is a tuple $S = (selection, content, \phi_{36}, observers)$ where:
- $selection : Element | null$ is the currently selected object
- $content : Component$ is the displayed content
- $\phi_{36} : Element → Component$ maps selection to content
- $observers : Set⟨Observer⟩$ watch selection changes

**Type Definitions:**
```
Element := Any selectable entity
Component := Rendered UI content
SelectionEvent := (previous: Element | null, current: Element | null)
```

**Properties:**

**P.P36.1 (Selection-Driven Content):**
```
selection changes → content := φ₃₆(selection)
∀s ∈ Element: content = φ₃₆(s) when selection = s
```

**P.P36.2 (Reactive Update):**
```
selection := new_selection ⇒ notify_observers(SelectionEvent)
All observers automatically receive update
```

**P.P36.3 (Null Selection State):**
```
selection = null ⇒ content = empty_state | default_content
Panel handles empty selection gracefully
```

**Operations:**

1. **Update Selection:**
   ```
   update_selection(element: Element | null) → Effect
   = previous := selection
     selection := element
     content := φ₃₆(selection)
     notify_observers((previous, selection))
   ```

2. **Render Content:**
   ```
   render() → Component
   = if selection = null:
       return render_empty_state()
     else:
       return φ₃₆(selection)
   ```

3. **Subscribe to Selection:**
   ```
   subscribe(observer: Observer) → Effect
   = observers := observers ∪ {observer}
     observer.update(selection)  // Initial notification
   ```

4. **Clear Selection:**
   ```
   clear() → Effect
   = update_selection(null)
   ```

**Specializations:**

- **P4 (Property Inspector): φ₃₆ maps to property fields
- Detail Panel:** φ₃₆ maps to detail view
- **Context Panel: φ₃₆ maps to contextual information

Manifestations:**
- Inspector panels (property editors)
- Detail views (master-detail pattern)
- Context-sensitive sidebars
- Selection-based toolbars
- Preview panels

---



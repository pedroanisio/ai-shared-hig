### P1. Direct Manipulation Canvas

**Definition P1:**
$C = (viewport, objects, cursor, tools, state)$

- $viewport : Rectangle$ is visible area
- $objects : Set⟨Element⟩$ is manipulable objects
- $cursor : Point$ is current cursor position
- $tools : Set⟨Tool⟩$ is available interaction tools

**Properties:**

**P.P1.1 (WYSIWYG):**
```
∀o ∈ objects: visual(o) = semantic(o)
Changes to visual representation directly modify semantic content.
```

**P.P1.2 (Direct Feedback):**
```
gesture(t) → update_visual(t + ε) where ε < 16ms (60fps)
```

**P.P1.3 (Object Selection):**
```
click(p) → select({o ∈ objects : p ∈ bounds(o)})
```

**Operations:**

1. **Interpret Gesture:**
   ```
   interpret(gesture: Gesture) → Action
   ```
   ```
   interpret(gesture: Gesture) → Action
      = case gesture of
          Click(p) → Select(objectAt(p))
          Drag(p₁, p₂) → Move(selected, p₂ - p₁)
          Scroll(Δ) → Pan(viewport, Δ)
   ```

2. **Update Visual:**
   ```
   update(objects: Set⟨Element⟩) → Effect
   ```
   ```
   update(objects: Set⟨Element⟩) → Effect
      = render(objects) ; invalidate(viewport)
   ```

3. **Persist Changes:**
   ```
   persist(objects: Set⟨Element⟩) → Effect
   ```
   ```
   persist(objects: Set⟨Element⟩) → Effect
      = save_to_storage(objects) ; notify_observers(objects)
   ```

**Manifestations:**
- Graph editor (knowledge graphs)
- 3D viewport (CAD)
- Drawing canvas (vector graphics)
- Visual editor (page builders)
- Diagram editors

---

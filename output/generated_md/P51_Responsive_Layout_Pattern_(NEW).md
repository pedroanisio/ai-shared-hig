### P51. Responsive Layout Pattern (NEW)

**Definition P51:**
$L = (breakpoints, layouts, current)$

- $current : String$ is active layout name

**Type Definitions:**
```
Breakpoint := (width: ℝ, name: String)
Layout := (structure: Component, visibility: Map⟨Element, 𝔹⟩)
```

**Properties:**

**P.P51.1 (Breakpoint Selection):**
```
current = max{bp.name : bp.width ≤ viewport.width}
```

**P.P51.2 (Layout Activation):**
```
viewport changes → update_current() → apply(layouts[current])
```

**P.P51.3 (Mobile-First):**
```
breakpoints ordered: mobile < tablet < desktop < wide
```

**Operations:**

1. **Select Layout:**
   ```
   select_layout(width: ℝ) → String
   ```
   ```
   select_layout(width: ℝ) → String
      = find_last(breakpoints, λbp: bp.width ≤ width).name
   ```

2. **Apply Layout:**
   ```
   apply(layout: Layout) → Effect
   ```
   ```
   apply(layout: Layout) → Effect
      = structure := layout.structure
        for (element, visible) in layout.visibility:
          element.visible := visible
        reflow()
   ```

3. **Register Breakpoint:**
   ```
   register(bp: Breakpoint, layout: Layout) → Effect
   ```
   ```
   register(bp: Breakpoint, layout: Layout) → Effect
      = breakpoints := insert_sorted(breakpoints, bp)
        layouts[bp.name] := layout
   mobile:  < 640px
   tablet:  640px - 1024px
   desktop: 1024px - 1440px
   wide:    ≥ 1440px
   ```

4. **Collapsing Navigation:**
   ```
   mobile: P43(collapsed)
      desktop: P43(pinned)
   ```

5. **Column Reflow:**
   ```
   mobile: 1 column
      tablet: 2 columns
      desktop: 3 columns
   ```

6. **Component Swap:**
   ```
   mobile: Compact cards
      desktop: Expanded cards with details
   ```

**Manifestations:**
- Responsive web apps
- Mobile-first design
- Adaptive interfaces
- Cross-device layouts

---

#!/bin/bash

# Phase 1 Quality Fix: P11-P20 (Navigation & Layout Patterns)
# Addresses: incomplete formalization, weak invariants, missing temporal specs
# Target API: localhost:8000

BASE_URL="http://localhost:8000"
CONTENT_TYPE="Content-Type: application/json"

echo "=========================================="
echo "Phase 1 Batch 2: Patching P11-P20"
echo "Critical Fixes: Type completion, formal invariants, temporal specs"
echo "=========================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

patch_pattern() {
    local pattern_id=$1
    local pattern_name=$2
    local json_payload=$3
    
    echo -e "${YELLOW}Patching ${pattern_id}: ${pattern_name}${NC}"
    
    response=$(curl -s -w "\n%{http_code}" -X PATCH \
        "${BASE_URL}/patterns/${pattern_id}" \
        -H "${CONTENT_TYPE}" \
        -d "${json_payload}")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}✓ Successfully patched ${pattern_id}${NC}"
        echo ""
    else
        echo -e "${RED}✗ Failed to patch ${pattern_id} (HTTP ${http_code})${NC}"
        echo "Response: $body"
        echo ""
    fi
}

#############################################
# P11: Breadcrumb Navigation - PATCH
#############################################

P11_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P11.1",
        "name": "Path Completeness",
        "formal-spec": {
          "content": "∀path: breadcrumb(current) = [root, ..., parent(current), current] ∧ connected(path)",
          "format": "latex"
        },
        "description": "Breadcrumb shows complete path from root to current location",
        "invariants": {
          "invariant": [
            {
              "content": "∀node: ∃path: root ⇝ node via breadcrumb_trail",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P11.2",
        "name": "Navigable History",
        "formal-spec": {
          "content": "∀item ∈ breadcrumb: clickable(item) ∧ click(item) ⟹ navigate_to(item)",
          "format": "latex"
        },
        "description": "Each breadcrumb item is clickable and navigates to that level",
        "invariants": {
          "invariant": [
            {
              "content": "∀crumb ∈ path: enabled(crumb) ∧ action(crumb) = navigate",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P11.3",
        "name": "Overflow Handling",
        "formal-spec": {
          "content": "|breadcrumb| > max_visible ⟹ show([root, ..., truncate_middle(...), parent, current])",
          "format": "latex"
        },
        "description": "Long paths truncated in middle, preserving root and current",
        "invariants": {
          "invariant": [
            {
              "content": "visible_crumbs ≤ MAX_DISPLAY ⟹ show_all else show_truncated",
              "format": "latex"
            }
          ]
        }
      }
    ]
  },
  "type-definitions": {
    "type-def": [
      {
        "name": "Breadcrumb",
        "definition": {
          "content": "List⟨BreadcrumbItem⟩ where length ≥ 1",
          "format": "latex"
        },
        "description": "Ordered list of navigation items"
      },
      {
        "name": "BreadcrumbItem",
        "definition": {
          "content": "(label: String, url: URL, level: ℕ, current: Boolean)",
          "format": "latex"
        },
        "description": "Individual breadcrumb link"
      }
    ]
  },
  "operations": {
    "operation": [
      {
        "name": "build_breadcrumb",
        "signature": "build_breadcrumb(current: Node, hierarchy: Tree) → List⟨BreadcrumbItem⟩",
        "formal-definition": {
          "content": "build_breadcrumb(n, t) = reverse(path_to_root(n, t))",
          "format": "latex"
        },
        "complexity": "O(depth) where depth = distance from root"
      }
    ]
  }
}
EOF
)

patch_pattern "P11" "Breadcrumb Navigation" "$P11_PATCH"

#############################################
# P12: Pagination - PATCH
#############################################

P12_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P12.1",
        "name": "Page Bounds",
        "formal-spec": {
          "content": "∀p ∈ Pages: 1 ≤ current_page ≤ total_pages ∧ total_pages = ⌈total_items / items_per_page⌉",
          "format": "latex"
        },
        "description": "Current page within valid bounds based on total items",
        "invariants": {
          "invariant": [
            {
              "content": "1 ≤ page ≤ ⌈count / page_size⌉",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P12.2",
        "name": "Item Range",
        "formal-spec": {
          "content": "items_on_page(p) = items[start_index(p) : end_index(p)] where start = (p-1) × size ∧ end = min(p × size, total)",
          "format": "latex"
        },
        "description": "Each page shows correct slice of total items",
        "invariants": {
          "invariant": [
            {
              "content": "∀page: |displayed_items(page)| ≤ page_size",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P12.3",
        "name": "Navigation Availability",
        "formal-spec": {
          "content": "enabled(previous) ⟺ current > 1 ∧ enabled(next) ⟺ current < total_pages",
          "format": "latex"
        },
        "description": "Previous/Next buttons enabled based on page position",
        "invariants": {
          "invariant": [
            {
              "content": "page = 1 ⟹ disabled(prev) ∧ page = last ⟹ disabled(next)",
              "format": "latex"
            }
          ]
        }
      }
    ]
  },
  "type-definitions": {
    "type-def": [
      {
        "name": "Pagination",
        "definition": {
          "content": "(current_page: ℕ₊, page_size: ℕ₊, total_items: ℕ)",
          "format": "latex"
        },
        "description": "Pagination state"
      },
      {
        "name": "PageInfo",
        "definition": {
          "content": "(start_index: ℕ, end_index: ℕ, has_previous: Boolean, has_next: Boolean)",
          "format": "latex"
        },
        "description": "Computed page information"
      }
    ]
  },
  "operations": {
    "operation": [
      {
        "name": "goto_page",
        "signature": "goto_page(page_num: ℕ) → Effect",
        "formal-definition": {
          "content": "goto_page(n) = if 1 ≤ n ≤ total_pages then current := n else error",
          "format": "latex"
        },
        "preconditions": {
          "condition": [{"content": "1 ≤ page_num ≤ total_pages", "format": "latex"}]
        },
        "postconditions": {
          "condition": [
            {"content": "current_page = page_num", "format": "latex"},
            {"content": "displayed_items = items[(n-1)×size : n×size]", "format": "latex"}
          ]
        },
        "complexity": "O(page_size) for data fetch"
      }
    ]
  }
}
EOF
)

patch_pattern "P12" "Pagination" "$P12_PATCH"

#############################################
# P13: Infinite Scroll - PATCH
#############################################

P13_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P13.1",
        "name": "Trigger Distance",
        "formal-spec": {
          "content": "∀scroll: distance_to_bottom < threshold ∧ ¬loading ⟹ fetch_next_batch() where threshold ∈ [200px, 500px]",
          "format": "latex"
        },
        "description": "Next batch loads when user approaches bottom",
        "invariants": {
          "invariant": [
            {
              "content": "trigger_load ⟺ scroll_position > (content_height - viewport_height - threshold)",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P13.2",
        "name": "No Duplicate Fetches",
        "formal-spec": {
          "content": "∀batch: loading(batch) ⟹ ¬initiate_fetch(batch) until complete(batch)",
          "format": "latex"
        },
        "description": "Prevents duplicate fetches while loading",
        "invariants": {
          "invariant": [
            {
              "content": "concurrent_requests ≤ 1",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P13.3",
        "name": "End Detection",
        "formal-spec": {
          "content": "fetched_items < batch_size ⟹ reached_end := true ∧ ¬trigger_more_fetches",
          "format": "latex"
        },
        "description": "Detects end of content and stops fetching",
        "invariants": {
          "invariant": [
            {
              "content": "reached_end = true ⟹ ∀future_scrolls: ¬fetch_attempted",
              "format": "latex"
            }
          ]
        }
      }
    ]
  },
  "type-definitions": {
    "type-def": [
      {
        "name": "InfiniteScroll",
        "definition": {
          "content": "(loaded_items: List⟨T⟩, loading: Boolean, has_more: Boolean, cursor: Option⟨String⟩)",
          "format": "latex"
        },
        "description": "Infinite scroll state"
      },
      {
        "name": "ScrollPosition",
        "definition": {
          "content": "(offset: ℝ₊, viewport_height: ℝ₊, content_height: ℝ₊)",
          "format": "latex"
        },
        "description": "Scroll position metrics"
      }
    ]
  },
  "operations": {
    "operation": [
      {
        "name": "fetch_next_batch",
        "signature": "fetch_next_batch(cursor: Option⟨String⟩, size: ℕ) → Promise⟨List⟨T⟩⟩",
        "formal-definition": {
          "content": "fetch_next_batch(c, n) = api.fetch(cursor: c, limit: n).then(append_items)",
          "format": "latex"
        },
        "preconditions": {
          "condition": [
            {"content": "¬loading ∧ has_more", "format": "latex"}
          ]
        },
        "postconditions": {
          "condition": [
            {"content": "loaded_items := old_items ++ new_items", "format": "latex"},
            {"content": "has_more := |new_items| = batch_size", "format": "latex"}
          ]
        },
        "complexity": "O(n) where n = batch_size"
      }
    ]
  }
}
EOF
)

patch_pattern "P13" "Infinite Scroll" "$P13_PATCH"

#############################################
# P14: Tab Navigation - PATCH
#############################################

P14_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P14.1",
        "name": "Single Active Tab",
        "formal-spec": {
          "content": "∀t ∈ Time: ∃!tab ∈ Tabs: active(tab, t)",
          "format": "latex"
        },
        "description": "Exactly one tab active at any time",
        "invariants": {
          "invariant": [
            {
              "content": "count({t ∈ Tabs | active(t)}) = 1",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P14.2",
        "name": "Content Visibility",
        "formal-spec": {
          "content": "∀tab: visible(content(tab)) ⟺ active(tab)",
          "format": "latex"
        },
        "description": "Only active tab's content is visible",
        "invariants": {
          "invariant": [
            {
              "content": "∀t: active(t) ⟹ rendered(content(t)) ∧ ∀t': t' ≠ t ⟹ hidden(content(t'))",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P14.3",
        "name": "State Preservation",
        "formal-spec": {
          "content": "∀tab: switch_away(tab) ⟹ save(state(tab)) ∧ switch_to(tab) ⟹ restore(state(tab))",
          "format": "latex"
        },
        "description": "Tab state preserved across switches",
        "invariants": {
          "invariant": [
            {
              "content": "∀tab: state_after_return(tab) = state_before_leave(tab)",
              "format": "latex"
            }
          ]
        }
      }
    ]
  },
  "type-definitions": {
    "type-def": [
      {
        "name": "Tab",
        "definition": {
          "content": "(id: String, label: String, content: Component, active: Boolean, state: State)",
          "format": "latex"
        },
        "description": "Individual tab definition"
      },
      {
        "name": "TabContainer",
        "definition": {
          "content": "(tabs: List⟨Tab⟩, active_index: ℕ, lazy_load: Boolean)",
          "format": "latex"
        },
        "description": "Tab container configuration"
      }
    ]
  },
  "state-machine": {
    "states": ["inactive", "activating", "active", "deactivating"],
    "initial": "inactive",
    "transitions": [
      {"from": "inactive", "to": "activating", "on": "tab_clicked", "guard": "enabled"},
      {"from": "activating", "to": "active", "on": "transition_complete", "guard": "content_loaded"},
      {"from": "active", "to": "deactivating", "on": "other_tab_clicked", "guard": "true"},
      {"from": "deactivating", "to": "inactive", "on": "transition_complete", "guard": "state_saved"}
    ]
  }
}
EOF
)

patch_pattern "P14" "Tab Navigation" "$P14_PATCH"

#############################################
# P15: Accordion - PATCH
#############################################

P15_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P15.1",
        "name": "Panel Independence",
        "formal-spec": {
          "content": "∀mode: mode = independent ⟹ ∀p ∈ Panels: toggle(p) independent of state(other_panels)",
          "format": "latex"
        },
        "description": "In independent mode, panels toggle independently",
        "invariants": {
          "invariant": [
            {
              "content": "mode = independent ⟹ ∀p: open(p) does not affect others",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P15.2",
        "name": "Exclusive Mode",
        "formal-spec": {
          "content": "∀mode: mode = exclusive ⟹ ∀t: |{p ∈ Panels | open(p, t)}| ≤ 1",
          "format": "latex"
        },
        "description": "In exclusive mode, at most one panel open",
        "invariants": {
          "invariant": [
            {
              "content": "mode = exclusive ⟹ count(open_panels) ≤ 1",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P15.3",
        "name": "Smooth Expansion",
        "formal-spec": {
          "content": "∀p: toggle(p) ⟹ animate(height: 0 → content_height, duration: τ) where τ ∈ [200ms, 400ms]",
          "format": "latex"
        },
        "description": "Panel expansion/collapse is smoothly animated",
        "invariants": {
          "invariant": [
            {
              "content": "∀transition: animation_duration ∈ [200ms, 400ms]",
              "format": "latex"
            }
          ]
        }
      }
    ]
  },
  "type-definitions": {
    "type-def": [
      {
        "name": "Panel",
        "definition": {
          "content": "(id: String, header: Element, content: Element, open: Boolean)",
          "format": "latex"
        },
        "description": "Accordion panel definition"
      },
      {
        "name": "Accordion",
        "definition": {
          "content": "(panels: List⟨Panel⟩, mode: {independent, exclusive}, allow_collapse_all: Boolean)",
          "format": "latex"
        },
        "description": "Accordion container configuration"
      }
    ]
  },
  "operations": {
    "operation": [
      {
        "name": "toggle_panel",
        "signature": "toggle_panel(panel: Panel, mode: Mode) → Effect",
        "formal-definition": {
          "content": "toggle_panel(p, m) = if m = exclusive then close_others(); toggle(p) else toggle(p)",
          "format": "latex"
        },
        "preconditions": {
          "condition": [{"content": "enabled(panel)", "format": "latex"}]
        },
        "postconditions": {
          "condition": [
            {"content": "panel.open = ¬old_panel.open", "format": "latex"},
            {"content": "mode = exclusive ⟹ ∀other: ¬other.open", "format": "latex"}
          ]
        },
        "complexity": "O(1) for independent, O(n) for exclusive where n = panel count"
      }
    ]
  }
}
EOF
)

patch_pattern "P15" "Accordion" "$P15_PATCH"

#############################################
# P16: Sidebar/Drawer - PATCH
#############################################

P16_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P16.1",
        "name": "State Persistence",
        "formal-spec": {
          "content": "∀drawer: state(drawer) ∈ {open, closed, pinned} ∧ persistent across sessions",
          "format": "latex"
        },
        "description": "Drawer state persists across sessions",
        "invariants": {
          "invariant": [
            {
              "content": "∀session_reload: state_after = state_before",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P16.2",
        "name": "Overlay Behavior",
        "formal-spec": {
          "content": "state = open ∧ ¬pinned ⟹ z_index(drawer) > z_index(main_content) ∧ click(outside) → close",
          "format": "latex"
        },
        "description": "Unpinned drawer overlays content and closes on outside click",
        "invariants": {
          "invariant": [
            {
              "content": "¬pinned ⟹ (overlays_content ∧ dismissible)",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P16.3",
        "name": "Responsive Width",
        "formal-spec": {
          "content": "width(drawer) = min(configured_width, viewport_width × max_percentage) where max_percentage = 0.8",
          "format": "latex"
        },
        "description": "Drawer width bounded by viewport size",
        "invariants": {
          "invariant": [
            {
              "content": "width(drawer) ≤ 0.8 × viewport_width",
              "format": "latex"
            }
          ]
        }
      }
    ]
  },
  "type-definitions": {
    "type-def": [
      {
        "name": "Drawer",
        "definition": {
          "content": "(position: {left, right, top, bottom}, state: DrawerState, width: ℝ₊, content: Component)",
          "format": "latex"
        },
        "description": "Drawer configuration"
      },
      {
        "name": "DrawerState",
        "definition": {
          "content": "Closed | Open(pinned: Boolean)",
          "format": "latex"
        },
        "description": "Drawer state variants"
      }
    ]
  },
  "state-machine": {
    "states": ["closed", "opening", "open_unpinned", "open_pinned", "closing"],
    "initial": "closed",
    "transitions": [
      {"from": "closed", "to": "opening", "on": "open_trigger", "guard": "true"},
      {"from": "opening", "to": "open_unpinned", "on": "animation_complete", "guard": "true"},
      {"from": "open_unpinned", "to": "open_pinned", "on": "pin_clicked", "guard": "true"},
      {"from": "open_pinned", "to": "open_unpinned", "on": "unpin_clicked", "guard": "true"},
      {"from": "open_unpinned", "to": "closing", "on": "close_trigger", "guard": "true"},
      {"from": "open_pinned", "to": "closing", "on": "close_trigger", "guard": "true"},
      {"from": "closing", "to": "closed", "on": "animation_complete", "guard": "true"}
    ]
  }
}
EOF
)

patch_pattern "P16" "Sidebar/Drawer" "$P16_PATCH"

#############################################
# P17: Grid Layout - PATCH
#############################################

P17_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P17.1",
        "name": "Space Distribution",
        "formal-spec": {
          "content": "∑_{cell ∈ Grid} area(cell) + gaps = total_area ∧ no_overlap(cells)",
          "format": "latex"
        },
        "description": "Grid cells fill space without overlap",
        "invariants": {
          "invariant": [
            {
              "content": "∀c₁, c₂ ∈ Cells: c₁ ≠ c₂ ⟹ bounds(c₁) ∩ bounds(c₂) = ∅",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P17.2",
        "name": "Responsive Columns",
        "formal-spec": {
          "content": "columns(viewport_width) = max({n ∈ ℕ | n × (min_cell_width + gap) ≤ viewport_width})",
          "format": "latex"
        },
        "description": "Column count adapts to viewport width",
        "invariants": {
          "invariant": [
            {
              "content": "∀breakpoint: columns decreases as viewport_width decreases",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P17.3",
        "name": "Alignment Consistency",
        "formal-spec": {
          "content": "∀row ∈ Rows: ∀cell ∈ row: aligned(cell, grid_lines) ∧ height(row) = max(heights(cells_in_row))",
          "format": "latex"
        },
        "description": "Cells align to grid and rows match tallest cell",
        "invariants": {
          "invariant": [
            {
              "content": "∀cell: position(cell) aligned to grid_system",
              "format": "latex"
            }
          ]
        }
      }
    ]
  },
  "type-definitions": {
    "type-def": [
      {
        "name": "GridLayout",
        "definition": {
          "content": "(columns: ℕ, gap: ℝ₊, cells: List⟨GridCell⟩, responsive: Boolean)",
          "format": "latex"
        },
        "description": "Grid layout configuration"
      },
      {
        "name": "GridCell",
        "definition": {
          "content": "(row_start: ℕ, col_start: ℕ, row_span: ℕ, col_span: ℕ, content: Component)",
          "format": "latex"
        },
        "description": "Individual grid cell"
      }
    ]
  }
}
EOF
)

patch_pattern "P17" "Grid Layout" "$P17_PATCH"

#############################################
# P18: Card Layout - PATCH
#############################################

P18_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P18.1",
        "name": "Visual Hierarchy",
        "formal-spec": {
          "content": "∀card: content(card) = [header?, media?, body, footer?] in order ∧ prominence(header) > prominence(body) > prominence(footer)",
          "format": "latex"
        },
        "description": "Card sections follow visual hierarchy",
        "invariants": {
          "invariant": [
            {
              "content": "∀card: order(sections) fixed ∧ sizes proportional to importance",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P18.2",
        "name": "Interactive States",
        "formal-spec": {
          "content": "clickable(card) ⟹ ∀state ∈ {hover, focus, active}: has_visual_feedback(card, state)",
          "format": "latex"
        },
        "description": "Interactive cards show state feedback",
        "invariants": {
          "invariant": [
            {
              "content": "interactive ⟹ ∀state: visible_change(state)",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P18.3",
        "name": "Content Bounds",
        "formal-spec": {
          "content": "∀card: width ∈ [min_width, max_width] ∧ height = content_height ∨ fixed_height",
          "format": "latex"
        },
        "description": "Cards have bounded dimensions",
        "invariants": {
          "invariant": [
            {
              "content": "∀card: dimensions within configured bounds",
              "format": "latex"
            }
          ]
        }
      }
    ]
  },
  "type-definitions": {
    "type-def": [
      {
        "name": "Card",
        "definition": {
          "content": "(header: Option⟨Element⟩, media: Option⟨Element⟩, body: Element, footer: Option⟨Element⟩, interactive: Boolean)",
          "format": "latex"
        },
        "description": "Card structure"
      },
      {
        "name": "CardAction",
        "definition": {
          "content": "(label: String, handler: () → Effect, type: {primary, secondary})",
          "format": "latex"
        },
        "description": "Card action button"
      }
    ]
  }
}
EOF
)

patch_pattern "P18" "Card Layout" "$P18_PATCH"

#############################################
# P19: List View - PATCH
#############################################

P19_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P19.1",
        "name": "Item Uniformity",
        "formal-spec": {
          "content": "∀mode: mode = uniform ⟹ ∀i ∈ Items: height(i) = constant ∧ structure(i) consistent",
          "format": "latex"
        },
        "description": "Uniform mode ensures consistent item height and structure",
        "invariants": {
          "invariant": [
            {
              "content": "uniform_mode ⟹ ∀i, j: height(i) = height(j)",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P19.2",
        "name": "Selection State",
        "formal-spec": {
          "content": "∀selection_mode: mode = single ⟹ |selected| ≤ 1 ∧ mode = multi ⟹ selected ⊆ Items",
          "format": "latex"
        },
        "description": "Selection respects mode constraints",
        "invariants": {
          "invariant": [
            {
              "content": "single_select ⟹ count(selected) ≤ 1",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P19.3",
        "name": "Virtual Scrolling",
        "formal-spec": {
          "content": "virtualized ⟹ rendered_items = visible_items ∪ buffer_items where |buffer_items| ≪ |total_items|",
          "format": "latex"
        },
        "description": "Virtual scrolling renders only visible + buffer items",
        "invariants": {
          "invariant": [
            {
              "content": "virtualized ⟹ rendered_count ≪ total_count",
              "format": "latex"
            }
          ]
        }
      }
    ]
  },
  "type-definitions": {
    "type-def": [
      {
        "name": "ListView",
        "definition": {
          "content": "(items: List⟨T⟩, render_item: T → Element, selection_mode: SelectionMode, virtualized: Boolean)",
          "format": "latex"
        },
        "description": "List view configuration"
      },
      {
        "name": "SelectionMode",
        "definition": {
          "content": "None | Single | Multiple",
          "format": "latex"
        },
        "description": "Selection behavior mode"
      }
    ]
  }
}
EOF
)

patch_pattern "P19" "List View" "$P19_PATCH"

#############################################
# P20: Master-Detail View - PATCH
#############################################

P20_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P20.1",
        "name": "Selection Binding",
        "formal-spec": {
          "content": "∀t: selected(master, t) = item ⟹ displayed(detail, t) = details(item)",
          "format": "latex"
        },
        "description": "Detail view shows details of selected master item",
        "invariants": {
          "invariant": [
            {
              "content": "∀item: selected(item) ⟺ detail_shows(item)",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P20.2",
        "name": "Responsive Layout",
        "formal-spec": {
          "content": "viewport_width < breakpoint ⟹ layout = stacked else layout = side_by_side",
          "format": "latex"
        },
        "description": "Layout adapts from side-by-side to stacked on small screens",
        "invariants": {
          "invariant": [
            {
              "content": "layout_mode determined by viewport_width thresholds",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P20.3",
        "name": "Empty State Handling",
        "formal-spec": {
          "content": "selected(master) = null ⟹ displayed(detail) = empty_state_placeholder",
          "format": "latex"
        },
        "description": "Detail shows placeholder when no item selected",
        "invariants": {
          "invariant": [
            {
              "content": "¬∃selection ⟹ detail_shows_placeholder",
              "format": "latex"
            }
          ]
        }
      }
    ]
  },
  "type-definitions": {
    "type-def": [
      {
        "name": "MasterDetail",
        "definition": {
          "content": "(master: ListView⟨T⟩, detail: T → Component, layout: LayoutMode, breakpoint: ℝ₊)",
          "format": "latex"
        },
        "description": "Master-detail view configuration"
      },
      {
        "name": "LayoutMode",
        "definition": {
          "content": "SideBySide(master_width: ℝ) | Stacked | Overlay",
          "format": "latex"
        },
        "description": "Layout arrangement mode"
      }
    ]
  }
}
EOF
)

patch_pattern "P20" "Master-Detail View" "$P20_PATCH"

echo ""
echo "=========================================="
echo "Batch 2 Complete: P11-P20"
echo "=========================================="
echo ""
echo "Summary: Enhanced 10 patterns with:"
echo "  ✓ Complete type definitions"
echo "  ✓ Formal invariants (not labels)"
echo "  ✓ Temporal specifications"
echo "  ✓ State machines (where applicable)"
echo "  ✓ Complexity analysis"
echo "  ✓ Precise pre/postconditions"
echo ""



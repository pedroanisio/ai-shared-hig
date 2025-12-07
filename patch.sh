#!/bin/bash

# Supplemental PATCH script for P37-P40
# These patterns already exist and need enhancement
# Run this AFTER patch_patterns.sh or combine them
# Target API: localhost:8000

BASE_URL="http://localhost:8000"
CONTENT_TYPE="Content-Type: application/json"

echo "=========================================="
echo "Patching P37-P40 (Supplemental)"
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
# P37: Empty State Pattern - PATCH
#############################################

P37_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P37.1",
        "name": "Visibility Condition",
        "formal-spec": {
          "content": "visible(P) ⟺ ε(C) = empty",
          "format": "latex"
        },
        "description": "Placeholder visible if and only if container is empty",
        "invariants": {
          "invariant": [{"content": "conditional_visibility", "format": "latex"}]
        }
      },
      {
        "id": "P.P37.2",
        "name": "Emptiness Definition",
        "formal-spec": {
          "content": "ε(C) = empty ⟺ |items(C)| = 0 ∨ (∀i ∈ items(C): hidden(i))",
          "format": "latex"
        },
        "description": "Container is empty if it has no items or all items are hidden",
        "invariants": {
          "invariant": [{"content": "clear_emptiness", "format": "latex"}]
        }
      },
      {
        "id": "P.P37.3",
        "name": "Action Trigger",
        "formal-spec": {
          "content": "∀a ∈ A: execute(a) ⟹ ε(C) → populated (eventually)",
          "format": "latex"
        },
        "description": "Call-to-action execution eventually populates container",
        "invariants": {
          "invariant": [{"content": "actionable_cta", "format": "latex"}]
        }
      },
      {
        "id": "P.P37.4",
        "name": "Content Hierarchy",
        "formal-spec": {
          "content": "priority(message) > priority(illustration) > priority(A)",
          "format": "latex"
        },
        "description": "Message is most prominent, followed by illustration, then actions",
        "invariants": {
          "invariant": [{"content": "visual_hierarchy", "format": "latex"}]
        }
      }
    ]
  },
  "definition": {
    "components": {
      "component": [
        {
          "name": "C",
          "type": "Container",
          "notation": "C",
          "description": "**container** (region that may be empty)"
        },
        {
          "name": "ε",
          "type": "C → {empty, populated}",
          "notation": "ε",
          "description": "**emptiness predicate**"
        },
        {
          "name": "P",
          "type": "(message, illustration, optional)",
          "notation": "P",
          "description": "**placeholder content**"
        },
        {
          "name": "A",
          "type": "Set⟨Action⟩",
          "notation": "A",
          "description": "set of **call-to-action** elements"
        }
      ]
    }
  },
  "type-definitions": {
    "type-def": [
      {
        "name": "Placeholder",
        "definition": {
          "content": "(message: String, illustration: Image, style: Style)",
          "format": "latex"
        },
        "description": "Empty state placeholder content"
      },
      {
        "name": "Action",
        "definition": {
          "content": "(label: String, handler: () → Effect, primary: 𝔹)",
          "format": "latex"
        },
        "description": "Call-to-action button"
      }
    ]
  }
}
EOF
)

patch_pattern "P37" "Empty State Pattern" "$P37_PATCH"

#############################################
# P38: Badge/Indicator Pattern - PATCH
#############################################

P38_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P38.1",
        "name": "Overlay Positioning",
        "formal-spec": {
          "content": "∀b: bounds(b) ∩ bounds(H) ≠ ∅ ∧ bounds(b) ⊄ interior(bounds(H))",
          "format": "latex"
        },
        "description": "Badge overlaps host but extends beyond its boundaries",
        "invariants": {
          "invariant": [{"content": "partial_overlap", "format": "latex"}]
        }
      },
      {
        "id": "P.P38.2",
        "name": "Z-Index Ordering",
        "formal-spec": {
          "content": "z-index(B) > z-index(H) > z-index(siblings(H))",
          "format": "latex"
        },
        "description": "Badge renders above host, host above siblings",
        "invariants": {
          "invariant": [{"content": "layering_order", "format": "latex"}]
        }
      },
      {
        "id": "P.P38.3",
        "name": "Value Thresholding",
        "formal-spec": {
          "content": "display(v) = if v ≤ threshold then v else threshold⁺",
          "format": "latex"
        },
        "description": "Large values truncated (e.g., \"99+\")",
        "invariants": {
          "invariant": [{"content": "readable_counts", "format": "latex"}]
        }
      },
      {
        "id": "P.P38.4",
        "name": "Attention Gradient",
        "formal-spec": {
          "content": "attention(v) = {low if v = 0, medium if 0 < v ≤ warning_threshold, high if v > warning_threshold}",
          "format": "latex"
        },
        "description": "Visual urgency increases with value",
        "invariants": {
          "invariant": [{"content": "urgency_scaling", "format": "latex"}]
        }
      },
      {
        "id": "P.P38.5",
        "name": "Animation on Update",
        "formal-spec": {
          "content": "v_old ≠ v_new ⟹ animate(scale, duration: τ) ∨ animate(color, duration: τ)",
          "format": "latex"
        },
        "description": "Value changes trigger brief animation",
        "invariants": {
          "invariant": [{"content": "animated_updates", "format": "latex"}]
        }
      }
    ]
  },
  "definition": {
    "components": {
      "component": [
        {
          "name": "H",
          "type": "Element",
          "notation": "H",
          "description": "**host element** (button, icon, menu item)"
        },
        {
          "name": "v",
          "type": "ℕ ∪ {status}",
          "notation": "v",
          "description": "**badge value** (count or state)"
        },
        {
          "name": "ρ",
          "type": "H → ℝ²",
          "notation": "ρ",
          "description": "**position function** (relative to host)"
        },
        {
          "name": "σ",
          "type": "v → Style",
          "notation": "σ",
          "description": "**styling function** (color, size based on value)"
        },
        {
          "name": "τ",
          "type": "ℝ₊",
          "notation": "τ",
          "description": "**update animation duration**"
        }
      ]
    }
  },
  "type-definitions": {
    "type-def": [
      {
        "name": "BadgeValue",
        "definition": {
          "content": "Number(n: ℕ) | Status(state: String)",
          "format": "latex"
        },
        "description": "Badge can show count or status"
      },
      {
        "name": "Style",
        "definition": {
          "content": "(color: Color, background: Color, size: Size, urgency: Level)",
          "format": "latex"
        },
        "description": "Visual styling properties"
      }
    ]
  }
}
EOF
)

patch_pattern "P38" "Badge/Indicator Pattern" "$P38_PATCH"

#############################################
# P39: Contextual Action Menu - PATCH
#############################################

P39_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P39.1",
        "name": "Context Dependency",
        "formal-spec": {
          "content": "∀a ∈ A: π(a, C) determines visibility/enablement",
          "format": "latex"
        },
        "description": "Actions shown/enabled based on current context",
        "invariants": {
          "invariant": [{"content": "context_aware_actions", "format": "latex"}]
        }
      },
      {
        "id": "P.P39.2",
        "name": "Mutual Exclusivity",
        "formal-spec": {
          "content": "∀m₁, m₂ ∈ Menus: m₁ ≠ m₂ ⟹ (σ(m₁) = open ⟹ σ(m₂) = closed)",
          "format": "latex"
        },
        "description": "At most one contextual menu open at a time",
        "invariants": {
          "invariant": [{"content": "single_open_menu", "format": "latex"}]
        }
      },
      {
        "id": "P.P39.3",
        "name": "Auto-Dismiss",
        "formal-spec": {
          "content": "σ(M) = open ∧ click(outside(M)) ⟹ σ(M) := closed",
          "format": "latex"
        },
        "description": "Clicking outside menu closes it",
        "invariants": {
          "invariant": [{"content": "dismissible", "format": "latex"}]
        }
      },
      {
        "id": "P.P39.4",
        "name": "Positioning Constraint",
        "formal-spec": {
          "content": "δ(M) such that bounds(M) ⊆ viewport ∧ near(M, T)",
          "format": "latex"
        },
        "description": "Menu positioned near trigger and within viewport",
        "invariants": {
          "invariant": [{"content": "smart_positioning", "format": "latex"}]
        }
      },
      {
        "id": "P.P39.5",
        "name": "Action Hierarchy",
        "formal-spec": {
          "content": "A = A_primary ∪ A_secondary ∪ A_destructive where visual(A_primary) > visual(A_secondary) > visual(A_destructive)",
          "format": "latex"
        },
        "description": "Actions grouped by importance and consequence",
        "invariants": {
          "invariant": [{"content": "visual_hierarchy", "format": "latex"}]
        }
      }
    ]
  },
  "definition": {
    "components": {
      "component": [
        {
          "name": "T",
          "type": "Element",
          "notation": "T",
          "description": "**trigger element** (button, right-click area)"
        },
        {
          "name": "C",
          "type": "Context",
          "notation": "C",
          "description": "**context** (selected item, current state)"
        },
        {
          "name": "A",
          "type": "Set⟨Action⟩",
          "notation": "A",
          "description": "set of **actions**"
        }
      ]
    }
  },
  "type-definitions": {
    "type-def": [
      {
        "name": "Action",
        "definition": {
          "content": "(id: String, label: String, handler: () → Effect, type: {primary, secondary, destructive})",
          "format": "latex"
        },
        "description": "Menu action definition"
      },
      {
        "name": "Context",
        "definition": {
          "content": "(selection: Set⟨Element⟩, state: State, permissions: Set⟨Permission⟩)",
          "format": "latex"
        },
        "description": "Current context state"
      }
    ]
  }
}
EOF
)

patch_pattern "P39" "Contextual Action Menu" "$P39_PATCH"

#############################################
# P40: Mode Toggle System - PATCH
#############################################

P40_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P40.1",
        "name": "Mutual Exclusivity",
        "formal-spec": {
          "content": "∀t ∈ Time: ∃! m ∈ M: active(m, t)",
          "format": "latex"
        },
        "description": "Exactly one mode is active at any time",
        "invariants": {
          "invariant": [{"content": "single_active_mode", "format": "latex"}]
        }
      },
      {
        "id": "P.P40.2",
        "name": "Transition Atomicity",
        "formal-spec": {
          "content": "transition(mᵢ, mⱼ) = if δ(mᵢ, mⱼ) = allowed then mⱼ else mᵢ",
          "format": "latex"
        },
        "description": "Transitions are atomic; forbidden transitions leave state unchanged",
        "invariants": {
          "invariant": [{"content": "atomic_transitions", "format": "latex"}]
        }
      },
      {
        "id": "P.P40.3",
        "name": "UI Consistency",
        "formal-spec": {
          "content": "active(m) ⟹ UI_visible = φ(m)",
          "format": "latex"
        },
        "description": "Active mode determines visible UI elements",
        "invariants": {
          "invariant": [{"content": "mode_ui_binding", "format": "latex"}]
        }
      },
      {
        "id": "P.P40.4",
        "name": "Indicator Visibility",
        "formal-spec": {
          "content": "∀m ∈ M: visible(ι(m)) ∧ (highlight(ι(m)) ⟺ active(m))",
          "format": "latex"
        },
        "description": "All mode indicators visible, but only active mode is highlighted",
        "invariants": {
          "invariant": [{"content": "clear_indicators", "format": "latex"}]
        }
      },
      {
        "id": "P.P40.5",
        "name": "State Preservation",
        "formal-spec": {
          "content": "transition(mᵢ, mⱼ) ⟹ preserve(state(mᵢ)) ∧ restore(state(mⱼ))",
          "format": "latex"
        },
        "description": "Each mode preserves its internal state across transitions",
        "invariants": {
          "invariant": [{"content": "state_persistence", "format": "latex"}]
        }
      }
    ]
  },
  "definition": {
    "components": {
      "component": [
        {
          "name": "M",
          "type": "Set⟨Mode⟩",
          "notation": "M",
          "description": "finite set of **modes**"
        },
        {
          "name": "m₀",
          "type": "M",
          "notation": "m₀",
          "description": "**initial/default mode**"
        }
      ]
    }
  },
  "type-definitions": {
    "type-def": [
      {
        "name": "Mode",
        "definition": {
          "content": "(id: String, label: String, config: UIConfig, state: State)",
          "format": "latex"
        },
        "description": "Individual mode definition"
      },
      {
        "name": "UIConfig",
        "definition": {
          "content": "(visible_elements: Set⟨Element⟩, enabled_features: Set⟨Feature⟩, layout: Layout)",
          "format": "latex"
        },
        "description": "Mode-specific UI configuration"
      }
    ]
  }
}
EOF
)

patch_pattern "P40" "Mode Toggle System" "$P40_PATCH"

echo ""
echo "=========================================="
echo "Supplemental Patch Complete!"
echo "=========================================="
echo ""
echo "Patched P37-P40 with enhanced definitions"
echo "Run patch_patterns.sh to update P35, P36, P41-P47, F5"
echo ""
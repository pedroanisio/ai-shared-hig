#!/bin/bash

# Script to add new UI/UX patterns (P156-P160) to the Universal Corpus Pattern API
# API Base URL
API_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Function to add a pattern
add_pattern() {
    local pattern_id=$1
    local pattern_json=$2
    
    print_info "Adding pattern $pattern_id..."
    
    response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/patterns" \
        -H "Content-Type: application/json" \
        -d "$pattern_json")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 201 ]; then
        print_success "Pattern $pattern_id added successfully"
        return 0
    else
        print_error "Failed to add pattern $pattern_id (HTTP $http_code)"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
        return 1
    fi
}

# Check if API is reachable
print_info "Checking API connectivity..."
if ! curl -s -f "$API_URL/health" > /dev/null 2>&1; then
    print_error "Cannot connect to API at $API_URL"
    print_info "Please ensure the API server is running on localhost:8000"
    exit 1
fi
print_success "API is reachable"

echo ""
echo "=========================================="
echo "Adding New UI/UX Patterns (P156-P160)"
echo "=========================================="
echo ""

# Pattern P156: 3D Spatial Navigation
print_info "Preparing P156 - 3D Spatial Navigation"
add_pattern "P156" '{
  "id": "P156",
  "version": "1.0",
  "metadata": {
    "name": "3D Spatial Navigation",
    "category": "pattern",
    "status": "stable",
    "complexity": "high",
    "domains": {
      "domain": ["Spatial Computing", "3D Interfaces", "AR/VR", "Visualization"]
    },
    "last_updated": "2025-11-23"
  },
  "definition": {
    "tuple-notation": {
      "content": "$S_{3D} = (navigation, orientation, depth\\_cues, perspective) : Input \\to Position_{3D}$",
      "format": "latex"
    },
    "components": {
      "component": [
        {
          "name": "navigation",
          "type": "Controls",
          "notation": "navigation",
          "description": "Movement controls (rotate, pan, zoom) for 3D space traversal"
        },
        {
          "name": "orientation",
          "type": "ViewState",
          "notation": "orientation",
          "description": "User viewpoint state in 3D space (position, rotation, scale)"
        },
        {
          "name": "depth_cues",
          "type": "VisualIndicators",
          "notation": "depth\\_cues",
          "description": "Visual indicators of spatial relationships and depth"
        },
        {
          "name": "perspective",
          "type": "Transform3D",
          "notation": "perspective",
          "description": "Projection transformation from 3D to 2D viewport"
        }
      ]
    },
    "description": "3D Spatial Navigation enables users to traverse and orient themselves within three-dimensional information spaces through intuitive controls and visual feedback. This pattern is essential for spatial computing interfaces, VR/AR applications, and complex data visualizations."
  },
  "properties": {
    "property": [
      {
        "id": "P.P156.1",
        "name": "Continuous Navigation",
        "formal-spec": {
          "content": "$\\forall t \\in Time: position(t) = f(position(t-1), input(t))$ where $f$ is continuous",
          "format": "latex"
        },
        "description": "Navigation transitions are smooth and continuous without jarring jumps"
      },
      {
        "id": "P.P156.2",
        "name": "Orientation Preservation",
        "formal-spec": {
          "content": "$|rotation_x| \\leq \\pi \\land rotation_y \\bmod 2\\pi$ prevents gimbal lock",
          "format": "latex"
        },
        "description": "System maintains valid orientation state preventing mathematical singularities"
      },
      {
        "id": "P.P156.3",
        "name": "Depth Perception",
        "formal-spec": {
          "content": "$depth\\_cue = \\{perspective, occlusion, shadow, size\\_gradient\\}$ provides spatial awareness",
          "format": "latex"
        },
        "description": "Multiple visual cues combine to create effective depth perception"
      }
    ]
  },
  "operations": {
    "operation": [
      {
        "name": "Rotate",
        "signature": "rotate(delta_x: ℝ, delta_y: ℝ) → Orientation",
        "formal-definition": {
          "content": "$rotate(\\Delta x, \\Delta y) = (rotation_x - \\Delta y \\cdot sensitivity, rotation_y + \\Delta x \\cdot sensitivity)$",
          "format": "latex"
        },
        "preconditions": {
          "condition": [
            {
              "content": "$|\\Delta x|, |\\Delta y| < threshold$",
              "format": "latex"
            }
          ]
        },
        "postconditions": {
          "condition": [
            {
              "content": "$rotation\\_x \\in [-180, 180]$",
              "format": "latex"
            },
            {
              "content": "$rotation\\_y \\in [0, 360)$",
              "format": "latex"
            }
          ]
        },
        "effects": {
          "effect": [
            "Updates view orientation",
            "Triggers transform recalculation",
            "Emits orientation change event"
          ]
        }
      },
      {
        "name": "Pan",
        "signature": "pan(delta_x: ℝ, delta_y: ℝ, delta_z: ℝ) → Position3D",
        "formal-definition": {
          "content": "$pan(\\Delta x, \\Delta y, \\Delta z) = position + (\\Delta x, \\Delta y, \\Delta z)$",
          "format": "latex"
        },
        "effects": {
          "effect": [
            "Translates camera position",
            "Preserves orientation"
          ]
        }
      },
      {
        "name": "UpdateTransform",
        "signature": "updateTransform() → Matrix4x4",
        "formal-definition": {
          "content": "$transform = perspective \\cdot rotation \\cdot translation \\cdot scale$",
          "format": "latex"
        },
        "effects": {
          "effect": [
            "Composes transformation matrices",
            "Updates CSS transform3d",
            "Triggers re-render"
          ]
        }
      }
    ]
  },
  "dependencies": {
    "uses": {
      "pattern-ref": ["P2", "P8", "P50"]
    }
  },
  "manifestations": {
    "manifestation": [
      {
        "name": "Grid3D.js",
        "description": "3D grid visualization with mouse drag rotation, middle-click panning, keyboard navigation (arrow keys, PageUp/Down for Z-axis)"
      },
      {
        "name": "Three.js OrbitControls",
        "description": "Standard 3D camera control with rotate, pan, zoom operations"
      },
      {
        "name": "Apple Vision Pro Spatial UI",
        "description": "Hand gesture-based 3D navigation in mixed reality"
      },
      {
        "name": "Google Earth",
        "description": "Globe navigation with tilt, rotate, zoom controls"
      },
      {
        "name": "Blender 3D Viewport",
        "description": "Professional 3D navigation with multiple projection modes"
      }
    ]
  }
}'

echo ""

# Pattern P157: Inline Contextual Editing
print_info "Preparing P157 - Inline Contextual Editing"
add_pattern "P157" '{
  "id": "P157",
  "version": "1.0",
  "metadata": {
    "name": "Inline Contextual Editing",
    "category": "pattern",
    "status": "stable",
    "complexity": "medium",
    "domains": {
      "domain": ["Content Editing", "Direct Manipulation", "Contextual UI"]
    },
    "last_updated": "2025-11-23"
  },
  "definition": {
    "tuple-notation": {
      "content": "$E_{inline} = (trigger, edit\\_mode, constraints, finalize) : Element \\to Element_{modified}$",
      "format": "latex"
    },
    "components": {
      "component": [
        {
          "name": "trigger",
          "type": "Event",
          "notation": "trigger",
          "description": "User action that initiates editing (double-click, explicit button)"
        },
        {
          "name": "edit_mode",
          "type": "EditStrategy",
          "notation": "edit\\_mode",
          "description": "Editing interface type: {inline, floating, modal}"
        },
        {
          "name": "constraints",
          "type": "ValidationRules",
          "notation": "constraints",
          "description": "Validation and formatting rules applied during editing"
        },
        {
          "name": "finalize",
          "type": "CommitStrategy",
          "notation": "finalize",
          "description": "Mechanism to commit or cancel changes (Enter, Esc, blur)"
        }
      ]
    },
    "description": "Inline Contextual Editing enables seamless in-place content modification without modal dialogs or page transitions. Users can edit content directly where it appears, maintaining spatial and cognitive context."
  },
  "properties": {
    "property": [
      {
        "id": "P.P157.1",
        "name": "Context Preservation",
        "formal-spec": {
          "content": "$context_{before} \\approx context_{after}$ where context includes position, surroundings, and user focus",
          "format": "latex"
        },
        "description": "Editing maintains spatial and visual context"
      },
      {
        "id": "P.P157.2",
        "name": "Atomic Commit",
        "formal-spec": {
          "content": "$edit\\_state \\in \\{viewing, editing\\}$ with atomic transitions $viewing \\xrightarrow{trigger} editing \\xrightarrow{commit} viewing$",
          "format": "latex"
        },
        "description": "Edit operations complete atomically with no intermediate states"
      },
      {
        "id": "P.P157.3",
        "name": "Reversibility",
        "formal-spec": {
          "content": "$\\exists cancel: editing \\to viewing$ where $content = content_{original}$",
          "format": "latex"
        },
        "description": "Users can cancel edits and restore original content"
      }
    ]
  },
  "operations": {
    "operation": [
      {
        "name": "BeginEdit",
        "signature": "beginEdit(element: Element, mode: EditMode) → EditSession",
        "formal-definition": {
          "content": "$beginEdit(e, m) = \\{element: e, mode: m, original: e.content, state: editing\\}$",
          "format": "latex"
        },
        "preconditions": {
          "condition": [
            {
              "content": "$element.editable = true$",
              "format": "latex"
            },
            {
              "content": "$element.state \\neq editing$",
              "format": "latex"
            }
          ]
        },
        "postconditions": {
          "condition": [
            {
              "content": "$element.state = editing$",
              "format": "latex"
            },
            {
              "content": "$element.focus = true$",
              "format": "latex"
            }
          ]
        },
        "effects": {
          "effect": [
            "Enters edit mode",
            "Focuses edit control",
            "Selects existing content",
            "Emits editStart event"
          ]
        }
      },
      {
        "name": "CommitEdit",
        "signature": "commitEdit(session: EditSession) → Element",
        "formal-definition": {
          "content": "$commitEdit(s) = s.element \\leftarrow s.modified\\_content$ if $valid(s.modified\\_content)$",
          "format": "latex"
        },
        "preconditions": {
          "condition": [
            {
              "content": "$session.state = editing$",
              "format": "latex"
            },
            {
              "content": "$valid(session.modified\\_content)$",
              "format": "latex"
            }
          ]
        },
        "postconditions": {
          "condition": [
            {
              "content": "$element.content = modified\\_content$",
              "format": "latex"
            },
            {
              "content": "$element.state = viewing$",
              "format": "latex"
            }
          ]
        },
        "effects": {
          "effect": [
            "Updates element content",
            "Exits edit mode",
            "Emits editEnd event"
          ]
        }
      },
      {
        "name": "CancelEdit",
        "signature": "cancelEdit(session: EditSession) → Element",
        "formal-definition": {
          "content": "$cancelEdit(s) = s.element \\leftarrow s.original$",
          "format": "latex"
        },
        "effects": {
          "effect": [
            "Restores original content",
            "Exits edit mode",
            "Discards changes"
          ]
        }
      }
    ]
  },
  "dependencies": {
    "uses": {
      "pattern-ref": ["P2", "P7", "P11"]
    }
  },
  "manifestations": {
    "manifestation": [
      {
        "name": "Grid3D Cell Editing",
        "description": "Double-click for inline contentEditable, single-click for floating input overlay with Enter/Esc finalization"
      },
      {
        "name": "Notion Block Editing",
        "description": "Click any block to edit inline with rich formatting"
      },
      {
        "name": "Figma Text Editing",
        "description": "Double-click text to edit in-place with immediate visual feedback"
      },
      {
        "name": "Excel Cell Editing",
        "description": "F2 or double-click for inline cell editing with formula bar sync"
      },
      {
        "name": "Google Docs Inline Comments",
        "description": "Contextual comment editing without leaving document"
      }
    ]
  }
}'

echo ""

# Pattern P158: Ambient Visual Feedback Layer
print_info "Preparing P158 - Ambient Visual Feedback Layer"
add_pattern "P158" '{
  "id": "P158",
  "version": "1.0",
  "metadata": {
    "name": "Ambient Visual Feedback Layer",
    "category": "pattern",
    "status": "stable",
    "complexity": "medium",
    "domains": {
      "domain": ["Visual Feedback", "UI Effects", "System Awareness"]
    },
    "last_updated": "2025-11-23"
  },
  "definition": {
    "tuple-notation": {
      "content": "$A_{ambient} = (effects, triggers, intensity, persistence) : State\\_Change \\to Visual\\_Feedback$",
      "format": "latex"
    },
    "components": {
      "component": [
        {
          "name": "effects",
          "type": "Set⟨VisualTransform⟩",
          "notation": "effects",
          "description": "Set of visual transformations: {glow, pulse, particle, color_shift, scale}"
        },
        {
          "name": "triggers",
          "type": "StateChange → Boolean",
          "notation": "triggers",
          "description": "Conditions that activate feedback effects"
        },
        {
          "name": "intensity",
          "type": "[0, 1]",
          "notation": "intensity",
          "description": "Configurable feedback strength level"
        },
        {
          "name": "persistence",
          "type": "Duration × FadeFunction",
          "notation": "persistence",
          "description": "Duration and fade characteristics of effects"
        }
      ]
    },
    "description": "Ambient Visual Feedback Layer provides continuous, non-intrusive awareness of system state changes through subtle visual effects. Unlike explicit notifications, ambient feedback exists at the periphery of attention, supporting awareness without demanding focus."
  },
  "properties": {
    "property": [
      {
        "id": "P.P158.1",
        "name": "Non-Disruptive",
        "formal-spec": {
          "content": "$attention\\_demand(ambient\\_feedback) < threshold\\_interruption$",
          "format": "latex"
        },
        "description": "Feedback does not force context switch or interrupt workflow"
      },
      {
        "id": "P.P158.2",
        "name": "Proportional Response",
        "formal-spec": {
          "content": "$intensity\\_visual = f(importance\\_state\\_change)$ where $f$ is monotonic",
          "format": "latex"
        },
        "description": "Visual feedback intensity proportional to state change significance"
      },
      {
        "id": "P.P158.3",
        "name": "Performance Optimized",
        "formal-spec": {
          "content": "$fps \\geq 60 \\land frame\\_time < 16.67ms$ during effect rendering",
          "format": "latex"
        },
        "description": "Effects maintain 60fps performance through optimization"
      }
    ]
  },
  "operations": {
    "operation": [
      {
        "name": "TriggerEffect",
        "signature": "triggerEffect(element: Element, effect_type: EffectType, intensity: ℝ) → Animation",
        "formal-definition": {
          "content": "$triggerEffect(e, t, i) = \\{element: e, type: t, start: now(), intensity: i, state: active\\}$",
          "format": "latex"
        },
        "preconditions": {
          "condition": [
            {
              "content": "$intensity \\in [0, 1]$",
              "format": "latex"
            },
            {
              "content": "$effect\\_type \\in allowed\\_effects$",
              "format": "latex"
            }
          ]
        },
        "effects": {
          "effect": [
            "Applies CSS transition or animation",
            "Schedules effect cleanup",
            "Updates animation frame queue"
          ]
        }
      },
      {
        "name": "HoverEffect",
        "signature": "hoverEffect(element: Element) → Transform",
        "formal-definition": {
          "content": "$hover(e) = \\{border: highlight, scale: 1.05, shadow: glow\\}$ applied with timing function",
          "format": "latex"
        },
        "effects": {
          "effect": [
            "Increases visual prominence",
            "Provides interaction affordance",
            "Reverses on mouse leave"
          ]
        }
      },
      {
        "name": "PulseEffect",
        "signature": "pulseEffect(element: Element, duration: Time) → KeyframeAnimation",
        "formal-definition": {
          "content": "$pulse(e, d) = animate(e, \\{0\\%: scale(1), 50\\%: scale(1.1), 100\\%: scale(1.2)\\}, d)$",
          "format": "latex"
        },
        "effects": {
          "effect": [
            "Draws attention to element",
            "Indicates active state transition",
            "Self-terminates after duration"
          ]
        }
      }
    ]
  },
  "dependencies": {
    "uses": {
      "pattern-ref": ["P50", "P52", "P93"]
    }
  },
  "manifestations": {
    "manifestation": [
      {
        "name": "Grid3D Ambient Effects",
        "description": "Hover glow effects, edit pulse animation, agent activity particles with performance optimization (RAF)"
      },
      {
        "name": "macOS Focus Indicators",
        "description": "Subtle blue glow on focused elements without disrupting layout"
      },
      {
        "name": "VS Code Activity Bar Badges",
        "description": "Small numbered badges indicating background activity"
      },
      {
        "name": "Slack Presence Indicators",
        "description": "Green/yellow/gray dots showing user availability status"
      },
      {
        "name": "GitHub Loading Skeleton",
        "description": "Animated shimmer effect during content loading"
      }
    ]
  }
}'

echo ""

# Pattern P159: Progressive Accessibility Enhancement
print_info "Preparing P159 - Progressive Accessibility Enhancement"
add_pattern "P159" '{
  "id": "P159",
  "version": "1.0",
  "metadata": {
    "name": "Progressive Accessibility Enhancement",
    "category": "pattern",
    "status": "stable",
    "complexity": "high",
    "domains": {
      "domain": ["Accessibility", "Inclusive Design", "ARIA", "Assistive Technology"]
    },
    "last_updated": "2025-11-23"
  },
  "definition": {
    "tuple-notation": {
      "content": "$A_{progressive} = (base\\_ux, aria\\_layer, keyboard\\_nav, announcements) : Interaction \\to Accessible\\_Interaction$",
      "format": "latex"
    },
    "components": {
      "component": [
        {
          "name": "base_ux",
          "type": "CoreInteraction",
          "notation": "base\\_ux",
          "description": "Core visual interaction patterns (mouse, touch)"
        },
        {
          "name": "aria_layer",
          "type": "SemanticMarkup",
          "notation": "aria\\_layer",
          "description": "ARIA labels, roles, states, and live regions"
        },
        {
          "name": "keyboard_nav",
          "type": "KeyboardInterface",
          "notation": "keyboard\\_nav",
          "description": "Complete keyboard alternative to mouse interactions"
        },
        {
          "name": "announcements",
          "type": "ScreenReaderNotifications",
          "notation": "announcements",
          "description": "Dynamic content announcements for screen readers"
        }
      ]
    },
    "description": "Progressive Accessibility Enhancement layers accessibility features progressively atop core functionality, ensuring inclusive access without compromising visual design. Each layer enhances access for different assistive technologies while maintaining a unified user experience."
  },
  "properties": {
    "property": [
      {
        "id": "P.P159.1",
        "name": "Semantic Equivalence",
        "formal-spec": {
          "content": "$\\forall action \\in base\\_ux: \\exists accessible\\_action \\in (keyboard\\_nav \\cup aria\\_layer)$ with equivalent outcome",
          "format": "latex"
        },
        "description": "Every visual interaction has an accessible equivalent"
      },
      {
        "id": "P.P159.2",
        "name": "Progressive Degradation",
        "formal-spec": {
          "content": "$functionality_{full} \\supseteq functionality_{accessible} \\supseteq functionality_{minimal}$ preserving core features",
          "format": "latex"
        },
        "description": "Features remain functional as enhancement layers are removed"
      },
      {
        "id": "P.P159.3",
        "name": "Screen Reader Compatibility",
        "formal-spec": {
          "content": "$\\forall state\\_change: announcement\\_timing \\in (immediate, polite, assertive)$ based on priority",
          "format": "latex"
        },
        "description": "Dynamic changes are announced appropriately to screen readers"
      }
    ]
  },
  "operations": {
    "operation": [
      {
        "name": "AddARIASemantics",
        "signature": "addARIA(element: Element, role: ARIARole, label: String) → Element",
        "formal-definition": {
          "content": "$addARIA(e, r, l) = e \\cup \\{role: r, aria-label: l, tabindex: 0\\}$",
          "format": "latex"
        },
        "preconditions": {
          "condition": [
            {
              "content": "$role \\in valid\\_aria\\_roles$",
              "format": "latex"
            },
            {
              "content": "$label \\neq empty$",
              "format": "latex"
            }
          ]
        },
        "effects": {
          "effect": [
            "Adds semantic role to element",
            "Provides accessible name",
            "Enables keyboard focus"
          ]
        }
      },
      {
        "name": "AnnounceToScreenReader",
        "signature": "announce(message: String, priority: Priority) → Effect",
        "formal-definition": {
          "content": "$announce(m, p) = liveRegion.textContent \\leftarrow m$ where $liveRegion.aria-live = p$",
          "format": "latex"
        },
        "preconditions": {
          "condition": [
            {
              "content": "$priority \\in \\{polite, assertive, off\\}$",
              "format": "latex"
            }
          ]
        },
        "effects": {
          "effect": [
            "Updates aria-live region",
            "Triggers screen reader announcement",
            "Self-cleans after timeout"
          ]
        }
      },
      {
        "name": "EnableKeyboardNav",
        "signature": "enableKeyboard(container: Element, nav_map: KeyMap) → EventListeners",
        "formal-definition": {
          "content": "$enableKeyboard(c, m) = \\forall k \\in m: addEventListener(c, keydown, m[k])$",
          "format": "latex"
        },
        "effects": {
          "effect": [
            "Registers keyboard event handlers",
            "Enables arrow key navigation",
            "Provides keyboard shortcuts",
            "Handles Tab/Shift+Tab focus management"
          ]
        }
      }
    ]
  },
  "dependencies": {
    "uses": {
      "pattern-ref": ["P1", "P2", "P7", "P8"]
    }
  },
  "manifestations": {
    "manifestation": [
      {
        "name": "Grid3D Accessibility Layer",
        "description": "Full ARIA labels on cells, arrow key 3D navigation, PageUp/Down for Z-axis, aria-live announcements, hidden instruction div"
      },
      {
        "name": "GOV.UK Design System",
        "description": "Progressive enhancement from HTML semantics to ARIA to JavaScript interactions"
      },
      {
        "name": "Material UI Components",
        "description": "Built-in keyboard navigation, ARIA attributes, focus management"
      },
      {
        "name": "Shopify Polaris",
        "description": "Comprehensive accessibility with screen reader testing and keyboard support"
      },
      {
        "name": "Adobe Spectrum",
        "description": "Accessibility-first component design with ARIA patterns"
      }
    ]
  }
}'

echo ""

# Pattern P160: Collaborative Task Visualization
print_info "Preparing P160 - Collaborative Task Visualization"
add_pattern "P160" '{
  "id": "P160",
  "version": "1.0",
  "metadata": {
    "name": "Collaborative Task Visualization",
    "category": "pattern",
    "status": "stable",
    "complexity": "high",
    "domains": {
      "domain": ["Task Management", "Spatial Metaphors", "Multi-Agent", "Workflow"]
    },
    "last_updated": "2025-11-23"
  },
  "definition": {
    "tuple-notation": {
      "content": "$T_{spatial} = (tasks, spatial\\_map, agent\\_viz, progress\\_indicators) : Task\\_Queue \\to Spatial\\_Layout$",
      "format": "latex"
    },
    "components": {
      "component": [
        {
          "name": "tasks",
          "type": "Queue⟨Task⟩",
          "notation": "tasks",
          "description": "Work items with metadata (priority, assignee, status, dependencies)"
        },
        {
          "name": "spatial_map",
          "type": "Task → Position3D",
          "notation": "spatial\\_map",
          "description": "Function assigning tasks to spatial positions"
        },
        {
          "name": "agent_viz",
          "type": "Agent → Visual",
          "notation": "agent\\_viz",
          "description": "Visual representation of agent activity and assignment"
        },
        {
          "name": "progress_indicators",
          "type": "Status → VisualState",
          "notation": "progress\\_indicators",
          "description": "Real-time status overlays (pending, active, complete, blocked)"
        }
      ]
    },
    "description": "Collaborative Task Visualization uses spatial metaphors to organize and display work items, enabling teams and AI agents to coordinate through visual proximity and organization. Tasks are mapped to physical or virtual space, with agent assignments and progress indicated spatially."
  },
  "properties": {
    "property": [
      {
        "id": "P.P160.1",
        "name": "Spatial Coherence",
        "formal-spec": {
          "content": "$related(t_1, t_2) \\implies distance(position(t_1), position(t_2)) < threshold$",
          "format": "latex"
        },
        "description": "Related tasks are positioned near each other in space"
      },
      {
        "id": "P.P160.2",
        "name": "Agent Task Binding",
        "formal-spec": {
          "content": "$\\forall task \\in active\\_tasks: \\exists! agent$ where $assigned(agent, task)$",
          "format": "latex"
        },
        "description": "Each active task has exactly one assigned agent"
      },
      {
        "id": "P.P160.3",
        "name": "Visual Status Consistency",
        "formal-spec": {
          "content": "$\\forall t: visual\\_state(t) = f(task\\_status(t))$ where $f$ is deterministic",
          "format": "latex"
        },
        "description": "Visual representation accurately reflects current task status"
      }
    ]
  },
  "operations": {
    "operation": [
      {
        "name": "AssignTaskToSpace",
        "signature": "assignToSpace(task: Task, position: Position3D) → Mapping",
        "formal-definition": {
          "content": "$assignToSpace(t, p) = spatial\\_map \\cup \\{t \\mapsto p\\}$",
          "format": "latex"
        },
        "preconditions": {
          "condition": [
            {
              "content": "$position \\in valid\\_space$",
              "format": "latex"
            },
            {
              "content": "$\\neg occupied(position)$",
              "format": "latex"
            }
          ]
        },
        "effects": {
          "effect": [
            "Maps task to spatial location",
            "Renders task visualization at position",
            "Updates spatial index"
          ]
        }
      },
      {
        "name": "AssignAgentToTask",
        "signature": "assignAgent(agent: Agent, task: Task) → Assignment",
        "formal-definition": {
          "content": "$assignAgent(a, t) = \\{agent: a, task: t, start: now(), status: active\\}$",
          "format": "latex"
        },
        "preconditions": {
          "condition": [
            {
              "content": "$agent.status = available$",
              "format": "latex"
            },
            {
              "content": "$task.status = pending$",
              "format": "latex"
            }
          ]
        },
        "postconditions": {
          "condition": [
            {
              "content": "$agent.assigned\\_task = task$",
              "format": "latex"
            },
            {
              "content": "$task.assigned\\_agent = agent$",
              "format": "latex"
            }
          ]
        },
        "effects": {
          "effect": [
            "Links agent to task",
            "Updates visual indicators",
            "Emits assignment event",
            "Changes task status to active"
          ]
        }
      },
      {
        "name": "UpdateTaskStatus",
        "signature": "updateStatus(task: Task, new_status: Status) → Task",
        "formal-definition": {
          "content": "$updateStatus(t, s) = t \\leftarrow \\{status: s, updated: now()\\}$",
          "format": "latex"
        },
        "effects": {
          "effect": [
            "Updates task metadata",
            "Changes visual representation",
            "Notifies observers",
            "May trigger reassignment"
          ]
        }
      }
    ]
  },
  "dependencies": {
    "uses": {
      "pattern-ref": ["P68", "P69", "P71", "P78", "P156"]
    }
  },
  "manifestations": {
    "manifestation": [
      {
        "name": "Grid3D Task Management",
        "description": "Tasks assigned to 3D grid cells with agent indicators, color-coded priority, status classes (active, pending, complete)"
      },
      {
        "name": "Trello Board",
        "description": "Cards in columns representing task workflow stages with assignee avatars"
      },
      {
        "name": "Jira Board",
        "description": "Issues in swimlanes with priority colors and assignee indicators"
      },
      {
        "name": "Miro Kanban",
        "description": "Spatial canvas with sticky notes representing tasks in freeform positions"
      },
      {
        "name": "Asana Timeline",
        "description": "Gantt-style visualization with tasks positioned by time and assigned to team members"
      }
    ]
  }
}'

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""
print_success "All 5 patterns (P156-P160) submitted to API"
echo ""
print_info "Verify patterns were added:"
echo "curl http://localhost:8000/patterns?limit=200 | jq '.[] | select(.id | startswith(\"P15\"))'"
echo ""
print_info "View specific pattern:"
echo "curl http://localhost:8000/patterns/P156 | jq ."
echo ""
print_info "Get pattern as XML:"
echo "curl http://localhost:8000/patterns/P156/xml"
echo ""

exit 0
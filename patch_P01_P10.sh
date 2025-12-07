#!/bin/bash

# Phase 1 Quality Fix: P1-P10 (Core UI Patterns)
# Addresses: incomplete formalization, weak invariants, missing temporal specs
# Target API: localhost:8000

BASE_URL="http://localhost:8000"
CONTENT_TYPE="Content-Type: application/json"

echo "=========================================="
echo "Phase 1 Batch 1: Patching P1-P10"
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
# P1: Immediate Feedback - PATCH
#############################################

P1_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P1.1",
        "name": "Response Time Bound",
        "formal-spec": {
          "content": "∀a ∈ Actions, ∀t ∈ Time: execute(a, t) ⟹ ∃f ∈ Feedback: visible(f, t + δ) where δ < 100ms",
          "format": "latex"
        },
        "description": "Visual feedback appears within 100ms of any action",
        "invariants": {
          "invariant": [
            {
              "content": "∀a ∈ Actions: response_time(a) < τ_immediate where τ_immediate = 100ms",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P1.2",
        "name": "Feedback Visibility",
        "formal-spec": {
          "content": "∀a ∈ Actions: executed(a) ⟹ ∃f ∈ Feedback: visible(f) ∧ associated(f, a)",
          "format": "latex"
        },
        "description": "Every action has associated visible feedback",
        "invariants": {
          "invariant": [
            {
              "content": "∀a ∈ Actions: ∃!f ∈ Feedback: maps_to(a, f)",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P1.3",
        "name": "Feedback Persistence",
        "formal-spec": {
          "content": "∀f ∈ Feedback: duration(f) ∈ [τ_min, τ_max] where τ_min = 150ms ∧ τ_max = 3000ms",
          "format": "latex"
        },
        "description": "Feedback persists for perceptible but bounded duration",
        "invariants": {
          "invariant": [
            {
              "content": "∀f ∈ Feedback: τ_min ≤ display_time(f) ≤ τ_max",
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
        "name": "Action",
        "definition": {
          "content": "(id: String, trigger: Event, timestamp: Time)",
          "format": "latex"
        },
        "description": "User action that requires feedback"
      },
      {
        "name": "Feedback",
        "definition": {
          "content": "(type: {visual, auditory, haptic}, intensity: ℝ₊, duration: ℝ₊)",
          "format": "latex"
        },
        "description": "Feedback response to action"
      },
      {
        "name": "Time",
        "definition": {
          "content": "ℝ₊ (milliseconds since epoch)",
          "format": "latex"
        },
        "description": "Temporal type for timing constraints"
      }
    ]
  },
  "operations": {
    "operation": [
      {
        "name": "execute",
        "signature": "execute(a: Action, t: Time) → Effect",
        "formal-definition": {
          "content": "execute(a, t) = schedule(show_feedback(a), t + ε) where ε ≈ 0",
          "format": "latex"
        },
        "preconditions": {
          "condition": [
            {"content": "enabled(a.trigger)", "format": "latex"},
            {"content": "¬processing(a)", "format": "latex"}
          ]
        },
        "postconditions": {
          "condition": [
            {"content": "∃f ∈ Feedback: visible(f) ∧ timestamp(f) - t < 100ms", "format": "latex"}
          ]
        },
        "complexity": "O(1) time, O(1) space"
      }
    ]
  }
}
EOF
)

patch_pattern "P1" "Immediate Feedback" "$P1_PATCH"

#############################################
# P2: Progressive Disclosure - PATCH
#############################################

P2_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P2.1",
        "name": "Information Hierarchy",
        "formal-spec": {
          "content": "∀l ∈ Levels: importance(l) > importance(l+1) ⟹ visible(l) before visible(l+1)",
          "format": "latex"
        },
        "description": "More important information revealed before less important",
        "invariants": {
          "invariant": [
            {
              "content": "∀i, j ∈ ℕ: i < j ⟹ revealed(level_i) ≤ revealed(level_j) in timeline",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P2.2",
        "name": "Reveal Atomicity",
        "formal-spec": {
          "content": "∀l ∈ Levels: reveal(l) is atomic ∧ duration(reveal(l)) < τ_transition",
          "format": "latex"
        },
        "description": "Each disclosure level reveals atomically with bounded duration",
        "invariants": {
          "invariant": [
            {
              "content": "∀l ∈ Levels: transition_time(hidden → visible, l) < 300ms",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P2.3",
        "name": "Collapse Reversibility",
        "formal-spec": {
          "content": "∀l ∈ Levels: visible(l) ⟹ ∃collapse(l): visible(l) → hidden(l) ∧ state_preserved(l)",
          "format": "latex"
        },
        "description": "All disclosed information can be collapsed reversibly",
        "invariants": {
          "invariant": [
            {
              "content": "∀l ∈ Levels: state_before_reveal(l) = state_after_collapse(l)",
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
        "name": "Level",
        "definition": {
          "content": "(depth: ℕ, content: Content, state: {hidden, visible}, importance: ℝ₊)",
          "format": "latex"
        },
        "description": "Disclosure hierarchy level"
      },
      {
        "name": "Content",
        "definition": {
          "content": "Element | List⟨Element⟩",
          "format": "latex"
        },
        "description": "Disclosed content structure"
      }
    ]
  },
  "state-machine": {
    "states": ["hidden", "transitioning", "visible"],
    "initial": "hidden",
    "transitions": [
      {"from": "hidden", "to": "transitioning", "on": "reveal_trigger", "guard": "user_action"},
      {"from": "transitioning", "to": "visible", "on": "animation_complete", "guard": "duration < τ_max"},
      {"from": "visible", "to": "hidden", "on": "collapse_trigger", "guard": "user_action"}
    ]
  }
}
EOF
)

patch_pattern "P2" "Progressive Disclosure" "$P2_PATCH"

#############################################
# P3: Undo/Redo Stack - PATCH
#############################################

P3_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P3.1",
        "name": "Stack Integrity",
        "formal-spec": {
          "content": "∀t ∈ Time: |past(t)| + |future(t)| ≤ capacity ∧ consistent(past ∪ {present} ∪ future)",
          "format": "latex"
        },
        "description": "History stack maintains bounded size and consistency",
        "invariants": {
          "invariant": [
            {
              "content": "size(past) + size(future) ≤ MAX_HISTORY where MAX_HISTORY = 100",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P3.2",
        "name": "Undo Semantics",
        "formal-spec": {
          "content": "undo(state_n) = state_{n-1} ⟹ push(state_n, future) ∧ pop(past) = state_{n-1}",
          "format": "latex"
        },
        "description": "Undo restores previous state and preserves current in future stack",
        "invariants": {
          "invariant": [
            {
              "content": "∀s ∈ States: undo(s) = prev(s) ∧ can_redo()",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P3.3",
        "name": "Redo Invalidation",
        "formal-spec": {
          "content": "∀a ∈ Actions: execute(a) ⟹ future := ∅",
          "format": "latex"
        },
        "description": "New action clears redo stack",
        "invariants": {
          "invariant": [
            {
              "content": "new_action() ⟹ |future_stack| = 0",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P3.4",
        "name": "State Serialization",
        "formal-spec": {
          "content": "∀s ∈ States: serializable(s) ∧ deserialize(serialize(s)) = s",
          "format": "latex"
        },
        "description": "All states can be serialized and restored exactly",
        "invariants": {
          "invariant": [
            {
              "content": "∀s: serialize(s) is pure function ∧ size(serialize(s)) < MAX_STATE_SIZE",
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
        "name": "State",
        "definition": {
          "content": "(data: Serializable, timestamp: Time, action_id: String)",
          "format": "latex"
        },
        "description": "Snapshot of application state"
      },
      {
        "name": "HistoryStack",
        "definition": {
          "content": "(past: Stack⟨State⟩, present: State, future: Stack⟨State⟩)",
          "format": "latex"
        },
        "description": "Complete undo/redo state"
      }
    ]
  },
  "operations": {
    "operation": [
      {
        "name": "undo",
        "signature": "undo() → State",
        "formal-definition": {
          "content": "undo() = if |past| > 0 then (push(present, future); present := pop(past)) else present",
          "format": "latex"
        },
        "preconditions": {
          "condition": [{"content": "|past| > 0", "format": "latex"}]
        },
        "postconditions": {
          "condition": [
            {"content": "present = old_past.top", "format": "latex"},
            {"content": "|future| = old_future.size + 1", "format": "latex"}
          ]
        },
        "complexity": "O(1) time, O(n) space where n = history size"
      },
      {
        "name": "redo",
        "signature": "redo() → State",
        "formal-definition": {
          "content": "redo() = if |future| > 0 then (push(present, past); present := pop(future)) else present",
          "format": "latex"
        },
        "preconditions": {
          "condition": [{"content": "|future| > 0", "format": "latex"}]
        },
        "postconditions": {
          "condition": [
            {"content": "present = old_future.top", "format": "latex"},
            {"content": "|past| = old_past.size + 1", "format": "latex"}
          ]
        },
        "complexity": "O(1) time, O(n) space"
      }
    ]
  }
}
EOF
)

patch_pattern "P3" "Undo/Redo Stack" "$P3_PATCH"

#############################################
# P4: Loading States - PATCH
#############################################

P4_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P4.1",
        "name": "State Exclusivity",
        "formal-spec": {
          "content": "∀t ∈ Time: ∃!s ∈ {idle, loading, success, error}: state(t) = s",
          "format": "latex"
        },
        "description": "Exactly one loading state active at any time",
        "invariants": {
          "invariant": [
            {
              "content": "state ∈ {idle, loading, success, error} ∧ unique(state)",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P4.2",
        "name": "Progress Indication",
        "formal-spec": {
          "content": "state = loading ∧ duration > τ_threshold ⟹ visible(progress_indicator) where τ_threshold = 200ms",
          "format": "latex"
        },
        "description": "Loading indicator appears after delay threshold",
        "invariants": {
          "invariant": [
            {
              "content": "loading_time > 200ms ⟹ ∃indicator: visible(indicator)",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P4.3",
        "name": "Timeout Guarantee",
        "formal-spec": {
          "content": "state = loading ∧ t > τ_timeout ⟹ state := error where τ_timeout = 30s",
          "format": "latex"
        },
        "description": "Loading state transitions to error after timeout",
        "invariants": {
          "invariant": [
            {
              "content": "∀loading_operation: duration(loading) ≤ MAX_TIMEOUT",
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
        "name": "LoadingState",
        "definition": {
          "content": "Idle | Loading(progress: Option⟨ℝ[0,1]⟩) | Success(data: T) | Error(message: String)",
          "format": "latex"
        },
        "description": "Algebraic data type for loading states"
      },
      {
        "name": "ProgressIndicator",
        "definition": {
          "content": "(type: {spinner, bar, skeleton}, progress: Option⟨ℝ[0,1]⟩)",
          "format": "latex"
        },
        "description": "Visual loading indicator configuration"
      }
    ]
  },
  "state-machine": {
    "states": ["idle", "loading", "success", "error"],
    "initial": "idle",
    "transitions": [
      {"from": "idle", "to": "loading", "on": "start_operation", "guard": "true"},
      {"from": "loading", "to": "success", "on": "operation_complete", "guard": "data_valid"},
      {"from": "loading", "to": "error", "on": "operation_failed", "guard": "true"},
      {"from": "loading", "to": "error", "on": "timeout", "guard": "elapsed > τ_timeout"},
      {"from": "success", "to": "idle", "on": "reset", "guard": "true"},
      {"from": "error", "to": "idle", "on": "retry", "guard": "true"}
    ]
  }
}
EOF
)

patch_pattern "P4" "Loading States" "$P4_PATCH"

#############################################
# P5: Error Boundary - PATCH
#############################################

P5_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P5.1",
        "name": "Error Containment",
        "formal-spec": {
          "content": "∀e ∈ Errors, ∀c ∈ Components: error_in(c) ⟹ ¬propagates_to(parent(c)) ∧ caught_by(boundary(c))",
          "format": "latex"
        },
        "description": "Errors contained within boundary, don't propagate to parent",
        "invariants": {
          "invariant": [
            {
              "content": "∀error: caught(error) ⟹ ∀ancestor: ¬affected(ancestor)",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P5.2",
        "name": "Graceful Degradation",
        "formal-spec": {
          "content": "∀c ∈ Components: error(c) ⟹ render(fallback(c)) ∧ siblings(c) still operational",
          "format": "latex"
        },
        "description": "Failed component replaced with fallback, siblings unaffected",
        "invariants": {
          "invariant": [
            {
              "content": "error_state(component) ⟹ visible(fallback_ui) ∧ functional(siblings)",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P5.3",
        "name": "Error Reporting",
        "formal-spec": {
          "content": "∀e ∈ Errors: caught(e) ⟹ ∃log: recorded(e, log) ∧ timestamp(log) = time(e)",
          "format": "latex"
        },
        "description": "All caught errors are logged with timestamp",
        "invariants": {
          "invariant": [
            {
              "content": "∀caught_error: ∃log_entry: contains(log_entry, error_details)",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P5.4",
        "name": "Recovery Mechanism",
        "formal-spec": {
          "content": "∀c ∈ Components: error_state(c) ⟹ ∃retry: retry(c) attempts recovery",
          "format": "latex"
        },
        "description": "Error boundaries provide recovery mechanism",
        "invariants": {
          "invariant": [
            {
              "content": "∀boundary: has_recovery_action(boundary)",
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
        "name": "ErrorBoundary",
        "definition": {
          "content": "(children: List⟨Component⟩, fallback: Component, onError: Error → Effect, retry: () → Effect)",
          "format": "latex"
        },
        "description": "Error boundary container"
      },
      {
        "name": "Error",
        "definition": {
          "content": "(type: ErrorType, message: String, stack: String, timestamp: Time, component: String)",
          "format": "latex"
        },
        "description": "Error information structure"
      },
      {
        "name": "ErrorType",
        "definition": {
          "content": "RenderError | DataError | NetworkError | UnknownError",
          "format": "latex"
        },
        "description": "Categorized error types"
      }
    ]
  },
  "state-machine": {
    "states": ["normal", "error", "recovering"],
    "initial": "normal",
    "transitions": [
      {"from": "normal", "to": "error", "on": "error_thrown", "guard": "true"},
      {"from": "error", "to": "recovering", "on": "retry_clicked", "guard": "true"},
      {"from": "recovering", "to": "normal", "on": "recovery_success", "guard": "true"},
      {"from": "recovering", "to": "error", "on": "recovery_failed", "guard": "true"}
    ]
  }
}
EOF
)

patch_pattern "P5" "Error Boundary" "$P5_PATCH"

#############################################
# P6: Optimistic Update - PATCH
#############################################

P6_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P6.1",
        "name": "Immediate UI Update",
        "formal-spec": {
          "content": "∀action: submit(action) ⟹ UI_state := predicted_state immediately ∧ server_request(action) in background",
          "format": "latex"
        },
        "description": "UI updates instantly with predicted state before server confirms",
        "invariants": {
          "invariant": [
            {
              "content": "∀update: time(UI_update) < time(server_response)",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P6.2",
        "name": "Rollback on Failure",
        "formal-spec": {
          "content": "server_response = error ⟹ UI_state := saved_state ∧ show_error_message",
          "format": "latex"
        },
        "description": "Failed operations rollback to previous state",
        "invariants": {
          "invariant": [
            {
              "content": "∀failed_update: final_state = state_before_attempt",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P6.3",
        "name": "State Reconciliation",
        "formal-spec": {
          "content": "server_response = success(data) ⟹ UI_state := reconcile(predicted_state, data)",
          "format": "latex"
        },
        "description": "Successful response reconciles predicted with actual state",
        "invariants": {
          "invariant": [
            {
              "content": "∀success_response: final_state = authoritative_server_state",
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
        "name": "OptimisticUpdate",
        "definition": {
          "content": "(predicted_state: State, saved_state: State, pending_request: Promise⟨Response⟩)",
          "format": "latex"
        },
        "description": "Optimistic update tracking"
      },
      {
        "name": "Response",
        "definition": {
          "content": "Success(data: T) | Error(message: String, code: ℕ)",
          "format": "latex"
        },
        "description": "Server response types"
      }
    ]
  },
  "operations": {
    "operation": [
      {
        "name": "optimistic_update",
        "signature": "optimistic_update(action: Action) → Effect",
        "formal-definition": {
          "content": "optimistic_update(a) = (save(current_state); apply_predicted(a); send_to_server(a))",
          "format": "latex"
        },
        "preconditions": {
          "condition": [
            {"content": "valid(action)", "format": "latex"},
            {"content": "¬pending(same_resource)", "format": "latex"}
          ]
        },
        "postconditions": {
          "condition": [
            {"content": "UI_reflects(predicted_state)", "format": "latex"},
            {"content": "saved_state = original_state", "format": "latex"},
            {"content": "∃request: pending(request)", "format": "latex"}
          ]
        },
        "complexity": "O(1) time for UI update, O(n) network latency"
      }
    ]
  }
}
EOF
)

patch_pattern "P6" "Optimistic Update" "$P6_PATCH"

#############################################
# P7: Skeleton Screen - PATCH
#############################################

P7_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P7.1",
        "name": "Layout Preservation",
        "formal-spec": {
          "content": "∀component: layout(skeleton(component)) ≈ layout(loaded(component)) where similarity ≥ 0.9",
          "format": "latex"
        },
        "description": "Skeleton layout matches final content layout",
        "invariants": {
          "invariant": [
            {
              "content": "∀transition: content_shift(skeleton → loaded) < 5% viewport height",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P7.2",
        "name": "Progressive Reveal",
        "formal-spec": {
          "content": "∀chunks: skeleton_parts revealed in order(importance) with animation_duration < 200ms per chunk",
          "format": "latex"
        },
        "description": "Content revealed progressively as it loads",
        "invariants": {
          "invariant": [
            {
              "content": "∀chunk: reveal_time(chunk_i) ≤ reveal_time(chunk_{i+1})",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P7.3",
        "name": "Animation Subtlety",
        "formal-spec": {
          "content": "∀skeleton: has_pulse_animation(skeleton) ∧ frequency ∈ [0.5Hz, 2Hz] ∧ opacity_range = [0.3, 0.7]",
          "format": "latex"
        },
        "description": "Subtle pulsing animation indicates loading",
        "invariants": {
          "invariant": [
            {
              "content": "animation_parameters within_accessibility_guidelines",
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
        "name": "Skeleton",
        "definition": {
          "content": "(shapes: List⟨Shape⟩, animation: PulseAnimation, layout: LayoutBox)",
          "format": "latex"
        },
        "description": "Skeleton screen structure"
      },
      {
        "name": "Shape",
        "definition": {
          "content": "(type: {rectangle, circle, text_line}, dimensions: Box, color: Color)",
          "format": "latex"
        },
        "description": "Individual skeleton shape"
      },
      {
        "name": "PulseAnimation",
        "definition": {
          "content": "(frequency: ℝ[0.5,2], opacity_min: ℝ[0,1], opacity_max: ℝ[0,1])",
          "format": "latex"
        },
        "description": "Pulsing animation parameters"
      }
    ]
  }
}
EOF
)

patch_pattern "P7" "Skeleton Screen" "$P7_PATCH"

#############################################
# P8: Search-Based Navigation - PATCH
#############################################

P8_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P8.1",
        "name": "Incremental Search",
        "formal-spec": {
          "content": "∀q ∈ Queries: |q| ≥ min_length ⟹ results(q) computed ∧ displayed within τ_response where τ_response < 300ms",
          "format": "latex"
        },
        "description": "Search results appear incrementally as user types",
        "invariants": {
          "invariant": [
            {
              "content": "∀query: response_time(query) < 300ms ∨ show_loading_indicator",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P8.2",
        "name": "Ranking Stability",
        "formal-spec": {
          "content": "∀q: rank(results(q)) = score_function(relevance, recency, authority) ∧ deterministic",
          "format": "latex"
        },
        "description": "Search ranking is deterministic and based on defined scoring",
        "invariants": {
          "invariant": [
            {
              "content": "∀q, t₁, t₂: (q, context) same ⟹ rank(results(q, t₁)) = rank(results(q, t₂))",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P8.3",
        "name": "Debouncing",
        "formal-spec": {
          "content": "∀keystrokes: search_executed ⟺ time_since_last_keystroke > τ_debounce where τ_debounce ∈ [150ms, 300ms]",
          "format": "latex"
        },
        "description": "Search queries debounced to reduce server load",
        "invariants": {
          "invariant": [
            {
              "content": "∀rapid_typing: actual_queries << keystroke_count",
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
        "name": "Query",
        "definition": {
          "content": "(text: String, filters: List⟨Filter⟩, timestamp: Time)",
          "format": "latex"
        },
        "description": "Search query structure"
      },
      {
        "name": "Result",
        "definition": {
          "content": "(item: T, score: ℝ₊, highlights: List⟨Span⟩)",
          "format": "latex"
        },
        "description": "Search result with scoring"
      },
      {
        "name": "Index",
        "definition": {
          "content": "InvertedIndex⟨Term, List⟨DocID⟩⟩",
          "format": "latex"
        },
        "description": "Search index structure"
      }
    ]
  },
  "operations": {
    "operation": [
      {
        "name": "search",
        "signature": "search(q: Query, index: Index) → List⟨Result⟩",
        "formal-definition": {
          "content": "search(q, idx) = sort_by_score(filter(idx.lookup(tokenize(q))))",
          "format": "latex"
        },
        "preconditions": {
          "condition": [
            {"content": "|q.text| ≥ min_query_length", "format": "latex"},
            {"content": "index_ready(idx)", "format": "latex"}
          ]
        },
        "postconditions": {
          "condition": [
            {"content": "∀r ∈ results: r.score = score_function(r, q)", "format": "latex"},
            {"content": "sorted_descending(results, by: score)", "format": "latex"}
          ]
        },
        "complexity": "O(log n + k) where n = index size, k = results count"
      }
    ]
  }
}
EOF
)

patch_pattern "P8" "Search-Based Navigation" "$P8_PATCH"

#############################################
# P9: Keyboard Shortcuts - PATCH
#############################################

P9_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P9.1",
        "name": "Unique Bindings",
        "formal-spec": {
          "content": "∀k ∈ Keybindings, ∀ctx ∈ Contexts: binding(k, ctx) maps to at most one action",
          "format": "latex"
        },
        "description": "Each key combination maps to unique action in given context",
        "invariants": {
          "invariant": [
            {
              "content": "∀context: injective(keybinding → action) within context",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P9.2",
        "name": "Context Hierarchy",
        "formal-spec": {
          "content": "∀k, ctx_child, ctx_parent: binding(k, ctx_child) overrides binding(k, ctx_parent)",
          "format": "latex"
        },
        "description": "More specific contexts override parent context bindings",
        "invariants": {
          "invariant": [
            {
              "content": "∀key: resolution_order = [local_context, parent_context, global_context]",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P9.3",
        "name": "Discoverability",
        "formal-spec": {
          "content": "∀action: has_keybinding(action) ⟹ ∃ui_hint: visible(ui_hint) ∧ describes(ui_hint, keybinding(action))",
          "format": "latex"
        },
        "description": "Keyboard shortcuts are discoverable through UI hints",
        "invariants": {
          "invariant": [
            {
              "content": "∀visible_action: keybinding_hint displayed in tooltip or menu",
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
        "name": "Keybinding",
        "definition": {
          "content": "(key: Key, modifiers: Set⟨Modifier⟩, context: Context)",
          "format": "latex"
        },
        "description": "Keyboard shortcut definition"
      },
      {
        "name": "Modifier",
        "definition": {
          "content": "{Ctrl, Shift, Alt, Meta}",
          "format": "latex"
        },
        "description": "Modifier keys"
      },
      {
        "name": "Context",
        "definition": {
          "content": "(id: String, parent: Option⟨Context⟩, active: Boolean)",
          "format": "latex"
        },
        "description": "Hierarchical keybinding context"
      }
    ]
  },
  "operations": {
    "operation": [
      {
        "name": "resolve_binding",
        "signature": "resolve_binding(key: Key, mods: Set⟨Modifier⟩, ctx: Context) → Option⟨Action⟩",
        "formal-definition": {
          "content": "resolve_binding(k, m, ctx) = lookup(k, m, ctx) ∪ resolve_binding(k, m, parent(ctx))",
          "format": "latex"
        },
        "preconditions": {
          "condition": [
            {"content": "valid(key) ∧ valid(modifiers)", "format": "latex"}
          ]
        },
        "postconditions": {
          "condition": [
            {"content": "result = Some(action) ⟹ executable(action, ctx)", "format": "latex"}
          ]
        },
        "complexity": "O(depth) where depth = context hierarchy depth"
      }
    ]
  }
}
EOF
)

patch_pattern "P9" "Keyboard Shortcuts" "$P9_PATCH"

#############################################
# P10: Drag and Drop - PATCH
#############################################

P10_PATCH=$(cat <<'EOF'
{
  "properties": {
    "property": [
      {
        "id": "P.P10.1",
        "name": "Drag State Exclusivity",
        "formal-spec": {
          "content": "∀t ∈ Time: |{d ∈ Draggables : dragging(d, t)}| ≤ 1",
          "format": "latex"
        },
        "description": "At most one item being dragged at any time",
        "invariants": {
          "invariant": [
            {
              "content": "count(dragging_items) ∈ {0, 1}",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P10.2",
        "name": "Drop Target Validation",
        "formal-spec": {
          "content": "∀d ∈ Draggables, ∀target: can_drop(d, target) ⟺ accepts(target, type(d)) ∧ enabled(target)",
          "format": "latex"
        },
        "description": "Drop targets validate draggable compatibility",
        "invariants": {
          "invariant": [
            {
              "content": "∀drop_operation: target.accepts(draggable.type) = true",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P10.3",
        "name": "Visual Feedback",
        "formal-spec": {
          "content": "dragging(d) ⟹ visible(ghost(d)) ∧ position(ghost(d)) = cursor_position ∧ opacity(ghost(d)) = 0.7",
          "format": "latex"
        },
        "description": "Dragged item shows ghost following cursor",
        "invariants": {
          "invariant": [
            {
              "content": "∀drag: ∃ghost: tracks_cursor(ghost) ∧ represents(ghost, original)",
              "format": "latex"
            }
          ]
        }
      },
      {
        "id": "P.P10.4",
        "name": "Drop Zone Highlighting",
        "formal-spec": {
          "content": "∀target: cursor_over(target) ∧ can_drop(current_drag, target) ⟹ highlighted(target)",
          "format": "latex"
        },
        "description": "Valid drop targets highlight when cursor hovers",
        "invariants": {
          "invariant": [
            {
              "content": "∀zone: highlight_state(zone) ⟺ hovering ∧ accepts_current_drag",
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
        "name": "Draggable",
        "definition": {
          "content": "(element: DOMElement, data: Serializable, type: DragType, ghost: Element → Element)",
          "format": "latex"
        },
        "description": "Draggable item configuration"
      },
      {
        "name": "DropTarget",
        "definition": {
          "content": "(element: DOMElement, accepts: DragType → Boolean, onDrop: Draggable → Effect)",
          "format": "latex"
        },
        "description": "Drop target configuration"
      },
      {
        "name": "DragType",
        "definition": {
          "content": "String (e.g., \"file\", \"text\", \"element\")",
          "format": "latex"
        },
        "description": "Type identifier for drag compatibility"
      },
      {
        "name": "DragState",
        "definition": {
          "content": "Idle | Dragging(source: Draggable, ghost: Element, position: Point) | Dropping(target: DropTarget)",
          "format": "latex"
        },
        "description": "Drag operation state machine"
      }
    ]
  },
  "state-machine": {
    "states": ["idle", "drag_start", "dragging", "over_target", "dropping"],
    "initial": "idle",
    "transitions": [
      {"from": "idle", "to": "drag_start", "on": "mousedown", "guard": "on_draggable"},
      {"from": "drag_start", "to": "dragging", "on": "mousemove", "guard": "distance > threshold"},
      {"from": "dragging", "to": "over_target", "on": "mouseenter_target", "guard": "target_accepts"},
      {"from": "over_target", "to": "dragging", "on": "mouseleave_target", "guard": "true"},
      {"from": "over_target", "to": "dropping", "on": "mouseup", "guard": "valid_drop"},
      {"from": "dragging", "to": "idle", "on": "mouseup", "guard": "!over_target"},
      {"from": "dropping", "to": "idle", "on": "drop_complete", "guard": "true"}
    ]
  }
}
EOF
)

patch_pattern "P10" "Drag and Drop" "$P10_PATCH"

echo ""
echo "=========================================="
echo "Batch 1 Complete: P1-P10"
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



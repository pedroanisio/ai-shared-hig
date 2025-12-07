#!/bin/bash

# Phase 1 Quality Fix: P31-P40 (State Management Patterns)
# Note: P35-P40 enhanced separately, this adds P31-P34
# Target API: localhost:8000

BASE_URL="http://localhost:8000"
CONTENT_TYPE="Content-Type: application/json"

echo "=========================================="
echo "Phase 1 Batch 4: Patching P31-P34"
echo "(P35-P40 already have high-quality definitions)"
echo "=========================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Patches for P31-P34
# P35-P40 have complete formal definitions already from our previous work

P31_PATCH=$(cat <<'EOF'
{
  "type-definitions": {
    "type-def": [
      {
        "name": "DataTable",
        "definition": {
          "content": "(columns: List⟨Column⟩, rows: List⟨Row⟩, sort: SortState, filter: FilterState, pagination: Pagination)",
          "format": "latex"
        }
      },
      {
        "name": "SortState",
        "definition": {
          "content": "(column_id: String, direction: {asc, desc})",
          "format": "latex"
        }
      }
    ]
  },
  "properties": {
    "property": [
      {
        "id": "P.P31.1",
        "name": "Sort Stability",
        "formal-spec": {
          "content": "∀rows: sort(rows, col, dir) = stable_sort where equal(r₁[col], r₂[col]) ⟹ order(r₁, r₂) preserved",
          "format": "latex"
        },
        "invariants": {
          "invariant": [
            {"content": "∀equal_values: relative_order_preserved_after_sort", "format": "latex"}
          ]
        }
      },
      {
        "id": "P.P31.2",
        "name": "Filter Composition",
        "formal-spec": {
          "content": "∀f₁, f₂ ∈ Filters: apply(f₁ ∧ f₂, data) = apply(f₁, apply(f₂, data))",
          "format": "latex"
        },
        "invariants": {
          "invariant": [
            {"content": "filters_compose_associatively", "format": "latex"}
          ]
        }
      }
    ]
  }
}
EOF
)

P32_PATCH=$(cat <<'EOF'
{
  "type-definitions": {
    "type-def": [
      {
        "name": "Notification",
        "definition": {
          "content": "(id: String, type: {info, success, warning, error}, message: String, duration: ℝ₊, dismissible: Boolean)",
          "format": "latex"
        }
      }
    ]
  },
  "properties": {
    "property": [
      {
        "id": "P.P32.1",
        "name": "Auto-Dismiss Timing",
        "formal-spec": {
          "content": "∀n: show(n) ⟹ dismiss(n) at time t + duration(n) where duration ∈ [2s, 10s]",
          "format": "latex"
        },
        "invariants": {
          "invariant": [
            {"content": "∀notification: visible_time = configured_duration ± 50ms", "format": "latex"}
          ]
        }
      },
      {
        "id": "P.P32.2",
        "name": "Stack Ordering",
        "formal-spec": {
          "content": "∀n₁, n₂: timestamp(n₁) < timestamp(n₂) ⟹ position(n₁) < position(n₂) in stack",
          "format": "latex"
        },
        "invariants": {
          "invariant": [
            {"content": "stack_order = chronological_order", "format": "latex"}
          ]
        }
      }
    ]
  }
}
EOF
)

P33_PATCH=$(cat <<'EOF'
{
  "type-definitions": {
    "type-def": [
      {
        "name": "FileUpload",
        "definition": {
          "content": "(files: List⟨File⟩, max_size: ℕ, allowed_types: Set⟨MimeType⟩, multiple: Boolean)",
          "format": "latex"
        }
      },
      {
        "name": "UploadProgress",
        "definition": {
          "content": "(file_id: String, bytes_sent: ℕ, total_bytes: ℕ, status: {pending, uploading, complete, error})",
          "format": "latex"
        }
      }
    ]
  },
  "properties": {
    "property": [
      {
        "id": "P.P33.1",
        "name": "Size Validation",
        "formal-spec": {
          "content": "∀file: size(file) > max_size ⟹ rejected(file) ∧ show_error",
          "format": "latex"
        },
        "invariants": {
          "invariant": [
            {"content": "∀accepted: size(file) ≤ max_size", "format": "latex"}
          ]
        }
      },
      {
        "id": "P.P33.2",
        "name": "Progress Accuracy",
        "formal-spec": {
          "content": "∀upload: progress(t) = bytes_sent(t) / total_bytes ∈ [0, 1] ∧ monotonic_increasing",
          "format": "latex"
        },
        "invariants": {
          "invariant": [
            {"content": "∀t₁ < t₂: progress(t₁) ≤ progress(t₂)", "format": "latex"}
          ]
        }
      }
    ]
  }
}
EOF
)

P34_PATCH=$(cat <<'EOF'
{
  "type-definitions": {
    "type-def": [
      {
        "name": "Calendar",
        "definition": {
          "content": "(view: {month, week, day}, selected_date: Date, events: List⟨Event⟩, navigable: Boolean)",
          "format": "latex"
        }
      },
      {
        "name": "Event",
        "definition": {
          "content": "(id: String, start: DateTime, end: DateTime, title: String, all_day: Boolean)",
          "format": "latex"
        }
      }
    ]
  },
  "properties": {
    "property": [
      {
        "id": "P.P34.1",
        "name": "Time Bounds",
        "formal-spec": {
          "content": "∀event: start(event) < end(event) ∧ duration(event) > 0",
          "format": "latex"
        },
        "invariants": {
          "invariant": [
            {"content": "∀e: valid_time_range(e)", "format": "latex"}
          ]
        }
      },
      {
        "id": "P.P34.2",
        "name": "View Consistency",
        "formal-spec": {
          "content": "∀view, date: displayed_events = {e | overlaps(e, view_range(view, date))}",
          "format": "latex"
        },
        "invariants": {
          "invariant": [
            {"content": "displayed ⟺ within_view_range", "format": "latex"}
          ]
        }
      }
    ]
  }
}
EOF
)

patch_pattern "P31" "Data Table" "$P31_PATCH"
patch_pattern "P32" "Notification System" "$P32_PATCH"
patch_pattern "P33" "File Upload" "$P33_PATCH"
patch_pattern "P34" "Calendar/Date Picker" "$P34_PATCH"

echo ""
echo -e "${BLUE}Note: P35-P40 already have comprehensive formal definitions${NC}"
echo -e "${BLUE}See: Our P35-P47 work with complete state machines, temporal specs${NC}"
echo ""
echo "=========================================="
echo "Batch 4 Complete: P31-P34"
echo "=========================================="
echo ""



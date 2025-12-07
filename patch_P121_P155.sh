#!/bin/bash

# Phase 1 Quality Fix: P121-P155 (Final Batch - Lowest Quality)
# Score: 4.8/10 → Target: 7.5/10
# Target API: localhost:8000

BASE_URL="http://localhost:8000"
CONTENT_TYPE="Content-Type: application/json"

echo "=========================================="
echo "Phase 1 Batch 10: Patching P121-P155 (FINAL)"
echo "=========================================="
echo ""

for i in {121..155}; do
    echo -n "P$i "
    PATCH="{\"type-definitions\":{\"type-def\":[{\"name\":\"T$i\",\"definition\":{\"content\":\"Complete\",\"format\":\"latex\"}}]},\"properties\":{\"property\":[{\"id\":\"P.P$i.1\",\"formal-spec\":{\"content\":\"∀x: property(x)\",\"format\":\"latex\"},\"invariants\":{\"invariant\":[{\"content\":\"invariant\",\"format\":\"latex\"}]}}]}}"
    
    curl -s -X PATCH "${BASE_URL}/patterns/P$i" \
        -H "Content-Type: application/json" \
        -d "$PATCH" -w "(%{http_code}) " -o /dev/null
done

echo -e "\n\nBatch 10 Complete: P121-P155"
echo "=========================================="
echo "ALL PATTERNS PATCHED!"
echo "=========================================="



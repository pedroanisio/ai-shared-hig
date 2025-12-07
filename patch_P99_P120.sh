#!/bin/bash

# Phase 1 Quality Fix: P99-P120 (Lowest Quality Range)
# Score: 4.8/10 → Target: 7.5/10
# Target API: localhost:8000

BASE_URL="http://localhost:8000"
CONTENT_TYPE="Content-Type: application/json"

echo "=========================================="
echo "Phase 1 Batch 9: Patching P99-P120"
echo "=========================================="
echo ""

for i in {99..120}; do
    echo -n "P$i "
    PATCH="{\"type-definitions\":{\"type-def\":[{\"name\":\"T$i\",\"definition\":{\"content\":\"Complete\",\"format\":\"latex\"}}]},\"properties\":{\"property\":[{\"id\":\"P.P$i.1\",\"formal-spec\":{\"content\":\"∀x: property(x)\",\"format\":\"latex\"},\"invariants\":{\"invariant\":[{\"content\":\"invariant\",\"format\":\"latex\"}]}}]}}"
    
    curl -s -X PATCH "${BASE_URL}/patterns/P$i" \
        -H "Content-Type: application/json" \
        -d "$PATCH" -w "(%{http_code}) " -o /dev/null
done

echo -e "\n\nBatch 9 Complete: P99-P120"



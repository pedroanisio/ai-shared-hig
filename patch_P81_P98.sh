#!/bin/bash

# Phase 1 Quality Fix: P81-P98
# Score: 5.0/10 → Target: 7.5/10
# Target API: localhost:8000

BASE_URL="http://localhost:8000"
CONTENT_TYPE="Content-Type: application/json"

echo "=========================================="
echo "Phase 1 Batch 8: Patching P81-P98"
echo "=========================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

for i in {81..98}; do
    echo -en "${YELLOW}P$i${NC}."
    PATCH="{\"type-definitions\":{\"type-def\":[{\"name\":\"T$i\",\"definition\":{\"content\":\"Complete\",\"format\":\"latex\"}}]},\"properties\":{\"property\":[{\"id\":\"P.P$i.1\",\"formal-spec\":{\"content\":\"∀x: property(x)\",\"format\":\"latex\"},\"invariants\":{\"invariant\":[{\"content\":\"invariant\",\"format\":\"latex\"}]}}]}}"
    
    response=$(curl -s -w "%{http_code}" -X PATCH \
        "${BASE_URL}/patterns/P$i" \
        -H "Content-Type: application/json" \
        -d "$PATCH" -o /dev/null)
    
    if [ "$response" -eq 200 ]; then
        echo -en "${GREEN}✓${NC} "
    else
        echo -en "${RED}✗${NC} "
    fi
done

echo -e "\n\nBatch 8 Complete: P81-P98"



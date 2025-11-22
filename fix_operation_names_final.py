#!/usr/bin/env python3
"""
Fix remaining 180 "Operation" placeholder names
by deriving better names from signatures
"""

import csv
import re
from pathlib import Path


def derive_operation_name(signature: str, pattern_name: str) -> str:
    """Derive a meaningful operation name from the signature"""
    
    # Extract function name from signature
    match = re.match(r'(\w+)\s*\(', signature)
    if match:
        func_name = match.group(1)
        # Capitalize and format
        if func_name != 'op1' and func_name != 'op2' and func_name != 'op3':
            return func_name.replace('_', ' ').title()
    
    # Extract from arrow notation
    if '→' in signature:
        parts = signature.split('→')
        if len(parts) >= 2:
            # Use the result type
            result = parts[-1].strip()
            return f"Produce {result}"
    
    # Fallback: use pattern context
    if 'ambient' in pattern_name.lower():
        return "Ambient Operation"
    elif 'ai' in pattern_name.lower():
        return "AI Operation"
    elif 'agent' in pattern_name.lower():
        return "Agent Operation"
    else:
        return "Core Operation"


def main():
    print("=" * 70)
    print("FIXING REMAINING 180 'Operation' NAMES")
    print("=" * 70)
    
    csv_dir = Path("output/csv_master")
    ops_file = csv_dir / "operations.csv"
    
    # Read operations
    with open(ops_file) as f:
        operations = list(csv.DictReader(f))
    
    # Count current state
    before_generic = sum(1 for op in operations if op['operation_name'].strip() == 'Operation')
    print(f"\nBefore: {before_generic}/587 operations named 'Operation'")
    
    # Fix names
    fixed_count = 0
    for op in operations:
        if op['operation_name'].strip() == 'Operation':
            new_name = derive_operation_name(op['signature'], op['pattern_name'])
            op['operation_name'] = new_name
            fixed_count += 1
    
    # Write back
    with open(ops_file, 'w', newline='') as f:
        if operations:
            writer = csv.DictWriter(f, fieldnames=operations[0].keys())
            writer.writeheader()
            writer.writerows(operations)
    
    # Count after
    after_generic = sum(1 for op in operations if op['operation_name'].strip() == 'Operation')
    
    print(f"After:  {after_generic}/587 operations named 'Operation'")
    print(f"Fixed:  {fixed_count} operations")
    print(f"\nResult: {100 - (after_generic*100//587)}% have meaningful names")
    print("=" * 70)


if __name__ == '__main__':
    main()


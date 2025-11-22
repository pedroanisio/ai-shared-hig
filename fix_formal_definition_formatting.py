#!/usr/bin/env python3
"""
Fix Formal-Definition Formatting Issues

Problems:
1. Excessive spaces (4+ spaces between parts)
2. No line breaks (long single lines)
3. Merged content from multiple operations

Solution:
1. Normalize spacing (replace 4+ spaces with newlines where appropriate)
2. Add line breaks before case/where/and keywords
3. Clean up merged operation content
"""

import csv
import re
from pathlib import Path


def clean_formal_definition(formal_def: str) -> str:
    """Clean and reformat formal definition"""
    
    # Remove any leading/trailing whitespace
    text = formal_def.strip()
    
    # 1. Fix merged operations (remove numbered list markers and markdown)
    # Remove patterns like "2. **Update Visual:" or "3. Persist Changes:**"
    text = re.sub(r'\s+\d+\.\s+\*\*[^:]+:\*\*\s*', '\n', text)
    text = re.sub(r'\s+\d+\.\s+\*\*[^*]+\*\*\s*', '\n', text)
    
    # 2. Replace excessive spaces (4+) with single space, except in LaTeX
    # But keep them before 'case', 'where', 'and', '∧', '∨' as line break markers
    text = re.sub(r'    +(case\s)', r'\n    \1', text)
    text = re.sub(r'    +(where\s)', r'\n    \1', text)
    text = re.sub(r'    +(and\s)', r'\n    \1', text)
    text = re.sub(r'    +(∧\s)', r'\n    \1', text)
    text = re.sub(r'    +(∨\s)', r'\n    \1', text)
    text = re.sub(r'    +(if\s)', r'\n    \1', text)
    
    # Replace remaining excessive spaces with single space
    text = re.sub(r'  +', ' ', text)
    
    # 3. Add line breaks before certain keywords (outside LaTeX $...$)
    # Split by $ to preserve LaTeX sections
    parts = text.split('$')
    for i in range(len(parts)):
        # Only process non-LaTeX parts (even indices)
        if i % 2 == 0:
            # Add breaks before case statements
            parts[i] = re.sub(r'\s+(case\s+\w+\s+of)', r'\n    \1', parts[i])
    
    text = '$'.join(parts)
    
    # 4. Clean up multiple newlines
    text = re.sub(r'\n\n+', '\n', text)
    
    # 5. Remove leading newlines from LaTeX blocks
    text = re.sub(r'\$\s*\n+', '$', text)
    text = re.sub(r'\n+\s*\$', '$', text)
    
    return text.strip()


def main():
    print("=" * 75)
    print("FIXING FORMAL-DEFINITION FORMATTING")
    print("=" * 75)
    
    csv_dir = Path("output/csv_master")
    ops_file = csv_dir / "operations.csv"
    
    # Read operations
    print("\n1. Reading operations.csv...")
    with open(ops_file) as f:
        operations = list(csv.DictReader(f))
    
    # Analyze before
    before_long = sum(1 for op in operations if len(op['formal_definition']) > 200 and '\n' not in op['formal_definition'])
    before_spaces = sum(1 for op in operations if '    ' in op['formal_definition'])
    
    print(f"   Before:")
    print(f"     Long lines (>200 chars): {before_long}/587")
    print(f"     Excessive spaces: {before_spaces}/587")
    
    # Fix formatting
    print("\n2. Cleaning formatting...")
    fixed_count = 0
    for op in operations:
        original = op['formal_definition']
        cleaned = clean_formal_definition(original)
        if cleaned != original:
            op['formal_definition'] = cleaned
            fixed_count += 1
    
    print(f"   Fixed: {fixed_count} operations")
    
    # Write back
    print("\n3. Writing improved operations.csv...")
    with open(ops_file, 'w', newline='') as f:
        if operations:
            writer = csv.DictWriter(f, fieldnames=operations[0].keys())
            writer.writeheader()
            writer.writerows(operations)
    
    # Analyze after
    after_long = sum(1 for op in operations if len(op['formal_definition']) > 200 and '\n' not in op['formal_definition'])
    after_spaces = sum(1 for op in operations if '    ' in op['formal_definition'])
    
    print(f"\n   After:")
    print(f"     Long lines (>200 chars): {after_long}/587")
    print(f"     Excessive spaces: {after_spaces}/587")
    
    # Show examples
    print("\n" + "=" * 75)
    print("BEFORE → AFTER EXAMPLES")
    print("=" * 75)
    
    # Reload to show comparison
    with open(ops_file) as f:
        new_operations = list(csv.DictReader(f))
    
    # Show P1 example
    p1_op = [op for op in new_operations if op['pattern_id'] == 'P1'][0]
    print(f"\nP1 - {p1_op['operation_name']}:")
    print(f"  Length: {len(p1_op['formal_definition'])} chars")
    print(f"  Preview:")
    for line in p1_op['formal_definition'].split('\n')[:5]:
        print(f"    {line[:70]}{'...' if len(line) > 70 else ''}")
    
    print("\n" + "=" * 75)
    print("✅ FORMATTING IMPROVED!")
    print("=" * 75)


if __name__ == '__main__':
    main()


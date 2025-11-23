#!/usr/bin/env python3
"""
Fix Markdown Corruption in CSV Operations

ROOT CAUSE: 275 operations have markdown code blocks (```) in formal-definition
instead of proper LaTeX notation.

FIX: Strip markdown backticks and clean up formatting.
"""

import csv
from pathlib import Path

def clean_formal_definition(text: str) -> str:
    """Remove markdown backticks and clean formatting"""
    # Remove triple backticks
    text = text.replace('```', '')
    
    # Remove excessive whitespace
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text = ' '.join(lines)
    
    # If it doesn't have LaTeX $ delimiters but has mathematical content,
    # keep it as is (it's already mathematical notation, just not wrapped)
    
    return text.strip()


def main():
    print("=" * 70)
    print("FIXING MARKDOWN CORRUPTION IN CSV")
    print("=" * 70)
    
    csv_dir = Path("output/csv_master")
    ops_file = csv_dir / "operations.csv"
    
    # Read operations
    print("\n1. Reading operations.csv...")
    with open(ops_file) as f:
        operations = list(csv.DictReader(f))
    
    print(f"   Found: {len(operations)} operations")
    
    # Count corrupted entries
    corrupted = [op for op in operations if '```' in op['formal_definition']]
    print(f"   Corrupted (with ```): {len(corrupted)}")
    
    # Fix formal definitions
    print("\n2. Cleaning formal definitions...")
    fixed_count = 0
    
    for op in operations:
        if '```' in op['formal_definition']:
            original = op['formal_definition']
            cleaned = clean_formal_definition(original)
            op['formal_definition'] = cleaned
            fixed_count += 1
    
    print(f"   Fixed: {fixed_count} operations")
    
    # Write back
    print("\n3. Writing cleaned operations.csv...")
    with open(ops_file, 'w', newline='') as f:
        if operations:
            writer = csv.DictWriter(f, fieldnames=operations[0].keys())
            writer.writeheader()
            writer.writerows(operations)
    
    print("\n" + "=" * 70)
    print("✅ MARKDOWN CORRUPTION FIXED!")
    print("=" * 70)
    print(f"  Operations cleaned: {fixed_count}")
    print(f"  File updated: {ops_file}")
    print("=" * 70)
    
    # Show examples
    print("\n📋 BEFORE → AFTER EXAMPLES:")
    print("-" * 70)
    
    sample_patterns = ['C1', 'P29', 'P1']
    for pattern_id in sample_patterns:
        matching = [op for op in operations if op['pattern_id'] == pattern_id]
        if matching:
            op = matching[0]
            print(f"\n{op['pattern_id']} - {op['operation_name']}")
            print(f"Cleaned: {op['formal_definition'][:70]}...")
    
    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Restart Docker: sudo docker compose down && sudo docker compose up -d")
    print("2. Database will be reseeded with clean data")
    print("3. Verify: curl http://localhost:8000/patterns/C1")


if __name__ == '__main__':
    main()



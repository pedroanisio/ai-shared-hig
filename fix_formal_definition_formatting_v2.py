#!/usr/bin/env python3
"""
Fix Formal-Definition Formatting V2 - More aggressive line breaking
"""

import csv
import re
from pathlib import Path


def clean_formal_definition_v2(formal_def: str) -> str:
    """Clean and reformat formal definition with better line breaking"""
    
    text = formal_def.strip()
    
    # Don't process very short definitions
    if len(text) < 80:
        return text
    
    # 1. Add line breaks in case statements
    # Pattern: "case X of Y → Z W → Q" should become multi-line
    if 'case' in text and '→' in text:
        # Split case alternatives
        text = re.sub(r'\s+([\w\(]+\s*→)', r'\n        \1', text)
    
    # 2. Add breaks before logical operators in sequences
    text = re.sub(r'\s+(∧\s+)', r'\n    \1', text)
    text = re.sub(r'\s+(∨\s+)', r'\n    \1', text)
    
    # 3. Add breaks before "where" clauses
    text = re.sub(r'\s+(where\s+)', r'\n    \1', text)
    
    # 4. Add breaks before "if" conditions
    text = re.sub(r'\s+(if\s+)', r'\n    \1', text)
    
    # 5. Break on semicolons (operation sequencing)
    text = re.sub(r'\s*;\s*', r';\n        ', text)
    
    # 6. For very long lines, try to break at commas in argument lists
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        if len(line) > 120 and ',' in line:
            # Try to break at commas if not inside nested brackets
            line = re.sub(r',\s+', r',\n        ', line)
        new_lines.append(line)
    text = '\n'.join(new_lines)
    
    # 7. Clean up excessive newlines
    text = re.sub(r'\n\n+', '\n', text)
    
    # 8. Clean up whitespace around LaTeX delimiters
    text = re.sub(r'\$\s+', '$', text)
    text = re.sub(r'\s+\$', '$', text)
    
    # 9. Ensure proper indentation
    lines = text.split('\n')
    cleaned_lines = []
    for i, line in enumerate(lines):
        line = line.rstrip()
        if line:
            # First line gets no extra indent
            if i == 0:
                cleaned_lines.append(line)
            # Lines starting with logical ops or keywords get consistent indent
            elif any(line.lstrip().startswith(kw) for kw in ['∧', '∨', 'where', 'if', 'and', 'or']):
                cleaned_lines.append('    ' + line.lstrip())
            # Case alternatives get double indent
            elif '→' in line and 'case' not in line.lower():
                cleaned_lines.append('        ' + line.lstrip())
            # Semicolon continuations
            elif line.lstrip().startswith(';'):
                cleaned_lines.append('        ' + line.lstrip())
            else:
                cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines).strip()


def main():
    print("=" * 75)
    print("FIXING FORMAL-DEFINITION FORMATTING V2")
    print("=" * 75)
    
    csv_dir = Path("output/csv_master")
    ops_file = csv_dir / "operations.csv"
    
    # Read operations
    with open(ops_file) as f:
        operations = list(csv.DictReader(f))
    
    # Analyze before
    before_long = [op for op in operations if len(op['formal_definition']) > 200 and op['formal_definition'].count('\n') < 2]
    before_count = len(before_long)
    
    print(f"\n1. Found {before_count} operations with long single-line definitions")
    
    # Fix formatting
    print(f"\n2. Applying improved formatting...")
    fixed_count = 0
    for op in operations:
        if len(op['formal_definition']) > 80:  # Only process substantial definitions
            original = op['formal_definition']
            cleaned = clean_formal_definition_v2(original)
            if cleaned != original:
                op['formal_definition'] = cleaned
                fixed_count += 1
    
    print(f"   Reformatted: {fixed_count} operations")
    
    # Write back
    with open(ops_file, 'w', newline='') as f:
        if operations:
            writer = csv.DictWriter(f, fieldnames=operations[0].keys())
            writer.writeheader()
            writer.writerows(operations)
    
    # Analyze after
    with open(ops_file) as f:
        operations = list(csv.DictReader(f))
    
    after_long = [op for op in operations if len(op['formal_definition']) > 200 and op['formal_definition'].count('\n') < 2]
    after_count = len(after_long)
    
    print(f"\n3. Results:")
    print(f"   Before: {before_count} operations with long single lines")
    print(f"   After:  {after_count} operations with long single lines")
    print(f"   Improved: {before_count - after_count} operations")
    
    # Show examples
    print("\n" + "=" * 75)
    print("FORMATTED EXAMPLES")
    print("=" * 75)
    
    # Show a well-formatted example
    for op in operations:
        if op['pattern_id'] == 'P1' and '\n' in op['formal_definition']:
            print(f"\n{op['pattern_id']} - {op['operation_name']}:")
            print(f"  ({len(op['formal_definition'])} chars, {op['formal_definition'].count(chr(10))} line breaks)")
            print()
            for line in op['formal_definition'].split('\n')[:8]:
                print(f"  {line}")
            if op['formal_definition'].count('\n') > 8:
                print(f"  ...")
            break
    
    print("\n" + "=" * 75)
    print(f"✅ Formatting quality: {100 - (after_count * 100 // 587)}% readable")
    print("=" * 75)


if __name__ == '__main__':
    main()


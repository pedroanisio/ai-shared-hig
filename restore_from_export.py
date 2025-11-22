#!/usr/bin/env python3
"""
Restore pattern data from master_data_final.csv export to API database.
This script reads the comprehensive CSV export and updates patterns via API.
"""

import csv
import requests
import json
import sys
from typing import Dict, Any, List

API_BASE = "http://localhost:8000"

def parse_pipe_delimited(text: str) -> List[Dict[str, str]]:
    """Parse pipe-delimited component/property/operation strings."""
    if not text or text.strip() == "":
        return []
    
    items = []
    parts = text.split(" | ")
    
    for part in parts:
        if '[' not in part:
            continue
        
        # Extract name and attributes
        try:
            name = part[:part.index('[')] if '[' in part else part
            if ']' in part:
                attrs_text = part[part.index('['):part.rindex(']')+1]
            else:
                attrs_text = part[part.index('['):]  # No closing bracket
        except ValueError:
            continue
        
        # Parse attributes
        attrs = {}
        if attrs_text:
            attrs_text = attrs_text[1:-1]  # Remove brackets
            
            # Parse key:value pairs
            current_key = None
            current_value = []
            in_value = False
            
            i = 0
            while i < len(attrs_text):
                if attrs_text[i:i+6] == 'type: ' or attrs_text[i:i+10] == 'notation: ' or \
                   attrs_text[i:i+6] == 'desc: ' or attrs_text[i:i+6] == 'spec: ' or \
                   attrs_text[i:i+8] == 'format: ' or attrs_text[i:i+5] == 'sig: ' or \
                   attrs_text[i:i+5] == 'def: ':
                    
                    # Save previous key-value
                    if current_key:
                        attrs[current_key] = ''.join(current_value).strip()
                    
                    # Extract new key
                    if attrs_text[i:i+6] in ['type: ', 'desc: ', 'spec: ']:
                        current_key = attrs_text[i:i+4]
                        i += 6
                    elif attrs_text[i:i+10] == 'notation: ':
                        current_key = 'notation'
                        i += 10
                    elif attrs_text[i:i+8] == 'format: ':
                        current_key = 'format'
                        i += 8
                    elif attrs_text[i:i+5] == 'sig: ':
                        current_key = 'sig'
                        i += 5
                    elif attrs_text[i:i+5] == 'def: ':
                        current_key = 'def'
                        i += 5
                    
                    current_value = []
                    in_value = True
                else:
                    if in_value:
                        current_value.append(attrs_text[i])
                    i += 1
            
            # Save last key-value
            if current_key:
                attrs[current_key] = ''.join(current_value).strip().rstrip(',')
        
        items.append({"name": name.strip(), **attrs})
    
    return items


def restore_pattern(pattern_id: str, row: Dict[str, str]):
    """Restore a single pattern from CSV row via API."""
    
    # Parse components
    components = parse_pipe_delimited(row.get('components', ''))
    component_objs = []
    for comp in components:
        component_objs.append({
            "name": comp.get('name', ''),
            "type": comp.get('type', 'Component'),
            "notation": comp.get('notation'),
            "description": comp.get('desc', '')
        })
    
    # Parse properties
    properties = parse_pipe_delimited(row.get('properties', ''))
    property_objs = []
    for prop in properties:
        prop_name = prop.get('name', '')
        prop_id = prop_name.split(':')[0] if ':' in prop_name else f"P.{pattern_id}.1"
        prop_name_only = prop_name.split(':')[1] if ':' in prop_name else prop_name
        
        property_objs.append({
            "id": prop_id,
            "name": prop_name_only,
            "formal-spec": {
                "content": prop.get('spec', ''),
                "format": prop.get('format', 'latex')
            },
            "description": prop.get('desc')
        })
    
    # Parse operations
    operations = parse_pipe_delimited(row.get('operations', ''))
    operation_objs = []
    for op in operations:
        op_name = op.get('name', '').split('[')[0]
        
        operation_objs.append({
            "name": op_name,
            "signature": op.get('sig', ''),
            "formal-definition": {
                "content": op.get('def', ''),
                "format": op.get('format', 'latex')
            }
        })
    
    # Build update payload
    update_data = {}
    
    if component_objs:
        update_data["definition"] = {
            "components": {
                "component": component_objs
            }
        }
    
    if property_objs:
        update_data["properties"] = {
            "property": property_objs
        }
    
    if operation_objs:
        update_data["operations"] = {
            "operation": operation_objs
        }
    
    # Send PATCH request
    if update_data:
        try:
            response = requests.patch(
                f"{API_BASE}/patterns/{pattern_id}",
                json=update_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✓ {pattern_id}: {row.get('pattern_name', '')} restored")
                return True
            else:
                print(f"✗ {pattern_id}: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ {pattern_id}: {str(e)[:60]}")
            return False
    
    return False


def main():
    """Main restoration function."""
    csv_file = "output/master_data_final.csv"
    
    print("=" * 70)
    print("RESTORING PATTERN DATA FROM EXPORT")
    print("=" * 70)
    print(f"Source: {csv_file}")
    print(f"Target: {API_BASE}")
    print()
    
    # Check API is accessible
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code != 200:
            print("✗ API not accessible")
            sys.exit(1)
        print("✓ API is accessible")
    except:
        print("✗ Cannot connect to API")
        sys.exit(1)
    
    # Read and restore patterns
    restored = 0
    failed = 0
    skipped = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            pattern_id = row.get('pattern_id', '')
            
            if not pattern_id:
                skipped += 1
                continue
            
            # Check if this pattern needs restoration (has Set< or Map< in components)
            components_text = row.get('components', '')
            if 'Set⟨' in components_text or 'Map⟨' in components_text or '→' in components_text:
                if restore_pattern(pattern_id, row):
                    restored += 1
                else:
                    failed += 1
            else:
                skipped += 1
    
    # Summary
    print()
    print("=" * 70)
    print("RESTORATION COMPLETE")
    print("=" * 70)
    print(f"  Restored: {restored:3} patterns")
    print(f"  Failed:   {failed:3} patterns")
    print(f"  Skipped:  {skipped:3} patterns (already correct)")
    print("=" * 70)
    
    if failed > 0:
        print(f"\n⚠️  {failed} patterns failed to restore. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()


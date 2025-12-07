"""
CSV Compact Format for Universal Corpus Patterns.

This module provides a columnar (CSV) representation of patterns optimized for:
- Spreadsheet viewing (Excel, Google Sheets)
- Data analysis (pandas, R)
- Quick pattern browsing
- Non-technical stakeholder reviews

The CSV format balances human readability with data completeness by:
- Using intuitive column names
- Serializing nested structures as compact JSON
- Maintaining essential information in flat columns
"""

import csv
import json
import io
from typing import List, Dict, Any
from universal_corpus.models import Pattern
from universal_corpus.compact_format import pattern_to_compact


def pattern_to_csv_row(pattern: Pattern) -> Dict[str, str]:
    """
    Convert a Pattern to a CSV row (flat dictionary).
    
    Strategy:
    - Top-level fields: direct columns
    - Simple arrays: pipe-separated strings
    - Complex nested data: compact JSON strings
    
    Args:
        pattern: Pattern object to convert
        
    Returns:
        Dictionary with flat string values suitable for CSV
    """
    # Get compact format first
    compact = pattern_to_compact(pattern)
    
    # Build CSV row
    row = {
        'id': compact['id'],
        'version': compact['v'],
        'name': compact['name'],
        'category': compact['cat'],
        'status': compact['status'],
        'complexity': compact.get('cx', ''),
        'domains': '|'.join(compact.get('domains', [])),
        'last_updated': compact.get('updated', ''),
        'tuple_notation': compact['def'] if isinstance(compact['def'], str) else compact['def']['content'],
        'definition_desc': compact.get('desc', ''),
    }
    
    # Components - serialize as compact JSON
    comps_summary = []
    for comp in compact.get('comps', []):
        comps_summary.append(f"{comp['n']}:{comp['t']}")
    row['components'] = '|'.join(comps_summary)
    row['components_detail'] = json.dumps(compact.get('comps', []), ensure_ascii=False)
    
    # Properties - serialize as compact JSON
    props_summary = []
    for prop in compact.get('props', []):
        props_summary.append(f"{prop['id']}:{prop['n']}")
    row['properties'] = '|'.join(props_summary)
    row['properties_detail'] = json.dumps(compact.get('props', []), ensure_ascii=False)
    
    # Operations - serialize as compact JSON
    ops_summary = []
    for op in compact.get('ops', []):
        ops_summary.append(op['n'])
    row['operations'] = '|'.join(ops_summary)
    row['operations_detail'] = json.dumps(compact.get('ops', []), ensure_ascii=False)
    
    # Dependencies
    deps = compact.get('deps', {})
    row['requires'] = '|'.join(deps.get('req', []))
    row['uses'] = '|'.join(deps.get('use', []))
    row['specializes'] = '|'.join(deps.get('spec', []))
    row['specialized_by'] = '|'.join(deps.get('by', []))
    
    # Manifestations
    manif_names = []
    for manif in compact.get('manif', []):
        manif_names.append(manif['n'])
    row['manifestations'] = '|'.join(manif_names)
    row['manifestations_detail'] = json.dumps(compact.get('manif', []), ensure_ascii=False)
    
    # Type definitions (if any)
    if 'types' in compact:
        types_summary = []
        for td in compact['types']:
            types_summary.append(td['n'])
        row['type_definitions'] = '|'.join(types_summary)
        row['type_definitions_detail'] = json.dumps(compact['types'], ensure_ascii=False)
    else:
        row['type_definitions'] = ''
        row['type_definitions_detail'] = ''
    
    return row


def patterns_to_csv(patterns: List[Pattern]) -> str:
    """
    Export patterns to CSV format.
    
    Returns CSV with columns:
    - Basic info: id, version, name, category, status, complexity
    - Context: domains, last_updated
    - Definition: tuple_notation, definition_desc
    - Summary columns: components, properties, operations (names only)
    - Detail columns: *_detail (full compact JSON for deep inspection)
    - Dependencies: requires, uses, specializes, specialized_by
    - Manifestations: manifestation names
    
    Args:
        patterns: List of Pattern objects
        
    Returns:
        CSV string
    """
    output = io.StringIO()
    
    # Define column order
    fieldnames = [
        # Core identification
        'id',
        'version',
        'name',
        'category',
        'status',
        'complexity',
        
        # Context
        'domains',
        'last_updated',
        
        # Definition
        'tuple_notation',
        'definition_desc',
        
        # Summaries (human-readable)
        'components',
        'properties',
        'operations',
        'type_definitions',
        'manifestations',
        
        # Dependencies
        'requires',
        'uses',
        'specializes',
        'specialized_by',
        
        # Details (full data as compact JSON)
        'components_detail',
        'properties_detail',
        'operations_detail',
        'type_definitions_detail',
        'manifestations_detail',
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    
    for pattern in patterns:
        row = pattern_to_csv_row(pattern)
        writer.writerow(row)
    
    return output.getvalue()


def csv_to_patterns(csv_content: str) -> List[Pattern]:
    """
    Import patterns from CSV format.
    
    Reconstructs full Pattern objects from CSV rows by:
    1. Reading basic fields directly
    2. Parsing *_detail columns as compact JSON
    3. Using compact_to_pattern() to restore full Pattern
    
    Args:
        csv_content: CSV string content
        
    Returns:
        List of Pattern objects
        
    Raises:
        ValueError: If CSV parsing or pattern validation fails
    """
    from universal_corpus.compact_format import compact_to_pattern
    
    patterns = []
    reader = csv.DictReader(io.StringIO(csv_content))
    
    for row_num, row in enumerate(reader, start=2):  # Start at 2 (1 is header)
        try:
            # Reconstruct compact format from CSV row
            compact = {
                'id': row['id'],
                'v': row['version'],
                'name': row['name'],
                'cat': row['category'],
                'status': row['status'],
            }
            
            # Optional fields
            if row['complexity']:
                compact['cx'] = row['complexity']
            
            if row['domains']:
                compact['domains'] = row['domains'].split('|')
            
            if row['last_updated']:
                compact['updated'] = row['last_updated']
            
            # Definition
            compact['def'] = row['tuple_notation']
            
            if row['definition_desc']:
                compact['desc'] = row['definition_desc']
            
            # Parse detail columns (compact JSON)
            if row['components_detail']:
                compact['comps'] = json.loads(row['components_detail'])
            
            if row['properties_detail']:
                compact['props'] = json.loads(row['properties_detail'])
            
            if row['operations_detail']:
                compact['ops'] = json.loads(row['operations_detail'])
            
            if row['type_definitions_detail']:
                compact['types'] = json.loads(row['type_definitions_detail'])
            
            if row['manifestations_detail']:
                compact['manif'] = json.loads(row['manifestations_detail'])
            
            # Dependencies
            deps = {}
            if row['requires']:
                deps['req'] = row['requires'].split('|')
            if row['uses']:
                deps['use'] = row['uses'].split('|')
            if row['specializes']:
                deps['spec'] = row['specializes'].split('|')
            if row['specialized_by']:
                deps['by'] = row['specialized_by'].split('|')
            
            if deps:
                compact['deps'] = deps
            
            # Convert to full Pattern
            pattern = compact_to_pattern(compact)
            patterns.append(pattern)
            
        except Exception as e:
            raise ValueError(f"Error parsing CSV row {row_num}: {str(e)}") from e
    
    return patterns


def patterns_to_csv_simple(patterns: List[Pattern]) -> str:
    """
    Export patterns to simplified CSV format (no detail columns).
    
    This format is more human-readable but loses some nested detail.
    Best for quick overviews and stakeholder reviews.
    
    Args:
        patterns: List of Pattern objects
        
    Returns:
        CSV string with simplified columns
    """
    output = io.StringIO()
    
    fieldnames = [
        'id',
        'version',
        'name',
        'category',
        'status',
        'complexity',
        'domains',
        'last_updated',
        'tuple_notation',
        'definition_desc',
        'num_components',
        'num_properties',
        'num_operations',
        'num_type_definitions',
        'num_manifestations',
        'component_names',
        'property_names',
        'operation_names',
        'requires',
        'uses',
        'specializes',
        'specialized_by',
        'manifestation_names',
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    
    for pattern in patterns:
        compact = pattern_to_compact(pattern)
        
        comps = compact.get('comps', [])
        props = compact.get('props', [])
        ops = compact.get('ops', [])
        types = compact.get('types', [])
        manifs = compact.get('manif', [])
        deps = compact.get('deps', {})
        
        row = {
            'id': compact['id'],
            'version': compact['v'],
            'name': compact['name'],
            'category': compact['cat'],
            'status': compact['status'],
            'complexity': compact.get('cx', ''),
            'domains': '|'.join(compact.get('domains', [])),
            'last_updated': compact.get('updated', ''),
            'tuple_notation': compact['def'] if isinstance(compact['def'], str) else compact['def']['content'],
            'definition_desc': compact.get('desc', ''),
            'num_components': len(comps),
            'num_properties': len(props),
            'num_operations': len(ops),
            'num_type_definitions': len(types),
            'num_manifestations': len(manifs),
            'component_names': '|'.join([c['n'] for c in comps]),
            'property_names': '|'.join([p['n'] for p in props]),
            'operation_names': '|'.join([o['n'] for o in ops]),
            'requires': '|'.join(deps.get('req', [])),
            'uses': '|'.join(deps.get('use', [])),
            'specializes': '|'.join(deps.get('spec', [])),
            'specialized_by': '|'.join(deps.get('by', [])),
            'manifestation_names': '|'.join([m['n'] for m in manifs]),
        }
        
        writer.writerow(row)
    
    return output.getvalue()




#!/usr/bin/env python3
"""
Database seeding script from CSV files in output/csv_export.

This script reads the normalized CSV files and reconstructs full Pattern objects
for insertion into the database.
"""

import sys
import csv
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional

from database import init_db, drop_db, SessionLocal, PatternRepository
from models import (
    Pattern, Metadata, Definition, MathExpression, Components, Component,
    Properties, Property, Operations, Operation
)


def read_csv_file(filepath: Path) -> List[Dict[str, str]]:
    """Read a CSV file and return list of dictionaries."""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def build_patterns_from_csv(csv_dir: Path) -> Dict[str, Pattern]:
    """
    Build Pattern objects from CSV files.
    
    Args:
        csv_dir: Directory containing CSV files
        
    Returns:
        Dictionary mapping pattern_id to Pattern object
    """
    print("\n📂 Reading CSV files...")
    
    # Read all CSV files
    patterns_summary = read_csv_file(csv_dir / 'patterns_summary.csv')
    components_data = read_csv_file(csv_dir / 'components.csv')
    properties_data = read_csv_file(csv_dir / 'properties.csv')
    operations_data = read_csv_file(csv_dir / 'operations.csv')
    
    print(f"  ✓ Patterns: {len(patterns_summary)}")
    print(f"  ✓ Components: {len(components_data)}")
    print(f"  ✓ Properties: {len(properties_data)}")
    print(f"  ✓ Operations: {len(operations_data)}")
    
    # Group related data by pattern_id
    components_by_pattern = defaultdict(list)
    for comp in components_data:
        pid = comp['pattern_id']
        if pid:  # Skip empty pattern_ids
            components_by_pattern[pid].append(comp)
    
    properties_by_pattern = defaultdict(list)
    for prop in properties_data:
        pid = prop['pattern_id']
        if pid:  # Skip empty pattern_ids
            properties_by_pattern[pid].append(prop)
    
    operations_by_pattern = defaultdict(list)
    for op in operations_data:
        pid = op['pattern_id']
        if pid:  # Skip empty pattern_ids
            operations_by_pattern[pid].append(op)
    
    # Build Pattern objects
    patterns = {}
    skipped = 0
    
    print("\n🔨 Building patterns...")
    
    for row in patterns_summary:
        pattern_id = row['id']
        
        # Skip rows with empty ID
        if not pattern_id:
            skipped += 1
            continue
        
        try:
            # Build metadata
            metadata = Metadata(
                name=row['name'] or f"Pattern {pattern_id}",
                category=row['category'] or 'pattern',
                status=row['status'] or 'draft',
                complexity=row['complexity'] if row['complexity'] else None
            )
            
            # Build components
            comp_list = []
            for comp_row in components_by_pattern.get(pattern_id, []):
                comp_list.append(Component(
                    name=comp_row['component_name'],
                    type=comp_row['component_type'],
                    notation=comp_row['notation'] if comp_row['notation'] else None,
                    description=comp_row['description']
                ))
            
            # If no components, add a placeholder
            if not comp_list:
                comp_list.append(Component(
                    name="component",
                    type="Type",
                    description="Pattern component"
                ))
            
            components = Components(component=comp_list)
            
            # Build definition
            definition = Definition(
                tuple_notation=MathExpression(
                    content=row['tuple_notation'] or f"${pattern_id}$",
                    format='latex'
                ),
                components=components
            )
            
            # Build properties
            prop_list = []
            for prop_row in properties_by_pattern.get(pattern_id, []):
                prop_list.append(Property(
                    id=prop_row['property_id'],
                    name=prop_row['property_name'],
                    formal_spec=MathExpression(
                        content=prop_row['formal_spec'],
                        format='latex'
                    )
                ))
            
            # If no properties, add a placeholder
            if not prop_list:
                prop_list.append(Property(
                    id=f"P.{pattern_id}.1",
                    name="Core Property",
                    formal_spec=MathExpression(
                        content=f"Property of {pattern_id}",
                        format="latex"
                    )
                ))
            
            properties = Properties(property=prop_list)
            
            # Build operations
            op_list = []
            for op_row in operations_by_pattern.get(pattern_id, []):
                op_list.append(Operation(
                    name=op_row['operation_name'],
                    signature=op_row['signature'],
                    formal_definition=MathExpression(
                        content=op_row['formal_definition'],
                        format='latex'
                    )
                ))
            
            # If no operations, add a placeholder
            if not op_list:
                op_list.append(Operation(
                    name="Execute",
                    signature=f"execute() → Effect",
                    formal_definition=MathExpression(
                        content=f"Execute {pattern_id} operation",
                        format="latex"
                    )
                ))
            
            operations = Operations(operation=op_list)
            
            # Create Pattern
            pattern = Pattern(
                id=pattern_id,
                version=row['version'] or '1.0',
                metadata=metadata,
                definition=definition,
                properties=properties,
                operations=operations
            )
            
            patterns[pattern_id] = pattern
            
        except Exception as e:
            print(f"  ✗ Error building {pattern_id}: {e}")
            skipped += 1
            continue
    
    print(f"  ✓ Built {len(patterns)} patterns")
    if skipped > 0:
        print(f"  ⊘ Skipped {skipped} invalid rows")
    
    return patterns


def seed_database(
    csv_dir: Path,
    skip_existing: bool = True,
    verbose: bool = True
) -> tuple[int, int, int]:
    """
    Seed the database from CSV files.
    
    Args:
        csv_dir: Directory containing CSV files
        skip_existing: Skip patterns that already exist in DB
        verbose: Print detailed progress
        
    Returns:
        Tuple of (loaded, skipped, failed) counts
    """
    # Build patterns from CSV
    patterns = build_patterns_from_csv(csv_dir)
    
    if not patterns:
        print("✗ No patterns to load")
        return (0, 0, 0)
    
    print(f"\n💾 Loading into database...")
    print("=" * 60)
    
    db = SessionLocal()
    repo = PatternRepository(db)
    
    loaded = 0
    skipped = 0
    failed = 0
    
    for pattern_id, pattern in sorted(patterns.items()):
        try:
            # Check if exists
            if skip_existing:
                existing = repo.get_by_id(pattern.id)
                if existing:
                    if verbose:
                        print(f"⊘ {pattern.id:8} - {pattern.metadata.name[:45]:45} (exists)")
                    skipped += 1
                    continue
            
            # Insert into database
            repo.create(pattern)
            loaded += 1
            
            if verbose:
                print(f"✓ {pattern.id:8} - {pattern.metadata.name[:45]:45} ({pattern.metadata.category})")
        
        except Exception as e:
            failed += 1
            print(f"✗ {pattern_id}: {str(e)[:60]}")
    
    db.close()
    
    return (loaded, skipped, failed)


def main():
    """Main seeding function."""
    print("=" * 60)
    print("Universal Corpus Pattern Database Seeding (from CSV)")
    print("=" * 60)
    
    # Parse arguments
    reset = '--reset' in sys.argv or '-r' in sys.argv
    quiet = '--quiet' in sys.argv or '-q' in sys.argv
    force = '--force' in sys.argv or '-f' in sys.argv
    
    # Determine CSV directory
    csv_dir = Path(__file__).parent / 'output' / 'csv_export'
    
    if not csv_dir.exists():
        print(f"✗ Directory not found: {csv_dir}")
        sys.exit(1)
    
    # Check required files
    required_files = ['patterns_summary.csv', 'components.csv', 'properties.csv', 'operations.csv']
    missing = [f for f in required_files if not (csv_dir / f).exists()]
    
    if missing:
        print(f"✗ Missing required CSV files: {', '.join(missing)}")
        sys.exit(1)
    
    # Reset if requested
    if reset:
        print("\n⚠️  Reset requested - all data will be lost!")
        if not force:
            response = input("Are you sure? (yes/no): ")
            if response.lower() != 'yes':
                print("Aborted.")
                return
        
        print("🗑️  Dropping database...")
        drop_db()
        print("✓ Database dropped")
    
    # Initialize database
    print("\n📦 Initializing database...")
    init_db()
    print("✓ Database ready")
    
    # Seed database
    loaded, skipped, failed = seed_database(
        csv_dir=csv_dir,
        skip_existing=not reset,
        verbose=not quiet
    )
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ Seeding complete!")
    print("=" * 60)
    print(f"  Loaded:  {loaded:3} patterns")
    print(f"  Skipped: {skipped:3} patterns (already exist)")
    print(f"  Failed:  {failed:3} patterns")
    print(f"  Total:   {loaded + skipped:3} patterns in database")
    print("=" * 60)
    
    if failed > 0:
        print(f"\n⚠️  {failed} patterns failed to load. Check errors above.")
    
    print("\nNext steps:")
    print("  1. Start API: python api.py")
    print("  2. View docs: http://localhost:8000/docs")
    print("  3. List patterns: curl http://localhost:8000/patterns")


if __name__ == '__main__':
    if '--help' in sys.argv or '-h' in sys.argv:
        print("Usage: python seed_from_csv.py [OPTIONS]")
        print("\nOptions:")
        print("  --reset, -r   Reset database before seeding")
        print("  --force, -f   Skip confirmation prompt")
        print("  --quiet, -q   Minimal output")
        print("  --help, -h    Show this help message")
        print("\nData source: output/csv_export/*.csv")
        print("\nExamples:")
        print("  python seed_from_csv.py              # Seed with existing data")
        print("  python seed_from_csv.py --reset      # Reset and seed")
        print("  python seed_from_csv.py -r -f -q     # Reset, force, quiet")
    else:
        main()


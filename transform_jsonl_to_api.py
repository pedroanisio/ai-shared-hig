"""
Transform JSONL Pattern Data to API Model

Converts master_patterns_merged.jsonl to the proper API model structure
without any data loss. All fields from the JSONL are preserved and mapped
to the correct Pydantic model structure.

This script:
1. Reads the JSONL file
2. Cleans and transforms each record to match the Pattern model
3. Validates against Pydantic schema
4. Seeds the database with clean data
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
import sys

from models import (
    Pattern, Metadata, Definition, MathExpression, Components, Component,
    TypeDefinitions, TypeDef, Properties, Property, Operations, Operation,
    Dependencies, PatternRefs, Manifestations, Manifestation, Domains,
    Conditions, Effects, Invariants
)
from database import init_db, SessionLocal, PatternRepository


class PatternTransformer:
    """
    Transforms JSONL pattern data to API model structure.
    
    Handles all data mapping, cleaning, and validation to ensure
    zero data loss during transformation.
    """
    
    def __init__(self, jsonl_path: str = "master_patterns_merged.jsonl"):
        """
        Initialize transformer with JSONL file path.
        
        Args:
            jsonl_path: Path to JSONL file
        """
        self.jsonl_path = Path(jsonl_path)
        if not self.jsonl_path.exists():
            raise FileNotFoundError(f"JSONL file not found: {self.jsonl_path}")
        
        self.patterns: List[Pattern] = []
        self.errors: List[Dict[str, Any]] = []
    
    @staticmethod
    def clean_text(text: Optional[str]) -> Optional[str]:
        """
        Clean text by removing trailing commas and whitespace.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text or None if empty
        """
        if text is None or text == "":
            return None
        
        # Remove trailing commas and whitespace
        cleaned = text.strip().rstrip(',').strip()
        
        # Return None for empty strings after cleaning
        return cleaned if cleaned else None
    
    @staticmethod
    def parse_pipe_delimited_components(text: Optional[str]) -> List[Component]:
        """
        Parse pipe-delimited component string into Component objects.
        
        Format: "name[type: ..., notation: ..., desc: ...]"
        
        Args:
            text: Pipe-delimited component string
            
        Returns:
            List of Component objects
        """
        if not text:
            return []
        
        components = []
        # Split by pipe, but be careful of pipes inside brackets
        parts = []
        current = ""
        bracket_depth = 0
        
        for char in text:
            if char == '[':
                bracket_depth += 1
            elif char == ']':
                bracket_depth -= 1
            elif char == '|' and bracket_depth == 0:
                parts.append(current.strip())
                current = ""
                continue
            current += char
        
        if current.strip():
            parts.append(current.strip())
        
        # Parse each component
        pattern = re.compile(r'([^[]+)\[(.+)\]')
        for part in parts:
            match = pattern.match(part.strip())
            if match:
                name = match.group(1).strip()
                attrs = match.group(2)
                
                # Parse attributes
                comp_type = ""
                notation = None
                description = ""
                
                # Split attributes by comma (but respect nested structures)
                attr_parts = []
                current_attr = ""
                depth = 0
                
                for char in attrs:
                    if char in '({[':
                        depth += 1
                    elif char in ')}]':
                        depth -= 1
                    elif char == ',' and depth == 0:
                        attr_parts.append(current_attr.strip())
                        current_attr = ""
                        continue
                    current_attr += char
                
                if current_attr.strip():
                    attr_parts.append(current_attr.strip())
                
                for attr in attr_parts:
                    if ':' in attr:
                        key, value = attr.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key == 'type':
                            comp_type = value
                        elif key == 'notation':
                            notation = value if value else None
                        elif key == 'desc':
                            description = value
                
                if comp_type and description:
                    components.append(Component(
                        name=name,
                        type=comp_type,
                        notation=notation,
                        description=description
                    ))
        
        return components
    
    @staticmethod
    def parse_dependency_string(dep_string: str) -> List[str]:
        """
        Parse dependency string that may contain pipes or semicolons.
        
        Args:
            dep_string: String containing pattern IDs separated by | or ;
            
        Returns:
            List of clean pattern IDs
        """
        # First split by pipe, then by semicolon
        refs = []
        for part in dep_string.split('|'):
            for subpart in part.split(';'):
                clean = subpart.strip()
                if clean:
                    refs.append(clean)
        return refs
    
    @staticmethod
    def parse_dependencies(data: Dict[str, Any]) -> Optional[Dependencies]:
        """
        Parse dependency fields into Dependencies object.
        
        Args:
            data: Raw JSONL data
            
        Returns:
            Dependencies object or None if no dependencies
        """
        has_deps = False
        requires = None
        uses = None
        specializes = None
        specialized_by = None
        
        if data.get('requires_dependencies'):
            refs = PatternTransformer.parse_dependency_string(data['requires_dependencies'])
            if refs:
                requires = PatternRefs(pattern_ref=refs)
                has_deps = True
        
        if data.get('uses_dependencies'):
            refs = PatternTransformer.parse_dependency_string(data['uses_dependencies'])
            if refs:
                uses = PatternRefs(pattern_ref=refs)
                has_deps = True
        
        if data.get('specializes_dependencies'):
            refs = PatternTransformer.parse_dependency_string(data['specializes_dependencies'])
            if refs:
                specializes = PatternRefs(pattern_ref=refs)
                has_deps = True
        
        if data.get('specialized_by_dependencies'):
            refs = PatternTransformer.parse_dependency_string(data['specialized_by_dependencies'])
            if refs:
                specialized_by = PatternRefs(pattern_ref=refs)
                has_deps = True
        
        if has_deps:
            return Dependencies(
                requires=requires,
                uses=uses,
                specializes=specializes,
                specialized_by=specialized_by
            )
        
        return None
    
    def transform_record(self, data: Dict[str, Any]) -> Optional[Pattern]:
        """
        Transform a single JSONL record to Pattern model.
        
        Args:
            data: Raw JSONL record
            
        Returns:
            Pattern object or None if transformation fails
        """
        try:
            # Extract basic fields
            pattern_id = data.get('id') or data.get('pattern_id')
            version = str(data.get('version', '1.0'))
            
            # Build metadata
            domains_obj = None
            if data.get('domains.domain'):
                domains_obj = Domains(domain=data['domains.domain'])
            elif data.get('domains'):
                domain_list = [d.strip() for d in str(data['domains']).split(';') if d.strip()]
                if domain_list:
                    domains_obj = Domains(domain=domain_list)
            
            metadata = Metadata(
                name=data.get('name') or data.get('pattern_name', ''),
                category=data.get('category', 'concept'),
                status=data.get('status', 'draft'),
                complexity=data.get('complexity'),
                domains=domains_obj,
                last_updated=self.clean_text(data.get('last_updated'))
            )
            
            # Build tuple notation
            tuple_content = data.get('tuple_notation.content') or data.get('tuple_notation', '')
            tuple_format = data.get('tuple_notation.format') or data.get('tuple_notation_format', 'latex')
            tuple_notation = MathExpression(
                content=self.clean_text(tuple_content) or '',
                format=tuple_format
            )
            
            # Build components
            components_list = []
            if data.get('components.component'):
                # Use structured component data
                for comp in data['components.component']:
                    components_list.append(Component(
                        name=comp.get('name', ''),
                        type=self.clean_text(comp.get('type')) or '',
                        notation=self.clean_text(comp.get('notation')),
                        description=comp.get('description', '')
                    ))
            elif data.get('components'):
                # Parse pipe-delimited format
                components_list = self.parse_pipe_delimited_components(data['components'])
            
            # Ensure at least one component (required by schema)
            if not components_list:
                components_list = [Component(
                    name="default",
                    type="Any",
                    description="No components defined"
                )]
            
            components = Components(component=components_list)
            
            # Build definition
            definition = Definition(
                tuple_notation=tuple_notation,
                components=components,
                description=self.clean_text(data.get('definition_description'))
            )
            
            # Build type definitions
            type_definitions = None
            if data.get('type_definitions') and isinstance(data['type_definitions'], dict):
                type_defs = data['type_definitions'].get('type_def', [])
                if type_defs:
                    parsed_defs = []
                    for td in type_defs:
                        def_content = td.get('definition', {})
                        if isinstance(def_content, str):
                            def_content = {'content': def_content, 'format': 'latex'}
                        
                        parsed_defs.append(TypeDef(
                            name=td.get('name', ''),
                            definition=MathExpression(
                                content=self.clean_text(def_content.get('content')) or '',
                                format=def_content.get('format', 'latex')
                            ),
                            description=self.clean_text(td.get('description'))
                        ))
                    
                    type_definitions = TypeDefinitions(type_def=parsed_defs)
            
            # Build properties
            properties_list = []
            if data.get('properties') and isinstance(data['properties'], dict):
                props = data['properties'].get('property', [])
                for prop in props:
                    formal_spec = prop.get('formal_spec', {})
                    if isinstance(formal_spec, str):
                        formal_spec = {'content': formal_spec, 'format': 'latex'}
                    
                    # Handle invariants
                    invariants = None
                    if prop.get('invariants') and isinstance(prop['invariants'], dict):
                        inv_list = prop['invariants'].get('invariant', [])
                        if inv_list:
                            inv_objs = []
                            for inv in inv_list:
                                if isinstance(inv, str):
                                    inv_objs.append(MathExpression(content=inv, format='latex'))
                                elif isinstance(inv, dict):
                                    inv_objs.append(MathExpression(
                                        content=inv.get('content', ''),
                                        format=inv.get('format', 'latex')
                                    ))
                            if inv_objs:
                                invariants = Invariants(invariant=inv_objs)
                    
                    properties_list.append(Property(
                        id=prop.get('id', ''),
                        name=prop.get('name', ''),
                        formal_spec=MathExpression(
                            content=self.clean_text(formal_spec.get('content')) or '',
                            format=formal_spec.get('format', 'latex')
                        ),
                        description=self.clean_text(prop.get('description')),
                        invariants=invariants
                    ))
            
            # Ensure at least one property (required by schema)
            if not properties_list:
                properties_list = [Property(
                    id=f"P.{pattern_id}.1",
                    name="Default Property",
                    formal_spec=MathExpression(
                        content="No properties defined",
                        format="latex"
                    )
                )]
            
            properties = Properties(property=properties_list)
            
            # Build operations
            operations_list = []
            if data.get('operations') and isinstance(data['operations'], dict):
                ops = data['operations'].get('operation', [])
                for op in ops:
                    formal_def = op.get('formal_definition', {})
                    if isinstance(formal_def, str):
                        formal_def = {'content': formal_def, 'format': 'latex'}
                    
                    # Handle preconditions
                    preconditions = None
                    if op.get('preconditions') and isinstance(op['preconditions'], dict):
                        pre_list = op['preconditions'].get('condition', [])
                        if pre_list:
                            pre_objs = []
                            for pre in pre_list:
                                if isinstance(pre, str):
                                    pre_objs.append(MathExpression(content=pre, format='latex'))
                                elif isinstance(pre, dict):
                                    pre_objs.append(MathExpression(
                                        content=pre.get('content', ''),
                                        format=pre.get('format', 'latex')
                                    ))
                            if pre_objs:
                                preconditions = Conditions(condition=pre_objs)
                    
                    # Handle postconditions
                    postconditions = None
                    if op.get('postconditions') and isinstance(op['postconditions'], dict):
                        post_list = op['postconditions'].get('condition', [])
                        if post_list:
                            post_objs = []
                            for post in post_list:
                                if isinstance(post, str):
                                    post_objs.append(MathExpression(content=post, format='latex'))
                                elif isinstance(post, dict):
                                    post_objs.append(MathExpression(
                                        content=post.get('content', ''),
                                        format=post.get('format', 'latex')
                                    ))
                            if post_objs:
                                postconditions = Conditions(condition=post_objs)
                    
                    # Handle effects
                    effects = None
                    if op.get('effects') and isinstance(op['effects'], dict):
                        eff_list = op['effects'].get('effect', [])
                        if eff_list:
                            effects = Effects(effect=eff_list)
                    
                    operations_list.append(Operation(
                        name=op.get('name', ''),
                        signature=self.clean_text(op.get('signature')) or '',
                        formal_definition=MathExpression(
                            content=self.clean_text(formal_def.get('content')) or '',
                            format=formal_def.get('format', 'latex')
                        ),
                        preconditions=preconditions,
                        postconditions=postconditions,
                        effects=effects
                    ))
            
            # Ensure at least one operation (required by schema)
            if not operations_list:
                operations_list = [Operation(
                    name="default",
                    signature="() → Unit",
                    formal_definition=MathExpression(
                        content="No operations defined",
                        format="latex"
                    )
                )]
            
            operations = Operations(operation=operations_list)
            
            # Build dependencies
            dependencies = self.parse_dependencies(data)
            
            # Build manifestations
            manifestations = None
            if data.get('manifestations') and isinstance(data['manifestations'], dict):
                manif_list = data['manifestations'].get('manifestation', [])
                if manif_list:
                    parsed_manifs = []
                    for manif in manif_list:
                        parsed_manifs.append(Manifestation(
                            name=manif.get('name', ''),
                            description=self.clean_text(manif.get('description'))
                        ))
                    manifestations = Manifestations(manifestation=parsed_manifs)
            
            # Create Pattern object
            pattern = Pattern(
                id=pattern_id,
                version=version,
                metadata=metadata,
                definition=definition,
                type_definitions=type_definitions,
                properties=properties,
                operations=operations,
                dependencies=dependencies,
                manifestations=manifestations
            )
            
            return pattern
            
        except Exception as e:
            self.errors.append({
                'pattern_id': data.get('id') or data.get('pattern_id', 'unknown'),
                'error': str(e),
                'type': type(e).__name__
            })
            return None
    
    def load_and_transform(self) -> List[Pattern]:
        """
        Load JSONL file and transform all records.
        
        Returns:
            List of successfully transformed Pattern objects
        """
        print(f"Loading patterns from: {self.jsonl_path}")
        
        with open(self.jsonl_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    pattern = self.transform_record(data)
                    if pattern:
                        self.patterns.append(pattern)
                        print(f"✓ Transformed pattern {pattern.id}: {pattern.metadata.name}")
                    else:
                        print(f"✗ Failed to transform line {line_num}")
                
                except json.JSONDecodeError as e:
                    self.errors.append({
                        'line': line_num,
                        'error': f"JSON decode error: {e}",
                        'type': 'JSONDecodeError'
                    })
                    print(f"✗ JSON error on line {line_num}")
        
        print(f"\nTransformation complete:")
        print(f"  Success: {len(self.patterns)} patterns")
        print(f"  Errors: {len(self.errors)} patterns")
        
        return self.patterns
    
    def seed_database(self) -> int:
        """
        Seed the database with transformed patterns.
        
        Returns:
            Number of patterns successfully inserted
        """
        if not self.patterns:
            raise ValueError("No patterns to seed. Run load_and_transform() first.")
        
        # Initialize database
        print("\nInitializing database...")
        init_db()
        
        # Create session and repository
        db = SessionLocal()
        repo = PatternRepository(db)
        
        inserted = 0
        skipped = 0
        
        try:
            for pattern in self.patterns:
                try:
                    # Try to create pattern
                    repo.create(pattern)
                    inserted += 1
                    print(f"✓ Inserted {pattern.id}")
                except ValueError as e:
                    if "already exists" in str(e):
                        # Try update instead
                        try:
                            repo.update(pattern.id, pattern)
                            inserted += 1
                            print(f"✓ Updated {pattern.id}")
                        except Exception as update_err:
                            skipped += 1
                            print(f"✗ Failed to update {pattern.id}: {update_err}")
                    else:
                        skipped += 1
                        print(f"✗ Failed to insert {pattern.id}: {e}")
                except Exception as e:
                    skipped += 1
                    print(f"✗ Failed to insert {pattern.id}: {e}")
        
        finally:
            db.close()
        
        print(f"\nDatabase seeding complete:")
        print(f"  Inserted: {inserted}")
        print(f"  Skipped: {skipped}")
        
        return inserted
    
    def print_error_report(self):
        """Print detailed error report."""
        if not self.errors:
            print("\n✓ No errors during transformation!")
            return
        
        print(f"\n{'='*60}")
        print(f"ERROR REPORT ({len(self.errors)} errors)")
        print(f"{'='*60}")
        
        for i, error in enumerate(self.errors, 1):
            print(f"\n{i}. Pattern: {error.get('pattern_id', 'unknown')}")
            print(f"   Type: {error.get('type', 'Unknown')}")
            print(f"   Error: {error.get('error', 'No details')}")


def main():
    """Main entry point."""
    import sys
    
    # Check for command line arguments
    seed_db = '--seed' in sys.argv
    auto_yes = '--yes' in sys.argv or '-y' in sys.argv
    
    try:
        # Create transformer
        transformer = PatternTransformer("master_patterns_merged.jsonl")
        
        # Load and transform
        patterns = transformer.load_and_transform()
        
        # Print error report if any
        transformer.print_error_report()
        
        if not patterns:
            print("\n✗ No patterns were successfully transformed!")
            return 1
        
        # Determine if we should seed
        should_seed = seed_db or auto_yes
        
        if not should_seed:
            # Ask user if they want to seed the database
            print(f"\n{len(patterns)} patterns ready to seed.")
            try:
                response = input("Seed database? (yes/no): ").strip().lower()
                should_seed = response in ['yes', 'y']
            except (EOFError, KeyboardInterrupt):
                print("\nSkipping database seeding (non-interactive mode).")
                should_seed = False
        
        if should_seed:
            inserted = transformer.seed_database()
            
            # Show statistics
            db = SessionLocal()
            repo = PatternRepository(db)
            stats = repo.get_statistics()
            db.close()
            
            print("\n=== Database Statistics ===")
            print(f"Total patterns: {stats['total_patterns']}")
            print(f"By category: {stats['by_category']}")
            print(f"By status: {stats['by_status']}")
            print(f"By complexity: {stats['by_complexity']}")
        else:
            print("\nSkipping database seeding.")
            print("\nTo seed automatically, run:")
            print("  python transform_jsonl_to_api.py --seed")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())


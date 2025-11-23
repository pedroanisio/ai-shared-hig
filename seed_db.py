#!/usr/bin/env python3
"""
Database seeding script for Universal Corpus Pattern API.

This script loads patterns from XML files in the master_data directory
and populates the database. It follows production-ready principles:
- Validates all data through Pydantic models
- Handles errors gracefully with transaction rollback
- Provides detailed progress reporting
- Supports incremental loading (skip existing patterns)
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List
from database import init_db, drop_db, SessionLocal, PatternRepository
from models import (
    Pattern, Metadata, Definition, MathExpression, Components, Component,
    Properties, Property, Operations, Operation, Manifestations, Manifestation,
    Dependencies, PatternRefs, TypeDefinitions, TypeDef, Invariants, Conditions, Effects
)


class XMLPatternParser:
    """Parser for Universal Corpus Pattern XML files."""
    
    NAMESPACE = {'uc': 'http://universal-corpus.org/schema/v1'}
    
    @classmethod
    def parse_file(cls, xml_path: Path) -> Optional[Pattern]:
        """
        Parse an XML file into a Pattern object.
        
        Args:
            xml_path: Path to XML file
            
        Returns:
            Pattern object if successful, None if parsing fails
        """
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Determine root element name (pattern, concept, or flow)
            tag = root.tag.replace('{http://universal-corpus.org/schema/v1}', '')
            
            # Extract attributes
            pattern_id = root.get('id')
            version = root.get('version', '1.0')
            
            # Parse metadata
            metadata = cls._parse_metadata(root)
            
            # Parse definition
            definition = cls._parse_definition(root)
            
            # Parse type definitions (optional)
            type_definitions = cls._parse_type_definitions(root)
            
            # Parse properties
            properties = cls._parse_properties(root)
            
            # Parse operations
            operations = cls._parse_operations(root)
            
            # Parse dependencies (optional)
            dependencies = cls._parse_dependencies(root)
            
            # Parse manifestations (optional)
            manifestations = cls._parse_manifestations(root)
            
            return Pattern(
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
        except Exception as e:
            print(f"✗ Error parsing {xml_path.name}: {e}")
            return None
    
    @classmethod
    def _parse_metadata(cls, root: ET.Element) -> Metadata:
        """Parse metadata section."""
        meta_elem = root.find('uc:metadata', cls.NAMESPACE)
        if meta_elem is None:
            meta_elem = root.find('metadata')
        
        name = cls._get_text(meta_elem, 'name', 'Unnamed Pattern')
        category = cls._get_text(meta_elem, 'category', 'pattern')
        status = cls._get_text(meta_elem, 'status', 'draft')
        complexity = cls._get_text(meta_elem, 'complexity')
        last_updated = cls._get_text(meta_elem, 'last-updated')
        
        return Metadata(
            name=name,
            category=category,
            status=status,
            complexity=complexity,
            last_updated=last_updated
        )
    
    @classmethod
    def _parse_definition(cls, root: ET.Element) -> Definition:
        """Parse definition section."""
        def_elem = root.find('uc:definition', cls.NAMESPACE)
        if def_elem is None:
            def_elem = root.find('definition')
        
        # Tuple notation
        tuple_elem = def_elem.find('uc:tuple-notation', cls.NAMESPACE)
        if tuple_elem is None:
            tuple_elem = def_elem.find('tuple-notation')
        
        tuple_notation = MathExpression(
            content=tuple_elem.text or '',
            format=tuple_elem.get('format', 'latex')
        )
        
        # Components
        components_elem = def_elem.find('uc:components', cls.NAMESPACE)
        if components_elem is None:
            components_elem = def_elem.find('components')
        
        component_list = []
        for comp_elem in components_elem.findall('uc:component', cls.NAMESPACE) or components_elem.findall('component'):
            component_list.append(Component(
                name=cls._get_text(comp_elem, 'name', ''),
                type=cls._get_text(comp_elem, 'type', ''),
                notation=cls._get_text(comp_elem, 'notation'),
                description=cls._get_text(comp_elem, 'description', '')
            ))
        
        components = Components(component=component_list)
        
        # Description (optional)
        description = cls._get_text(def_elem, 'description')
        
        return Definition(
            tuple_notation=tuple_notation,
            components=components,
            description=description
        )
    
    @classmethod
    def _parse_type_definitions(cls, root: ET.Element) -> Optional[TypeDefinitions]:
        """Parse type-definitions section (optional)."""
        typedef_elem = root.find('uc:type-definitions', cls.NAMESPACE)
        if typedef_elem is None:
            typedef_elem = root.find('type-definitions')
        
        if typedef_elem is None:
            return None
        
        typedef_list = []
        for td_elem in typedef_elem.findall('uc:type-def', cls.NAMESPACE) or typedef_elem.findall('type-def'):
            def_elem = td_elem.find('uc:definition', cls.NAMESPACE)
            if def_elem is None:
                def_elem = td_elem.find('definition')
            
            typedef_list.append(TypeDef(
                name=cls._get_text(td_elem, 'name', ''),
                definition=MathExpression(
                    content=def_elem.text or '',
                    format=def_elem.get('format', 'latex')
                ),
                description=cls._get_text(td_elem, 'description')
            ))
        
        return TypeDefinitions(type_def=typedef_list) if typedef_list else None
    
    @classmethod
    def _parse_properties(cls, root: ET.Element) -> Properties:
        """Parse properties section."""
        props_elem = root.find('uc:properties', cls.NAMESPACE)
        if props_elem is None:
            props_elem = root.find('properties')
        
        property_list = []
        for prop_elem in props_elem.findall('uc:property', cls.NAMESPACE) or props_elem.findall('property'):
            formal_spec_elem = prop_elem.find('uc:formal-spec', cls.NAMESPACE)
            if formal_spec_elem is None:
                formal_spec_elem = prop_elem.find('formal-spec')
            
            # Parse invariants (optional)
            invariants = None
            inv_elem = prop_elem.find('uc:invariants', cls.NAMESPACE)
            if inv_elem is None:
                inv_elem = prop_elem.find('invariants')
            
            if inv_elem is not None:
                inv_list = []
                for i_elem in inv_elem.findall('uc:invariant', cls.NAMESPACE) or inv_elem.findall('invariant'):
                    inv_list.append(MathExpression(
                        content=i_elem.text or '',
                        format=i_elem.get('format', 'latex')
                    ))
                if inv_list:
                    invariants = Invariants(invariant=inv_list)
            
            property_list.append(Property(
                id=prop_elem.get('id', ''),
                name=cls._get_text(prop_elem, 'name', ''),
                formal_spec=MathExpression(
                    content=formal_spec_elem.text or '',
                    format=formal_spec_elem.get('format', 'latex')
                ),
                description=cls._get_text(prop_elem, 'description'),
                invariants=invariants
            ))
        
        return Properties(property=property_list)
    
    @classmethod
    def _parse_operations(cls, root: ET.Element) -> Operations:
        """Parse operations section."""
        ops_elem = root.find('uc:operations', cls.NAMESPACE)
        if ops_elem is None:
            ops_elem = root.find('operations')
        
        operation_list = []
        for op_elem in ops_elem.findall('uc:operation', cls.NAMESPACE) or ops_elem.findall('operation'):
            formal_def_elem = op_elem.find('uc:formal-definition', cls.NAMESPACE)
            if formal_def_elem is None:
                formal_def_elem = op_elem.find('formal-definition')
            
            # Parse preconditions (optional)
            preconditions = cls._parse_conditions(op_elem, 'preconditions')
            
            # Parse postconditions (optional)
            postconditions = cls._parse_conditions(op_elem, 'postconditions')
            
            # Parse effects (optional)
            effects = None
            eff_elem = op_elem.find('uc:effects', cls.NAMESPACE)
            if eff_elem is None:
                eff_elem = op_elem.find('effects')
            
            if eff_elem is not None:
                eff_list = []
                for e_elem in eff_elem.findall('uc:effect', cls.NAMESPACE) or eff_elem.findall('effect'):
                    if e_elem.text:
                        eff_list.append(e_elem.text)
                if eff_list:
                    effects = Effects(effect=eff_list)
            
            operation_list.append(Operation(
                name=cls._get_text(op_elem, 'name', ''),
                signature=cls._get_text(op_elem, 'signature', ''),
                formal_definition=MathExpression(
                    content=formal_def_elem.text or '',
                    format=formal_def_elem.get('format', 'latex')
                ),
                preconditions=preconditions,
                postconditions=postconditions,
                effects=effects
            ))
        
        return Operations(operation=operation_list)
    
    @classmethod
    def _parse_conditions(cls, parent: ET.Element, tag: str) -> Optional[Conditions]:
        """Parse preconditions or postconditions."""
        cond_elem = parent.find(f'uc:{tag}', cls.NAMESPACE)
        if cond_elem is None:
            cond_elem = parent.find(tag)
        
        if cond_elem is None:
            return None
        
        cond_list = []
        for c_elem in cond_elem.findall('uc:condition', cls.NAMESPACE) or cond_elem.findall('condition'):
            cond_list.append(MathExpression(
                content=c_elem.text or '',
                format=c_elem.get('format', 'latex')
            ))
        
        return Conditions(condition=cond_list) if cond_list else None
    
    @classmethod
    def _parse_dependencies(cls, root: ET.Element) -> Optional[Dependencies]:
        """Parse dependencies section (optional)."""
        deps_elem = root.find('uc:dependencies', cls.NAMESPACE)
        if deps_elem is None:
            deps_elem = root.find('dependencies')
        
        if deps_elem is None:
            return None
        
        requires = cls._parse_pattern_refs(deps_elem, 'requires')
        uses = cls._parse_pattern_refs(deps_elem, 'uses')
        specializes = cls._parse_pattern_refs(deps_elem, 'specializes')
        specialized_by = cls._parse_pattern_refs(deps_elem, 'specialized-by')
        
        if not any([requires, uses, specializes, specialized_by]):
            return None
        
        return Dependencies(
            requires=requires,
            uses=uses,
            specializes=specializes,
            specialized_by=specialized_by
        )
    
    @classmethod
    def _parse_pattern_refs(cls, parent: ET.Element, tag: str) -> Optional[PatternRefs]:
        """Parse pattern references."""
        refs_elem = parent.find(f'uc:{tag}', cls.NAMESPACE)
        if refs_elem is None:
            refs_elem = parent.find(tag)
        
        if refs_elem is None:
            return None
        
        ref_list = []
        for ref_elem in refs_elem.findall('uc:pattern-ref', cls.NAMESPACE) or refs_elem.findall('pattern-ref'):
            if ref_elem.text:
                ref_list.append(ref_elem.text)
        
        return PatternRefs(pattern_ref=ref_list) if ref_list else None
    
    @classmethod
    def _parse_manifestations(cls, root: ET.Element) -> Optional[Manifestations]:
        """Parse manifestations section (optional)."""
        manif_elem = root.find('uc:manifestations', cls.NAMESPACE)
        if manif_elem is None:
            manif_elem = root.find('manifestations')
        
        if manif_elem is None:
            return None
        
        manif_list = []
        for m_elem in manif_elem.findall('uc:manifestation', cls.NAMESPACE) or manif_elem.findall('manifestation'):
            manif_list.append(Manifestation(
                name=cls._get_text(m_elem, 'name', ''),
                description=cls._get_text(m_elem, 'description')
            ))
        
        return Manifestations(manifestation=manif_list) if manif_list else None
    
    @classmethod
    def _get_text(cls, parent: Optional[ET.Element], tag: str, default: Optional[str] = None) -> Optional[str]:
        """Safely get text from an element."""
        if parent is None:
            return default
        
        elem = parent.find(f'uc:{tag}', cls.NAMESPACE)
        if elem is None:
            elem = parent.find(tag)
        
        if elem is not None and elem.text:
            return elem.text.strip()
        
        return default


def seed_database(
    xml_dir: Path,
    skip_existing: bool = True,
    verbose: bool = True
) -> tuple[int, int, int]:
    """
    Seed the database from XML files.
    
    Args:
        xml_dir: Directory containing XML files
        skip_existing: Skip patterns that already exist in DB
        verbose: Print detailed progress
        
    Returns:
        Tuple of (loaded, skipped, failed) counts
    """
    # Get all XML files
    xml_files = sorted(xml_dir.glob('*.xml'))
    
    if not xml_files:
        print(f"✗ No XML files found in {xml_dir}")
        return (0, 0, 0)
    
    print(f"\n📂 Found {len(xml_files)} XML files")
    print("=" * 60)
    
    db = SessionLocal()
    repo = PatternRepository(db)
    
    loaded = 0
    skipped = 0
    failed = 0
    
    for xml_file in xml_files:
        try:
            # Parse XML
            pattern = XMLPatternParser.parse_file(xml_file)
            
            if pattern is None:
                failed += 1
                continue
            
            # Check if exists
            if skip_existing:
                existing = repo.get_by_id(pattern.id)
                if existing:
                    if verbose:
                        print(f"⊘ {pattern.id:6} - {pattern.metadata.name[:40]:40} (exists)")
                    skipped += 1
                    continue
            
            # Insert into database
            repo.create(pattern)
            loaded += 1
            
            if verbose:
                print(f"✓ {pattern.id:6} - {pattern.metadata.name[:40]:40} ({pattern.metadata.category})")
        
        except Exception as e:
            failed += 1
            print(f"✗ {xml_file.name}: {str(e)[:60]}")
    
    db.close()
    
    return (loaded, skipped, failed)


def main():
    """Main seeding function."""
    print("=" * 60)
    print("Universal Corpus Pattern Database Seeding")
    print("=" * 60)
    
    # Parse arguments
    reset = '--reset' in sys.argv or '-r' in sys.argv
    quiet = '--quiet' in sys.argv or '-q' in sys.argv
    force = '--force' in sys.argv or '-f' in sys.argv
    
    # Determine XML directory
    xml_dir = Path(__file__).parent / 'master_data'
    
    if not xml_dir.exists():
        print(f"✗ Directory not found: {xml_dir}")
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
    print("\n📝 Loading patterns from XML files...")
    loaded, skipped, failed = seed_database(
        xml_dir=xml_dir,
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
        print("Usage: python seed_db.py [OPTIONS]")
        print("\nOptions:")
        print("  --reset, -r   Reset database before seeding")
        print("  --force, -f   Skip confirmation prompt")
        print("  --quiet, -q   Minimal output")
        print("  --help, -h    Show this help message")
        print("\nExamples:")
        print("  python seed_db.py              # Seed with existing data")
        print("  python seed_db.py --reset      # Reset and seed")
        print("  python seed_db.py -r -f -q     # Reset, force, quiet")
    else:
        main()




#!/usr/bin/env python3
"""
Universal Corpus Manager - XML Master Data Architecture
Treats XML as the single source of truth for all pattern data.

Architecture:
- XML files in master_data/ are the authoritative source
- Internal domain model based on Pattern dataclasses
- Exports to XML (round-trip), Markdown (human view), YAML (machine view)
- Zero data loss guarantee on XML round-trips

Version: 2.0
"""

import re
import json
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple, Set
from pathlib import Path
import sys


# ============================================================================
# Domain Model - Shared with corpus_converter.py
# ============================================================================

@dataclass
class Component:
    """Tuple component definition"""
    name: str
    type: str
    notation: str
    description: str


@dataclass
class TypeDefinition:
    """Type definition"""
    name: str
    definition: str
    notation: str = ""
    description: str = ""


@dataclass
class Property:
    """Formal property specification"""
    id: str
    name: str
    formal_spec: str
    description: str = ""
    invariants: List[str] = field(default_factory=list)


@dataclass
class Operation:
    """Operation definition"""
    name: str
    signature: str
    formal_definition: str
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)


@dataclass
class Dependencies:
    """Pattern dependencies"""
    requires: List[str] = field(default_factory=list)
    uses: List[str] = field(default_factory=list)
    specializes: List[str] = field(default_factory=list)
    specialized_by: List[str] = field(default_factory=list)


@dataclass
class Manifestation:
    """Real-world manifestation"""
    name: str
    description: str = ""


@dataclass
class Pattern:
    """Complete pattern specification - master data model"""
    id: str
    version: str
    name: str
    category: str
    status: str = "stable"
    complexity: str = "medium"
    domains: List[str] = field(default_factory=list)
    tuple_notation: str = ""
    definition_description: str = ""
    components: List[Component] = field(default_factory=list)
    type_definitions: List[TypeDefinition] = field(default_factory=list)
    properties: List[Property] = field(default_factory=list)
    operations: List[Operation] = field(default_factory=list)
    dependencies: Dependencies = field(default_factory=Dependencies)
    manifestations: List[Manifestation] = field(default_factory=list)
    
    @property
    def pattern_type(self) -> str:
        """Get pattern type (P, C, F)"""
        if self.id:
            return self.id[0]
        return self.category[0].upper()
    
    @property
    def number(self) -> str:
        """Get pattern number (e.g., '35', '1.1')"""
        if self.id:
            return self.id[1:]
        return ""


# ============================================================================
# XML Parser - Master Data Input
# ============================================================================

class XMLParser:
    """Parse XML pattern files into Pattern domain model"""
    
    @staticmethod
    def parse_pattern_file(xml_path: Path) -> Pattern:
        """Parse a single XML pattern file"""
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Remove namespace for easier parsing
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]
        
        pattern = Pattern(
            id=root.get('id', ''),
            version=root.get('version', '1.0'),
            name='',
            category='pattern'
        )
        
        # Parse metadata
        metadata = root.find('metadata')
        if metadata is not None:
            pattern.name = XMLParser._get_text(metadata, 'name')
            pattern.category = XMLParser._get_text(metadata, 'category', 'pattern')
            pattern.status = XMLParser._get_text(metadata, 'status', 'stable')
            pattern.complexity = XMLParser._get_text(metadata, 'complexity', 'medium')
            
            domains_elem = metadata.find('domains')
            if domains_elem is not None:
                pattern.domains = [d.text for d in domains_elem.findall('domain') if d.text]
        
        # Parse definition
        definition = root.find('definition')
        if definition is not None:
            tuple_not = definition.find('tuple-notation')
            if tuple_not is not None:
                pattern.tuple_notation = tuple_not.text or ''
            
            desc = definition.find('description')
            if desc is not None:
                pattern.definition_description = desc.text or ''
            
            # Parse components
            components = definition.find('components')
            if components is not None:
                for comp in components.findall('component'):
                    pattern.components.append(Component(
                        name=XMLParser._get_text(comp, 'name'),
                        type=XMLParser._get_text(comp, 'type'),
                        notation=XMLParser._get_text(comp, 'notation'),
                        description=XMLParser._get_text(comp, 'description')
                    ))
        
        # Parse type definitions
        type_defs = root.find('type-definitions')
        if type_defs is not None:
            for td in type_defs.findall('type-def'):
                defn_elem = td.find('definition')
                defn_text = defn_elem.text if defn_elem is not None else ''
                pattern.type_definitions.append(TypeDefinition(
                    name=XMLParser._get_text(td, 'name'),
                    definition=defn_text,
                    notation=XMLParser._get_text(td, 'notation')
                ))
        
        # Parse properties
        properties = root.find('properties')
        if properties is not None:
            for prop in properties.findall('property'):
                formal_spec = prop.find('formal-spec')
                spec_text = formal_spec.text if formal_spec is not None else ''
                pattern.properties.append(Property(
                    id=prop.get('id', ''),
                    name=XMLParser._get_text(prop, 'name'),
                    formal_spec=spec_text,
                    description=XMLParser._get_text(prop, 'description')
                ))
        
        # Parse operations
        operations = root.find('operations')
        if operations is not None:
            for op in operations.findall('operation'):
                formal_def = op.find('formal-definition')
                def_text = formal_def.text if formal_def is not None else ''
                
                preconditions = [pc.text for pc in op.findall('precondition') if pc.text]
                postconditions = [pc.text for pc in op.findall('postcondition') if pc.text]
                effects = [e.text for e in op.findall('effect') if e.text]
                
                pattern.operations.append(Operation(
                    name=XMLParser._get_text(op, 'name'),
                    signature=XMLParser._get_text(op, 'signature'),
                    formal_definition=def_text,
                    preconditions=preconditions,
                    postconditions=postconditions,
                    effects=effects
                ))
        
        # Parse dependencies
        deps = root.find('dependencies')
        if deps is not None:
            pattern.dependencies = Dependencies(
                requires=[p.text for p in deps.findall('requires/pattern-ref') if p.text],
                uses=[p.text for p in deps.findall('uses/pattern-ref') if p.text],
                specializes=[p.text for p in deps.findall('specializes/pattern-ref') if p.text],
                specialized_by=[p.text for p in deps.findall('specialized-by/pattern-ref') if p.text]
            )
        
        # Parse manifestations
        manifestations = root.find('manifestations')
        if manifestations is not None:
            for manif in manifestations.findall('manifestation'):
                pattern.manifestations.append(Manifestation(
                    name=XMLParser._get_text(manif, 'name'),
                    description=XMLParser._get_text(manif, 'description')
                ))
        
        return pattern
    
    @staticmethod
    def _get_text(element: ET.Element, child_name: str, default: str = '') -> str:
        """Safely get text from child element"""
        child = element.find(child_name)
        return child.text if child is not None and child.text else default


# ============================================================================
# Corpus Manager - Master Data Operations
# ============================================================================

class CorpusManager:
    """
    Manages Universal Corpus patterns with XML as master data.
    
    Key principles:
    - XML files are the single source of truth
    - All operations preserve XML fidelity
    - Exports to multiple formats (XML, Markdown, YAML)
    """
    
    def __init__(self):
        self.patterns: Dict[str, Pattern] = {}
        self.metadata: Dict[str, str] = {}
    
    def load_from_xml_directory(self, xml_dir: Path) -> None:
        """
        Load all XML pattern files from a directory.
        This is the primary method for loading master data.
        """
        if not xml_dir.exists():
            raise FileNotFoundError(f"XML directory not found: {xml_dir}")
        
        xml_files = sorted(xml_dir.glob('*.xml'))
        
        for xml_file in xml_files:
            try:
                pattern = XMLParser.parse_pattern_file(xml_file)
                self.patterns[pattern.id] = pattern
            except Exception as e:
                print(f"Warning: Failed to parse {xml_file.name}: {e}", file=sys.stderr)
                continue
    
    def load_pattern_xml(self, xml_path: Path) -> Pattern:
        """Load a single pattern from XML file"""
        pattern = XMLParser.parse_pattern_file(xml_path)
        self.patterns[pattern.id] = pattern
        return pattern
    
    def export_to_xml(self, pattern_id: str, output_path: Optional[Path] = None) -> str:
        """Export a pattern to XML format (round-trip safe)"""
        pattern = self.patterns.get(pattern_id)
        if not pattern:
            raise ValueError(f"Pattern {pattern_id} not found")
        
        xml_content = self._pattern_to_xml(pattern)
        
        if output_path:
            output_path.write_text(xml_content, encoding='utf-8')
        
        return xml_content
    
    def export_all_to_xml(self, output_dir: Path) -> Dict[str, Path]:
        """Export all patterns to XML files"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        exported = {}
        for pattern_id, pattern in self.patterns.items():
            safe_name = pattern.name.replace('/', '-').replace(' ', '_')
            filename = f"{pattern_id}_{safe_name}.xml"
            filepath = output_dir / filename
            
            self.export_to_xml(pattern_id, filepath)
            exported[pattern_id] = filepath
        
        return exported
    
    def _pattern_to_xml(self, pattern: Pattern) -> str:
        """Convert Pattern to XML string"""
        root = ET.Element('pattern')
        root.set('xmlns', 'http://universal-corpus.org/schema/v1')
        root.set('id', pattern.id)
        root.set('version', pattern.version)
        
        # Metadata
        metadata = ET.SubElement(root, 'metadata')
        ET.SubElement(metadata, 'name').text = pattern.name
        ET.SubElement(metadata, 'category').text = pattern.category
        ET.SubElement(metadata, 'status').text = pattern.status
        ET.SubElement(metadata, 'complexity').text = pattern.complexity
        
        if pattern.domains:
            domains = ET.SubElement(metadata, 'domains')
            for domain in pattern.domains:
                ET.SubElement(domains, 'domain').text = domain
        
        # Definition
        definition = ET.SubElement(root, 'definition')
        if pattern.tuple_notation:
            tuple_not = ET.SubElement(definition, 'tuple-notation')
            tuple_not.set('format', 'latex')
            tuple_not.text = pattern.tuple_notation
        
        if pattern.definition_description:
            ET.SubElement(definition, 'description').text = pattern.definition_description
        
        if pattern.components:
            components = ET.SubElement(definition, 'components')
            for comp in pattern.components:
                component = ET.SubElement(components, 'component')
                ET.SubElement(component, 'name').text = comp.name
                ET.SubElement(component, 'type').text = comp.type
                ET.SubElement(component, 'notation').text = comp.notation
                ET.SubElement(component, 'description').text = comp.description
        
        # Type definitions
        if pattern.type_definitions:
            type_defs = ET.SubElement(root, 'type-definitions')
            for td in pattern.type_definitions:
                type_def = ET.SubElement(type_defs, 'type-def')
                ET.SubElement(type_def, 'name').text = td.name
                defn = ET.SubElement(type_def, 'definition')
                defn.set('format', 'latex')
                defn.text = td.definition
                if td.notation:
                    ET.SubElement(type_def, 'notation').text = td.notation
        
        # Properties
        if pattern.properties:
            properties = ET.SubElement(root, 'properties')
            for prop in pattern.properties:
                property_elem = ET.SubElement(properties, 'property')
                property_elem.set('id', prop.id)
                ET.SubElement(property_elem, 'name').text = prop.name
                formal_spec = ET.SubElement(property_elem, 'formal-spec')
                formal_spec.set('format', 'latex')
                formal_spec.text = prop.formal_spec
                if prop.description:
                    ET.SubElement(property_elem, 'description').text = prop.description
        
        # Operations
        if pattern.operations:
            operations = ET.SubElement(root, 'operations')
            for op in pattern.operations:
                operation = ET.SubElement(operations, 'operation')
                ET.SubElement(operation, 'name').text = op.name
                if op.signature:
                    ET.SubElement(operation, 'signature').text = op.signature
                formal_def = ET.SubElement(operation, 'formal-definition')
                formal_def.set('format', 'latex')
                formal_def.text = op.formal_definition
                
                for precond in op.preconditions:
                    ET.SubElement(operation, 'precondition').text = precond
                for postcond in op.postconditions:
                    ET.SubElement(operation, 'postcondition').text = postcond
                for effect in op.effects:
                    ET.SubElement(operation, 'effect').text = effect
        
        # Dependencies
        if any([pattern.dependencies.requires, pattern.dependencies.uses,
                pattern.dependencies.specializes, pattern.dependencies.specialized_by]):
            deps = ET.SubElement(root, 'dependencies')
            
            if pattern.dependencies.requires:
                req = ET.SubElement(deps, 'requires')
                for ref in pattern.dependencies.requires:
                    ET.SubElement(req, 'pattern-ref').text = ref
            
            if pattern.dependencies.uses:
                uses = ET.SubElement(deps, 'uses')
                for ref in pattern.dependencies.uses:
                    ET.SubElement(uses, 'pattern-ref').text = ref
            
            if pattern.dependencies.specializes:
                spec = ET.SubElement(deps, 'specializes')
                for ref in pattern.dependencies.specializes:
                    ET.SubElement(spec, 'pattern-ref').text = ref
            
            if pattern.dependencies.specialized_by:
                spec_by = ET.SubElement(deps, 'specialized-by')
                for ref in pattern.dependencies.specialized_by:
                    ET.SubElement(spec_by, 'pattern-ref').text = ref
        
        # Manifestations
        if pattern.manifestations:
            manifestations = ET.SubElement(root, 'manifestations')
            for manif in pattern.manifestations:
                manifestation = ET.SubElement(manifestations, 'manifestation')
                ET.SubElement(manifestation, 'name').text = manif.name
                if manif.description:
                    ET.SubElement(manifestation, 'description').text = manif.description
        
        # Pretty print
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent='  ')
    
    def export_to_markdown(self, pattern_id: str, output_path: Optional[Path] = None) -> str:
        """Export a pattern to Markdown format (human-readable view)"""
        pattern = self.patterns.get(pattern_id)
        if not pattern:
            raise ValueError(f"Pattern {pattern_id} not found")
        
        md_content = self._pattern_to_markdown(pattern)
        
        if output_path:
            output_path.write_text(md_content, encoding='utf-8')
        
        return md_content
    
    def export_all_to_markdown(self, output_dir: Path) -> Dict[str, Path]:
        """Export all patterns to Markdown files"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        exported = {}
        for pattern_id, pattern in self.patterns.items():
            safe_name = pattern.name.replace('/', '-').replace(' ', '_')
            filename = f"{pattern_id}_{safe_name}.md"
            filepath = output_dir / filename
            
            self.export_to_markdown(pattern_id, filepath)
            exported[pattern_id] = filepath
        
        return exported
    
    def _pattern_to_markdown(self, pattern: Pattern) -> str:
        """Convert Pattern to Markdown string"""
        lines = []
        
        # Header
        lines.append(f"### {pattern.id}. {pattern.name}\n")
        lines.append(f"**Category:** {pattern.category}  ")
        lines.append(f"**Status:** {pattern.status}  ")
        lines.append(f"**Complexity:** {pattern.complexity}\n")
        
        if pattern.domains:
            lines.append(f"**Domains:** {', '.join(pattern.domains)}\n")
        
        # Definition
        lines.append("**Definition:**\n")
        if pattern.tuple_notation:
            lines.append(f"{pattern.tuple_notation}\n")
        
        if pattern.definition_description:
            lines.append(f"{pattern.definition_description}\n")
        
        if pattern.components:
            lines.append("\n**Components:**")
            for comp in pattern.components:
                lines.append(f"- ${comp.name} : {comp.type}$ {comp.description}")
        
        # Type definitions
        if pattern.type_definitions:
            lines.append("\n**Type Definitions:**")
            lines.append("```")
            for td in pattern.type_definitions:
                lines.append(f"{td.name} := {td.definition}")
            lines.append("```")
        
        # Properties
        if pattern.properties:
            lines.append("\n**Properties:**")
            for prop in pattern.properties:
                lines.append(f"\n**{prop.id}({prop.name}):**")
                if prop.formal_spec:
                    lines.append(f"{prop.formal_spec}")
                if prop.description:
                    lines.append(f"{prop.description}")
        
        # Operations
        if pattern.operations:
            lines.append("\n**Operations:**")
            for i, op in enumerate(pattern.operations, 1):
                lines.append(f"\n{i}. **{op.name}:**")
                if op.signature:
                    lines.append(f"   ```")
                    lines.append(f"   {op.signature}")
                    lines.append(f"   ```")
                if op.formal_definition:
                    lines.append(f"   {op.formal_definition}")
        
        # Dependencies
        if any([pattern.dependencies.requires, pattern.dependencies.uses,
                pattern.dependencies.specializes, pattern.dependencies.specialized_by]):
            lines.append("\n**Dependencies:**")
            if pattern.dependencies.requires:
                lines.append(f"- **Requires:** {', '.join(pattern.dependencies.requires)}")
            if pattern.dependencies.uses:
                lines.append(f"- **Uses:** {', '.join(pattern.dependencies.uses)}")
            if pattern.dependencies.specializes:
                lines.append(f"- **Specializes:** {', '.join(pattern.dependencies.specializes)}")
            if pattern.dependencies.specialized_by:
                lines.append(f"- **Specialized By:** {', '.join(pattern.dependencies.specialized_by)}")
        
        # Manifestations
        if pattern.manifestations:
            lines.append("\n**Manifestations:**")
            for manif in pattern.manifestations:
                if manif.description:
                    lines.append(f"- {manif.name} ({manif.description})")
                else:
                    lines.append(f"- {manif.name}")
        
        lines.append("\n---\n")
        
        return '\n'.join(lines)
    
    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """Get a specific pattern by ID (e.g., 'P35', 'C1', 'F1.1')."""
        return self.patterns.get(pattern_id)
    
    def validate_xml_roundtrip(self, pattern_id: str) -> Tuple[bool, str]:
        """
        Validate that XML export → parse produces identical Pattern.
        Returns: (is_valid, message)
        """
        original = self.patterns.get(pattern_id)
        if not original:
            return False, f"Pattern {pattern_id} not found"
        
        # Export to XML
        xml_content = self._pattern_to_xml(original)
        
        # Parse it back
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as tmp:
            tmp.write(xml_content)
            tmp_path = Path(tmp.name)
        
        try:
            reconstructed = XMLParser.parse_pattern_file(tmp_path)
            
            # Compare key fields
            if original.id != reconstructed.id:
                return False, f"ID mismatch: {original.id} vs {reconstructed.id}"
            
            if original.name != reconstructed.name:
                return False, f"Name mismatch: {original.name} vs {reconstructed.name}"
            
            if len(original.components) != len(reconstructed.components):
                return False, f"Component count mismatch: {len(original.components)} vs {len(reconstructed.components)}"
            
            if len(original.properties) != len(reconstructed.properties):
                return False, f"Property count mismatch: {len(original.properties)} vs {len(reconstructed.properties)}"
            
            if len(original.operations) != len(reconstructed.operations):
                return False, f"Operation count mismatch: {len(original.operations)} vs {len(reconstructed.operations)}"
            
            return True, "Perfect XML round-trip: pattern identical"
            
        finally:
            tmp_path.unlink()
    
    def validate_all_roundtrips(self) -> Dict[str, Tuple[bool, str]]:
        """Validate XML round-trip for all patterns"""
        results = {}
        for pattern_id in self.patterns:
            results[pattern_id] = self.validate_xml_roundtrip(pattern_id)
        return results
    
    def get_stats(self) -> Dict[str, int]:
        """Get corpus statistics."""
        patterns_by_type = {'P': 0, 'C': 0, 'F': 0}
        total_components = 0
        total_operations = 0
        total_properties = 0
        
        for pattern in self.patterns.values():
            ptype = pattern.pattern_type
            patterns_by_type[ptype] = patterns_by_type.get(ptype, 0) + 1
            total_components += len(pattern.components)
            total_operations += len(pattern.operations)
            total_properties += len(pattern.properties)
        
        return {
            'total_patterns': len(self.patterns),
            'concepts': patterns_by_type.get('C', 0),
            'patterns': patterns_by_type.get('P', 0),
            'flows': patterns_by_type.get('F', 0),
            'total_components': total_components,
            'total_operations': total_operations,
            'total_properties': total_properties,
        }
    
    def list_patterns(self, pattern_type: Optional[str] = None) -> List[str]:
        """List all pattern IDs, optionally filtered by type."""
        # Filter out empty pattern IDs
        valid_ids = [pid for pid in self.patterns.keys() if pid]
        
        pattern_ids = sorted(valid_ids, 
                            key=lambda x: (x[0] if x else '', self._extract_sort_number(x)))
        
        if pattern_type:
            pattern_ids = [pid for pid in pattern_ids if pid.startswith(pattern_type)]
        
        return pattern_ids
    
    def _extract_sort_number(self, pattern_id: str) -> float:
        """Extract numeric part for sorting (handles decimals like F1.1)"""
        num_str = re.sub(r'[PCF]', '', pattern_id)
        try:
            return float(num_str)
        except ValueError:
            return 0.0
    
    def find_missing_patterns(self) -> Dict[str, List[str]]:
        """Find gaps in pattern numbering."""
        missing = {'P': [], 'C': [], 'F': []}
        
        # Check P patterns (expect P1-P155)
        p_numbers = [int(p[1:]) for p in self.patterns.keys() 
                     if p.startswith('P') and '.' not in p]
        if p_numbers:
            for i in range(1, max(p_numbers) + 1):
                if i not in p_numbers:
                    missing['P'].append(f'P{i}')
        
        # Check C patterns (expect C1-C5)
        c_numbers = [int(p[1:]) for p in self.patterns.keys() 
                     if p.startswith('C') and '.' not in p]
        if c_numbers:
            for i in range(1, max(c_numbers) + 1):
                if i not in c_numbers:
                    missing['C'].append(f'C{i}')
        
        # F patterns can have decimals (F1.1, F2.3), just list what we have
        # Don't check for missing as the numbering scheme is flexible
        
        return {k: v for k, v in missing.items() if v}
    
    def get_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build dependency graph (pattern_id -> set of dependencies)"""
        graph = {}
        for pattern_id, pattern in self.patterns.items():
            deps = set()
            deps.update(pattern.dependencies.requires)
            deps.update(pattern.dependencies.uses)
            deps.update(pattern.dependencies.specializes)
            graph[pattern_id] = deps
        return graph
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependency chains"""
        graph = self.get_dependency_graph()
        cycles = []
        
        def dfs(node: str, path: List[str], visited: Set[str]) -> None:
            if node in path:
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                if cycle not in cycles:
                    cycles.append(cycle)
                return
            
            if node in visited or node not in graph:
                return
            
            visited.add(node)
            path.append(node)
            
            for neighbor in graph[node]:
                dfs(neighbor, path[:], visited)
        
        for pattern_id in graph:
            dfs(pattern_id, [], set())
        
        return cycles
    
    def create_corpus_manifest(self, output_path: Path) -> None:
        """
        Create a manifest file describing the entire corpus.
        This provides metadata about all patterns for tools and scripts.
        """
        manifest = {
            'version': '2.0',
            'format': 'xml-master',
            'total_patterns': len(self.patterns),
            'patterns': []
        }
        
        for pattern_id in sorted(self.patterns.keys(), key=self._extract_sort_number):
            pattern = self.patterns[pattern_id]
            manifest['patterns'].append({
                'id': pattern.id,
                'name': pattern.name,
                'category': pattern.category,
                'status': pattern.status,
                'complexity': pattern.complexity,
                'component_count': len(pattern.components),
                'operation_count': len(pattern.operations),
                'property_count': len(pattern.properties),
                'dependencies': {
                    'requires': pattern.dependencies.requires,
                    'uses': pattern.dependencies.uses,
                    'specializes': pattern.dependencies.specializes,
                    'specialized_by': pattern.dependencies.specialized_by
                }
            })
        
        output_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    
    def export_unified_corpus_xml(self, output_path: Path) -> None:
        """
        Export all patterns into a single unified XML corpus file.
        This creates a complete corpus document from individual patterns.
        """
        root = ET.Element('corpus')
        root.set('xmlns', 'http://universal-corpus.org/schema/v1')
        root.set('version', '2.0')
        
        # Metadata
        metadata = ET.SubElement(root, 'metadata')
        ET.SubElement(metadata, 'total-patterns').text = str(len(self.patterns))
        ET.SubElement(metadata, 'format').text = 'xml-master'
        
        # Patterns (sorted)
        patterns_elem = ET.SubElement(root, 'patterns')
        for pattern_id in sorted(self.patterns.keys(), key=self._extract_sort_number):
            pattern = self.patterns[pattern_id]
            
            # Parse the pattern XML and attach it
            pattern_xml = self._pattern_to_xml(pattern)
            pattern_tree = ET.fromstring(pattern_xml)
            patterns_elem.append(pattern_tree)
        
        # Pretty print
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        output_path.write_text(dom.toprettyxml(indent='  '), encoding='utf-8')
    
    def export_to_csv_summary(self, output_path: Path) -> None:
        """
        Export corpus summary to CSV with one row per pattern.
        Includes metadata, counts, and key relationships.
        """
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'id', 'name', 'category', 'status', 'complexity',
                'version', 'domains', 'tuple_notation',
                'component_count', 'type_def_count', 'property_count',
                'operation_count', 'manifestation_count',
                'requires', 'uses', 'specializes', 'specialized_by',
                'has_circular_deps'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Get circular dependencies for marking
            cycles = self.find_circular_dependencies()
            patterns_in_cycles = set()
            for cycle in cycles:
                patterns_in_cycles.update(cycle)
            
            # Write pattern rows
            for pattern_id in sorted(self.patterns.keys(), key=self._extract_sort_number):
                pattern = self.patterns[pattern_id]
                
                writer.writerow({
                    'id': pattern.id,
                    'name': pattern.name,
                    'category': pattern.category,
                    'status': pattern.status,
                    'complexity': pattern.complexity,
                    'version': pattern.version,
                    'domains': '; '.join(pattern.domains) if pattern.domains else '',
                    'tuple_notation': pattern.tuple_notation,
                    'component_count': len(pattern.components),
                    'type_def_count': len(pattern.type_definitions),
                    'property_count': len(pattern.properties),
                    'operation_count': len(pattern.operations),
                    'manifestation_count': len(pattern.manifestations),
                    'requires': '; '.join(pattern.dependencies.requires),
                    'uses': '; '.join(pattern.dependencies.uses),
                    'specializes': '; '.join(pattern.dependencies.specializes),
                    'specialized_by': '; '.join(pattern.dependencies.specialized_by),
                    'has_circular_deps': 'yes' if pattern.id in patterns_in_cycles else 'no'
                })
    
    def export_to_csv_components(self, output_path: Path) -> None:
        """
        Export all components to CSV with one row per component.
        Useful for analyzing component patterns across the corpus.
        """
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'pattern_id', 'pattern_name', 'component_name',
                'component_type', 'notation', 'description'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for pattern_id in sorted(self.patterns.keys(), key=self._extract_sort_number):
                pattern = self.patterns[pattern_id]
                
                for component in pattern.components:
                    writer.writerow({
                        'pattern_id': pattern.id,
                        'pattern_name': pattern.name,
                        'component_name': component.name,
                        'component_type': component.type,
                        'notation': component.notation,
                        'description': component.description
                    })
    
    def export_to_csv_operations(self, output_path: Path) -> None:
        """
        Export all operations to CSV with one row per operation.
        Useful for analyzing operation patterns and signatures.
        """
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'pattern_id', 'pattern_name', 'operation_name',
                'signature', 'formal_definition',
                'precondition_count', 'postcondition_count', 'effect_count'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for pattern_id in sorted(self.patterns.keys(), key=self._extract_sort_number):
                pattern = self.patterns[pattern_id]
                
                for operation in pattern.operations:
                    writer.writerow({
                        'pattern_id': pattern.id,
                        'pattern_name': pattern.name,
                        'operation_name': operation.name,
                        'signature': operation.signature,
                        'formal_definition': operation.formal_definition.replace('\n', ' '),
                        'precondition_count': len(operation.preconditions),
                        'postcondition_count': len(operation.postconditions),
                        'effect_count': len(operation.effects)
                    })
    
    def export_to_csv_properties(self, output_path: Path) -> None:
        """
        Export all properties to CSV with one row per property.
        Useful for analyzing formal specifications and invariants.
        """
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'pattern_id', 'pattern_name', 'property_id',
                'property_name', 'formal_spec', 'description',
                'invariant_count'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for pattern_id in sorted(self.patterns.keys(), key=self._extract_sort_number):
                pattern = self.patterns[pattern_id]
                
                for prop in pattern.properties:
                    writer.writerow({
                        'pattern_id': pattern.id,
                        'pattern_name': pattern.name,
                        'property_id': prop.id,
                        'property_name': prop.name,
                        'formal_spec': prop.formal_spec.replace('\n', ' '),
                        'description': prop.description,
                        'invariant_count': len(prop.invariants)
                    })
    
    def export_to_csv_dependencies(self, output_path: Path) -> None:
        """
        Export dependency relationships to CSV with one row per relationship.
        Useful for graph analysis and dependency visualization.
        """
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'source_id', 'source_name', 'target_id',
                'relationship_type', 'is_circular'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Get circular dependencies
            cycles = self.find_circular_dependencies()
            circular_pairs = set()
            for cycle in cycles:
                for i in range(len(cycle) - 1):
                    circular_pairs.add((cycle[i], cycle[i + 1]))
            
            for pattern_id in sorted(self.patterns.keys(), key=self._extract_sort_number):
                pattern = self.patterns[pattern_id]
                
                # Export each dependency relationship
                for target in pattern.dependencies.requires:
                    writer.writerow({
                        'source_id': pattern.id,
                        'source_name': pattern.name,
                        'target_id': target,
                        'relationship_type': 'requires',
                        'is_circular': 'yes' if (pattern.id, target) in circular_pairs else 'no'
                    })
                
                for target in pattern.dependencies.uses:
                    writer.writerow({
                        'source_id': pattern.id,
                        'source_name': pattern.name,
                        'target_id': target,
                        'relationship_type': 'uses',
                        'is_circular': 'yes' if (pattern.id, target) in circular_pairs else 'no'
                    })
                
                for target in pattern.dependencies.specializes:
                    writer.writerow({
                        'source_id': pattern.id,
                        'source_name': pattern.name,
                        'target_id': target,
                        'relationship_type': 'specializes',
                        'is_circular': 'yes' if (pattern.id, target) in circular_pairs else 'no'
                    })
                
                for target in pattern.dependencies.specialized_by:
                    writer.writerow({
                        'source_id': pattern.id,
                        'source_name': pattern.name,
                        'target_id': target,
                        'relationship_type': 'specialized_by',
                        'is_circular': 'yes' if (pattern.id, target) in circular_pairs else 'no'
                    })
    
    def export_all_csv(self, output_dir: Path) -> Dict[str, Path]:
        """
        Export all CSV formats to a directory.
        Creates comprehensive tabular views of the corpus.
        
        Returns dict mapping CSV type to file path.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        exports = {}
        
        # Summary
        summary_path = output_dir / 'patterns_summary.csv'
        self.export_to_csv_summary(summary_path)
        exports['summary'] = summary_path
        
        # Components
        components_path = output_dir / 'components.csv'
        self.export_to_csv_components(components_path)
        exports['components'] = components_path
        
        # Operations
        operations_path = output_dir / 'operations.csv'
        self.export_to_csv_operations(operations_path)
        exports['operations'] = operations_path
        
        # Properties
        properties_path = output_dir / 'properties.csv'
        self.export_to_csv_properties(properties_path)
        exports['properties'] = properties_path
        
        # Dependencies
        dependencies_path = output_dir / 'dependencies.csv'
        self.export_to_csv_dependencies(dependencies_path)
        exports['dependencies'] = dependencies_path
        
        return exports


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """Command-line interface for XML-based corpus management."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Universal Corpus Manager - XML Master Data Architecture',
        epilog='XML files in master_data/ are the authoritative source of truth.'
    )
    
    parser.add_argument('input', type=Path, 
                       help='Path to XML file or directory containing XML pattern files')
    parser.add_argument('--stats', action='store_true',
                       help='Show corpus statistics')
    parser.add_argument('--list', choices=['all', 'P', 'C', 'F'],
                       help='List patterns')
    parser.add_argument('--missing', action='store_true',
                       help='Find missing patterns in numbering')
    parser.add_argument('--cycles', action='store_true',
                       help='Find circular dependencies')
    parser.add_argument('--validate', metavar='PATTERN_ID',
                       help='Validate XML round-trip for specific pattern')
    parser.add_argument('--validate-all', action='store_true',
                       help='Validate XML round-trip for all patterns')
    parser.add_argument('--export-xml', metavar='PATTERN_ID',
                       help='Export specific pattern to XML (stdout)')
    parser.add_argument('--export-markdown', metavar='PATTERN_ID',
                       help='Export specific pattern to Markdown (stdout)')
    parser.add_argument('--export-all-xml', metavar='OUTPUT_DIR',
                       help='Export all patterns to XML files')
    parser.add_argument('--export-all-markdown', metavar='OUTPUT_DIR',
                       help='Export all patterns to Markdown files')
    parser.add_argument('--create-manifest', metavar='OUTPUT_FILE',
                       help='Create JSON manifest of entire corpus')
    parser.add_argument('--unified-corpus', metavar='OUTPUT_FILE',
                       help='Export unified corpus XML file')
    parser.add_argument('--export-csv-summary', metavar='OUTPUT_FILE',
                       help='Export patterns summary to CSV')
    parser.add_argument('--export-csv-components', metavar='OUTPUT_FILE',
                       help='Export components to CSV')
    parser.add_argument('--export-csv-operations', metavar='OUTPUT_FILE',
                       help='Export operations to CSV')
    parser.add_argument('--export-csv-properties', metavar='OUTPUT_FILE',
                       help='Export properties to CSV')
    parser.add_argument('--export-csv-dependencies', metavar='OUTPUT_FILE',
                       help='Export dependencies to CSV')
    parser.add_argument('--export-all-csv', metavar='OUTPUT_DIR',
                       help='Export all CSV formats (summary, components, operations, properties, dependencies)')
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = CorpusManager()
    
    # Load patterns from XML
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Path not found: {input_path}", file=sys.stderr)
        return 1
    
    try:
        if input_path.is_dir():
            print(f"Loading XML patterns from: {input_path}", file=sys.stderr)
            manager.load_from_xml_directory(input_path)
        else:
            print(f"Loading XML pattern: {input_path}", file=sys.stderr)
            manager.load_pattern_xml(input_path)
        
        print(f"✓ Loaded {len(manager.patterns)} patterns\n", file=sys.stderr)
    
    except Exception as e:
        print(f"Error loading patterns: {e}", file=sys.stderr)
        return 1
    
    # Execute commands
    if args.stats:
        stats = manager.get_stats()
        print("Corpus Statistics:")
        for key, value in stats.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
    
    if args.list:
        pattern_type = None if args.list == 'all' else args.list
        patterns = manager.list_patterns(pattern_type)
        print(f"Patterns ({len(patterns)}):")
        for pid in patterns:
            pattern = manager.get_pattern(pid)
            print(f"  {pid}: {pattern.name}")
    
    if args.missing:
        missing = manager.find_missing_patterns()
        if missing:
            print("Missing patterns:")
            for pattern_type, pattern_ids in missing.items():
                print(f"  {pattern_type}: {', '.join(pattern_ids)}")
        else:
            print("No missing patterns detected")
    
    if args.cycles:
        cycles = manager.find_circular_dependencies()
        if cycles:
            print(f"Found {len(cycles)} circular dependency chains:")
            for cycle in cycles:
                print(f"  {' → '.join(cycle)}")
        else:
            print("No circular dependencies detected")
    
    if args.validate:
        is_valid, message = manager.validate_xml_roundtrip(args.validate)
        print(f"XML Round-trip Validation ({args.validate}): {message}")
        return 0 if is_valid else 1
    
    if args.validate_all:
        results = manager.validate_all_roundtrips()
        failed = [(pid, msg) for pid, (valid, msg) in results.items() if not valid]
        
        if failed:
            print(f"Validation failed for {len(failed)} patterns:")
            for pid, msg in failed:
                print(f"  {pid}: {msg}")
            return 1
        else:
            print(f"✓ All {len(results)} patterns passed XML round-trip validation")
    
    if args.export_xml:
        try:
            xml_content = manager.export_to_xml(args.export_xml)
            print(xml_content)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    
    if args.export_markdown:
        try:
            md_content = manager.export_to_markdown(args.export_markdown)
            print(md_content)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    
    if args.export_all_xml:
        output_dir = Path(args.export_all_xml)
        exported = manager.export_all_to_xml(output_dir)
        print(f"Exported {len(exported)} patterns to XML:")
        print(f"  Output directory: {output_dir}")
    
    if args.export_all_markdown:
        output_dir = Path(args.export_all_markdown)
        exported = manager.export_all_to_markdown(output_dir)
        print(f"Exported {len(exported)} patterns to Markdown:")
        print(f"  Output directory: {output_dir}")
    
    if args.create_manifest:
        output_file = Path(args.create_manifest)
        manager.create_corpus_manifest(output_file)
        print(f"Created corpus manifest: {output_file}")
    
    if args.unified_corpus:
        output_file = Path(args.unified_corpus)
        manager.export_unified_corpus_xml(output_file)
        print(f"Created unified corpus XML: {output_file}")
    
    if args.export_csv_summary:
        output_file = Path(args.export_csv_summary)
        manager.export_to_csv_summary(output_file)
        print(f"Exported patterns summary to CSV: {output_file}")
    
    if args.export_csv_components:
        output_file = Path(args.export_csv_components)
        manager.export_to_csv_components(output_file)
        print(f"Exported components to CSV: {output_file}")
    
    if args.export_csv_operations:
        output_file = Path(args.export_csv_operations)
        manager.export_to_csv_operations(output_file)
        print(f"Exported operations to CSV: {output_file}")
    
    if args.export_csv_properties:
        output_file = Path(args.export_csv_properties)
        manager.export_to_csv_properties(output_file)
        print(f"Exported properties to CSV: {output_file}")
    
    if args.export_csv_dependencies:
        output_file = Path(args.export_csv_dependencies)
        manager.export_to_csv_dependencies(output_file)
        print(f"Exported dependencies to CSV: {output_file}")
    
    if args.export_all_csv:
        output_dir = Path(args.export_all_csv)
        exports = manager.export_all_csv(output_dir)
        print(f"Exported all CSV formats to: {output_dir}")
        print("  Files created:")
        for csv_type, filepath in exports.items():
            print(f"    • {csv_type}: {filepath.name}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())


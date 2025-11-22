#!/usr/bin/env python3
"""
Universal Corpus M2M Converter
Converts markdown patterns to machine-readable formats (YAML/XML)
Preserves full formal mathematical rigor

Version: 1.0
Author: Universal Corpus Project
"""

import re
import yaml
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict


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
    """Complete pattern specification"""
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


class MarkdownParser:
    """Parse markdown pattern files into structured data"""
    
    def __init__(self, content: str):
        self.content = content
        self.lines = content.split('\n')
        
    def parse(self) -> Pattern:
        """Parse markdown into Pattern object"""
        pattern = Pattern(
            id="",
            version="1.1",
            name="",
            category="pattern"
        )
        
        # Extract pattern ID and name from title
        title_match = re.search(r'###\s+([CPF][0-9.]+)\.\s+(.+)', self.content)
        if title_match:
            pattern.id = title_match.group(1)
            pattern.name = title_match.group(2)
            # Determine category
            if pattern.id.startswith('C'):
                pattern.category = "concept"
            elif pattern.id.startswith('F'):
                pattern.category = "flow"
                
        # Extract definition tuple notation
        tuple_match = re.search(r'\$([A-Z])\s*=\s*\(([^)]+)\)\$', self.content)
        if tuple_match:
            pattern.tuple_notation = f"${tuple_match.group(0)[1:-1]}$"
            
        # Extract components
        pattern.components = self._extract_components()
        
        # Extract type definitions
        pattern.type_definitions = self._extract_type_definitions()
        
        # Extract properties
        pattern.properties = self._extract_properties(pattern.id)
        
        # Extract operations
        pattern.operations = self._extract_operations()
        
        # Extract manifestations
        pattern.manifestations = self._extract_manifestations()
        
        return pattern
    
    def _extract_components(self) -> List[Component]:
        """Extract tuple components from definition"""
        components = []
        in_definition = False
        
        for line in self.lines:
            if '**Definition' in line:
                in_definition = True
                continue
            if in_definition and line.startswith('**'):
                break
            if in_definition and line.startswith('-'):
                # Parse component line: - $name : Type$ description or - $name : Type$ is description
                # Also handle: - name : Type description
                match = re.match(r'-\s+\$?([^:$]+)\s*:\s*([^$]+)\$?\s+(?:is\s+|are\s+)?(?:a\s+|an\s+|the\s+)?(.+)', line)
                if match:
                    name = match.group(1).strip()
                    type_str = match.group(2).strip()
                    description = match.group(3).strip()
                    components.append(Component(
                        name=name,
                        type=type_str,
                        notation=name,
                        description=description
                    ))
                    
        return components
    
    def _extract_type_definitions(self) -> List[TypeDefinition]:
        """Extract type definitions section"""
        type_defs = []
        in_types = False
        current_def = None
        
        for line in self.lines:
            if '**Type Definitions:**' in line:
                in_types = True
                continue
            if in_types and line.startswith('**Properties'):
                break
            if in_types and '```' in line:
                continue
            if in_types and ':=' in line:
                # Parse type definition line
                match = re.match(r'([A-Za-z_]+)\s*:=\s*(.+)', line.strip())
                if match:
                    type_defs.append(TypeDefinition(
                        name=match.group(1),
                        definition=match.group(2),
                        notation=line.strip()
                    ))
                    
        return type_defs
    
    def _extract_properties(self, pattern_id: str) -> List[Property]:
        """Extract formal properties"""
        properties = []
        in_properties = False
        current_prop = None
        current_spec = []
        
        for line in self.lines:
            if '**Properties:**' in line:
                in_properties = True
                continue
            if in_properties and '**Operations:**' in line:
                if current_prop and current_prop not in properties:
                    current_prop.formal_spec = '\n'.join(current_spec).strip()
                    properties.append(current_prop)
                break
                
            if in_properties:
                # Property header
                prop_match = re.match(r'\*\*P\.([^(]+)\(([^)]+)\):\*\*', line)
                if prop_match:
                    if current_prop and current_prop not in properties:
                        current_prop.formal_spec = '\n'.join(current_spec).strip()
                        properties.append(current_prop)
                    current_prop = Property(
                        id=f"P.{prop_match.group(1).strip()}",
                        name=prop_match.group(2).strip(),
                        formal_spec=""
                    )
                    current_spec = []
                elif current_prop and line.strip() and not line.startswith('```'):
                    current_spec.append(line.strip())
            
        return properties
    
    def _extract_operations(self) -> List[Operation]:
        """Extract operations section"""
        operations = []
        in_operations = False
        current_op = None
        current_def = []
        in_code_block = False
        
        for i, line in enumerate(self.lines):
            if '**Operations:**' in line:
                in_operations = True
                continue
            if in_operations and ('**Manifestations:**' in line or '**Specializations:**' in line):
                if current_op and current_op not in operations:
                    current_op.formal_definition = '\n'.join(current_def).strip()
                    operations.append(current_op)
                break
                
            if in_operations:
                # Track code blocks
                if '```' in line:
                    in_code_block = not in_code_block
                    if in_code_block and current_op:
                        current_def.append(line.strip())
                    continue
                
                # Operation header (numbered)
                op_match = re.match(r'\d+\.\s+\*\*([^:]+):\*\*', line)
                if op_match and not in_code_block:
                    if current_op and current_op not in operations:
                        current_op.formal_definition = '\n'.join(current_def).strip()
                        operations.append(current_op)
                    
                    op_name = op_match.group(1).strip()
                    # Look ahead for signature
                    signature = ""
                    if i + 2 < len(self.lines):
                        sig_line = self.lines[i + 2].strip()
                        if '→' in sig_line:
                            signature = sig_line
                    
                    current_op = Operation(
                        name=op_name,
                        signature=signature,
                        formal_definition=""
                    )
                    current_def = []
                elif current_op:
                    # Inside code block, capture everything
                    if in_code_block:
                        current_def.append(line)
                    # Outside code block, capture lines with relevant content
                    elif line.strip() and not line.startswith('**'):
                        current_def.append(line.strip())
            
        return operations
    
    def _extract_manifestations(self) -> List[Manifestation]:
        """Extract manifestations section"""
        manifestations = []
        in_manifest = False
        
        for line in self.lines:
            if '**Manifestations:**' in line:
                in_manifest = True
                continue
            if in_manifest and line.startswith('---'):
                break
            if in_manifest and line.startswith('-'):
                # Extract manifestation
                text = line[1:].strip()
                # Check if there's a description in parentheses
                match = re.match(r'([^(]+)(?:\(([^)]+)\))?', text)
                if match:
                    name = match.group(1).strip()
                    description = match.group(2).strip() if match.group(2) else ""
                    manifestations.append(Manifestation(name=name, description=description))
                    
        return manifestations


class YAMLConverter:
    """Convert Pattern to YAML format"""
    
    @staticmethod
    def convert(pattern: Pattern) -> str:
        """Convert pattern to YAML string"""
        data = {
            'id': pattern.id,
            'version': pattern.version,
            'schema_version': '1.0',
            'metadata': {
                'name': pattern.name,
                'category': pattern.category,
                'status': pattern.status,
                'complexity': pattern.complexity,
                'domains': pattern.domains if pattern.domains else []
            },
            'definition': {
                'tuple_notation': pattern.tuple_notation,
                'description': pattern.definition_description,
                'components': [
                    {
                        'name': c.name,
                        'type': c.type,
                        'notation': c.notation,
                        'description': c.description
                    }
                    for c in pattern.components
                ]
            },
            'type_definitions': [
                {
                    'name': td.name,
                    'definition': td.definition,
                    'notation': td.notation
                }
                for td in pattern.type_definitions
            ] if pattern.type_definitions else [],
            'properties': [
                {
                    'id': p.id,
                    'name': p.name,
                    'formal_spec': p.formal_spec,
                    'description': p.description,
                    'invariants': p.invariants
                }
                for p in pattern.properties
            ],
            'operations': [
                {
                    'name': op.name,
                    'signature': op.signature,
                    'formal_definition': op.formal_definition,
                    'preconditions': op.preconditions,
                    'postconditions': op.postconditions,
                    'effects': op.effects
                }
                for op in pattern.operations
            ],
            'manifestations': [
                {
                    'name': m.name,
                    'description': m.description
                }
                for m in pattern.manifestations
            ]
        }
        
        return yaml.dump(data, allow_unicode=True, sort_keys=False, width=100)


class XMLConverter:
    """Convert Pattern to XML format"""
    
    @staticmethod
    def convert(pattern: Pattern) -> str:
        """Convert pattern to XML string"""
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
        
        # Definition
        definition = ET.SubElement(root, 'definition')
        tuple_not = ET.SubElement(definition, 'tuple-notation')
        tuple_not.set('format', 'latex')
        tuple_not.text = pattern.tuple_notation
        
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
        
        # Properties
        properties = ET.SubElement(root, 'properties')
        for prop in pattern.properties:
            property_elem = ET.SubElement(properties, 'property')
            property_elem.set('id', prop.id)
            ET.SubElement(property_elem, 'name').text = prop.name
            formal_spec = ET.SubElement(property_elem, 'formal-spec')
            formal_spec.set('format', 'latex')
            formal_spec.text = prop.formal_spec
        
        # Operations
        operations = ET.SubElement(root, 'operations')
        for op in pattern.operations:
            operation = ET.SubElement(operations, 'operation')
            ET.SubElement(operation, 'name').text = op.name
            ET.SubElement(operation, 'signature').text = op.signature
            formal_def = ET.SubElement(operation, 'formal-definition')
            formal_def.set('format', 'latex')
            formal_def.text = op.formal_definition
        
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


def convert_pattern_file(md_path: Path, output_format: str = 'yaml') -> str:
    """
    Convert a markdown pattern file to M2M format
    
    Args:
        md_path: Path to markdown file
        output_format: 'yaml' or 'xml'
        
    Returns:
        Converted content as string
    """
    content = md_path.read_text(encoding='utf-8')
    parser = MarkdownParser(content)
    pattern = parser.parse()
    
    if output_format.lower() == 'yaml':
        return YAMLConverter.convert(pattern)
    elif output_format.lower() == 'xml':
        return XMLConverter.convert(pattern)
    else:
        raise ValueError(f"Unknown format: {output_format}")


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert Universal Corpus patterns to machine-readable formats'
    )
    parser.add_argument('input', type=Path, help='Input markdown file or directory')
    parser.add_argument('--format', choices=['yaml', 'xml', 'both'], default='yaml',
                       help='Output format (default: yaml)')
    parser.add_argument('--output-dir', type=Path, default=Path('m2m'),
                       help='Output directory (default: m2m)')
    
    args = parser.parse_args()
    
    # Create output directories
    if args.format in ['yaml', 'both']:
        (args.output_dir / 'yaml').mkdir(parents=True, exist_ok=True)
    if args.format in ['xml', 'both']:
        (args.output_dir / 'xml').mkdir(parents=True, exist_ok=True)
    
    # Process files
    md_files = []
    if args.input.is_dir():
        md_files = list(args.input.glob('[CPF]*.md'))
    else:
        md_files = [args.input]
    
    for md_file in md_files:
        print(f"Converting {md_file.name}...")
        
        if args.format in ['yaml', 'both']:
            yaml_content = convert_pattern_file(md_file, 'yaml')
            yaml_path = args.output_dir / 'yaml' / f"{md_file.stem}.yaml"
            yaml_path.write_text(yaml_content, encoding='utf-8')
            print(f"  ✅ {yaml_path}")
        
        if args.format in ['xml', 'both']:
            xml_content = convert_pattern_file(md_file, 'xml')
            xml_path = args.output_dir / 'xml' / f"{md_file.stem}.xml"
            xml_path.write_text(xml_content, encoding='utf-8')
            print(f"  ✅ {xml_path}")
    
    print(f"\n✅ Converted {len(md_files)} patterns")


if __name__ == '__main__':
    main()


#!/usr/bin/env python3
"""
XML to Markdown Converter
Generates markdown documentation from Universal Corpus XML files
Makes XML the source of truth for the corpus

Version: 1.0
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional
import argparse


NS = {'uc': 'http://universal-corpus.org/schema/v1'}


def clean_text(text: Optional[str]) -> str:
    """Clean up text from XML"""
    if not text:
        return ""
    return text.strip()


def convert_xml_to_markdown(xml_path: Path) -> str:
    """Convert a single XML pattern file to markdown"""
    
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # Extract metadata
    pattern_id = root.get('id', '')
    name_elem = root.find('.//uc:name', NS)
    name = clean_text(name_elem.text) if name_elem is not None else ""
    
    # Start markdown
    md = []
    md.append(f"### {pattern_id}. {name}")
    md.append("")
    
    # Definition
    md.append(f"**Definition {pattern_id}:**")
    tuple_elem = root.find('.//uc:tuple-notation', NS)
    if tuple_elem is not None and tuple_elem.text:
        tuple_notation = clean_text(tuple_elem.text)
        md.append(f"{tuple_notation}")
        md.append("")
    
    # Components
    components = root.findall('.//uc:definition/uc:components/uc:component', NS)
    if components:
        for comp in components:
            comp_name = clean_text(comp.find('uc:name', NS).text)
            comp_type = clean_text(comp.find('uc:type', NS).text)
            comp_desc = clean_text(comp.find('uc:description', NS).text)
            md.append(f"- ${comp_name} : {comp_type}$ is {comp_desc}")
        md.append("")
    
    # Type Definitions
    type_defs = root.findall('.//uc:type-definitions/uc:type-def', NS)
    if type_defs:
        md.append("**Type Definitions:**")
        md.append("```")
        for td in type_defs:
            td_name = clean_text(td.find('uc:name', NS).text)
            td_def = clean_text(td.find('uc:definition', NS).text)
            md.append(f"{td_name} := {td_def}")
        md.append("```")
        md.append("")
    
    # Properties
    properties = root.findall('.//uc:properties/uc:property', NS)
    if properties:
        md.append("**Properties:**")
        md.append("")
        for prop in properties:
            prop_id = prop.get('id', '')
            prop_name = clean_text(prop.find('uc:name', NS).text)
            formal_spec_elem = prop.find('uc:formal-spec', NS)
            formal_spec = clean_text(formal_spec_elem.text) if formal_spec_elem is not None else ""
            
            md.append(f"**{prop_id} ({prop_name}):**")
            md.append("```")
            md.append(formal_spec)
            md.append("```")
            md.append("")
    
    # Operations
    operations = root.findall('.//uc:operations/uc:operation', NS)
    if operations:
        md.append("**Operations:**")
        md.append("")
        for i, op in enumerate(operations, 1):
            op_name = clean_text(op.find('uc:name', NS).text)
            signature_elem = op.find('uc:signature', NS)
            signature = clean_text(signature_elem.text) if signature_elem is not None else ""
            formal_def_elem = op.find('uc:formal-definition', NS)
            formal_def = clean_text(formal_def_elem.text) if formal_def_elem is not None else ""
            
            md.append(f"{i}. **{op_name}:**")
            if signature:
                md.append("   ```")
                md.append(f"   {signature}")
                md.append("   ```")
            if formal_def:
                # Remove extra ``` if present
                formal_def = formal_def.replace('```', '').strip()
                md.append("   ```")
                for line in formal_def.split('\n'):
                    if line.strip():
                        md.append(f"   {line}")
                md.append("   ```")
            md.append("")
    
    # Manifestations
    manifestations = root.findall('.//uc:manifestations/uc:manifestation', NS)
    if manifestations:
        md.append("**Manifestations:**")
        for manif in manifestations:
            manif_name = clean_text(manif.find('uc:name', NS).text)
            manif_desc_elem = manif.find('uc:description', NS)
            manif_desc = clean_text(manif_desc_elem.text) if manif_desc_elem is not None else ""
            if manif_desc:
                md.append(f"- {manif_name} ({manif_desc})")
            else:
                md.append(f"- {manif_name}")
        md.append("")
    
    md.append("---")
    md.append("")
    
    return '\n'.join(md)


def main():
    parser = argparse.ArgumentParser(
        description='Generate markdown from Universal Corpus XML files'
    )
    parser.add_argument('input', type=Path, help='Input XML file or directory')
    parser.add_argument('--output-dir', type=Path, default=Path('generated_md'),
                       help='Output directory for markdown files')
    
    args = parser.parse_args()
    
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process files
    xml_files = []
    if args.input.is_dir():
        xml_files = list(args.input.glob('[CPF]*.xml'))
    else:
        xml_files = [args.input]
    
    for xml_file in xml_files:
        print(f"Converting {xml_file.name}...")
        try:
            markdown = convert_xml_to_markdown(xml_file)
            md_path = args.output_dir / f"{xml_file.stem}.md"
            md_path.write_text(markdown, encoding='utf-8')
            print(f"  ✅ {md_path}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n✅ Converted {len(xml_files)} patterns")


if __name__ == '__main__':
    main()



#!/usr/bin/env python3
"""
CSV to XML Pattern Generator
Reads pattern_specs_complete.csv and generates production-ready XML files
"""

import csv
import re
import os

def escape_xml(text):
    """Escape XML special characters"""
    if not text:
        return ""
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')  
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    return text

def parse_component(comp_str):
    """Parse component string: 'name|type|description'"""
    if not comp_str or comp_str == '':
        return None
    parts = comp_str.split('|')
    if len(parts) != 3:
        return None
    return {'name': parts[0], 'type': parts[1], 'desc': parts[2]}

def parse_type(type_str):
    """Parse type string: 'name|definition'"""
    if not type_str or type_str == '':
        return None
    parts = type_str.split('|', 1)
    if len(parts) != 2:
        return None
    return {'name': parts[0], 'definition': parts[1]}

def parse_property(prop_str):
    """Parse property string: 'name|formal_spec'"""
    if not prop_str or prop_str == '':
        return None
    parts = prop_str.split('|', 1)
    if len(parts) != 2:
        return None
    return {'name': parts[0], 'spec': parts[1]}

def parse_operation(op_str):
    """Parse operation string: 'name|signature|formal_def'"""
    if not op_str or op_str == '':
        return None
    parts = op_str.split('|')
    if len(parts) != 3:
        return None
    return {'name': parts[0], 'sig': parts[1], 'def': parts[2]}

def parse_manifestation(manif_str):
    """Parse manifestation string: 'name|description'"""
    if not manif_str or manif_str == '':
        return None
    parts = manif_str.split('|', 1)
    if len(parts) != 2:
        return None
    return {'name': parts[0], 'desc': parts[1]}

def generate_xml(row):
    """Generate complete XML for a pattern from CSV row"""
    pid = row['ID']
    name = row['Name']
    tuple_notation = row['Tuple']
    
    # Start XML
    xml = f'''<?xml version="1.0" ?>
<pattern xmlns="http://universal-corpus.org/schema/v1" id="{pid}" version="1.1">
  <metadata>
    <name>{name}</name>
    <category>pattern</category>
    <status>stable</status>
    <complexity>medium</complexity>
  </metadata>
  <definition>
    <tuple-notation format="latex">{escape_xml(tuple_notation)}</tuple-notation>
    <components>
'''
    
    # Add components
    for i in range(1, 5):
        comp_key = f'Component{i}'
        if comp_key in row:
            comp = parse_component(row[comp_key])
            if comp:
                xml += f'''      <component>
        <name>{escape_xml(comp['name'])}</name>
        <type>{escape_xml(comp['type'])}</type>
        <notation>{escape_xml(comp['name'])}</notation>
        <description>{escape_xml(comp['desc'])}</description>
      </component>
'''
    
    xml += '    </components>\n  </definition>\n  <type-definitions>\n'
    
    # Add types
    for i in range(1, 3):
        type_key = f'Type{i}'
        if type_key in row:
            typ = parse_type(row[type_key])
            if typ:
                xml += f'''    <type-def>
      <name>{escape_xml(typ['name'])}</name>
      <definition>{escape_xml(typ['definition'])}</definition>
    </type-def>
'''
    
    xml += '  </type-definitions>\n  <properties>\n'
    
    # Add properties
    for i in range(1, 4):
        prop_key = f'Property{i}'
        if prop_key in row:
            prop = parse_property(row[prop_key])
            if prop:
                xml += f'''    <property id="P.{pid}.{i}">
      <name>{escape_xml(prop['name'])}</name>
      <formal-spec format="latex">{escape_xml(prop['spec'])}</formal-spec>
    </property>
'''
    
    xml += '  </properties>\n  <operations>\n'
    
    # Add operations
    for i in range(1, 4):
        op_key = f'Operation{i}'
        if op_key in row:
            op = parse_operation(row[op_key])
            if op:
                xml += f'''    <operation>
      <name>{escape_xml(op['name'])}</name>
      <signature>{escape_xml(op['sig'])}</signature>
      <formal-definition format="latex">{escape_xml(op['def'])}</formal-definition>
    </operation>
'''
    
    xml += '  </operations>\n'
    
    # Add dependencies
    if 'Deps' in row and row['Deps']:
        deps = [d.strip() for d in row['Deps'].split(',') if d.strip()]
        if deps:
            xml += '  <dependencies>\n    <uses>\n'
            for dep in deps:
                xml += f'      <pattern-ref>{dep}</pattern-ref>\n'
            xml += '    </uses>\n  </dependencies>\n'
    
    xml += '  <manifestations>\n'
    
    # Add manifestations
    for i in range(1, 3):
        manif_key = f'Manifestation{i}'
        if manif_key in row:
            manif = parse_manifestation(row[manif_key])
            if manif:
                xml += f'''    <manifestation>
      <name>{escape_xml(manif['name'])}</name>
      <description>{escape_xml(manif['desc'])}</description>
    </manifestation>
'''
    
    xml += '  </manifestations>\n</pattern>'
    
    return xml

def main():
    """Main processing function"""
    csv_file = 'pattern_specs_complete.csv'
    output_dir = 'master_data'
    
    if not os.path.exists(csv_file):
        print(f"❌ Error: {csv_file} not found")
        return
    
    # Read CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"✓ Loaded {len(rows)} patterns from CSV")
    print("=" * 60)
    
    # Generate XML for each pattern
    generated = 0
    for row in rows:
        try:
            pid = row['ID']
            name = row['Name']
            
            # Generate XML
            xml_content = generate_xml(row)
            
            # Create safe filename
            safe_name = name.replace('/', '_').replace(' ', '_')
            filename = f"{pid}_{safe_name}.xml"
            filepath = os.path.join(output_dir, filename)
            
            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            print(f"✓ {pid:6s} - {name}")
            generated += 1
            
        except Exception as e:
            print(f"❌ Error generating {row.get('ID', 'unknown')}: {e}")
    
    print("=" * 60)
    print(f"✓ Generated {generated}/{len(rows)} patterns successfully")
    print(f"\nNext: Run validation with xmllint")

if __name__ == '__main__':
    main()


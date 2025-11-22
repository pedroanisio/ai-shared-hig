#!/usr/bin/env python3
"""
Universal Corpus Formal Rigor Assessment
Analyzes cross-references, mathematical symbols, and formalism quality
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
import re

NS = {'uc': 'http://universal-corpus.org/schema/v1'}

class FormalRigorMetrics:
    """Track formal rigor metrics"""
    def __init__(self, pattern_id):
        self.pattern_id = pattern_id
        self.math_symbols = set()
        self.has_tuple_notation = False
        self.has_arrows = False
        self.has_set_notation = False
        self.has_quantifiers = False
        self.has_mappings = False
        self.cross_refs = []
        self.broken_refs = []
        self.symbol_score = 0
        self.formalism_score = 0
        self.cross_ref_score = 0

def extract_all_pattern_ids(master_data_dir):
    """Extract all valid pattern IDs from XML files"""
    valid_ids = set()
    for xml_file in Path(master_data_dir).glob('*.xml'):
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            pattern_id = root.get('id')
            if pattern_id:
                valid_ids.add(pattern_id)
        except:
            pass
    return valid_ids

def assess_mathematical_symbols(root, pattern_id):
    """Assess mathematical notation and symbols"""
    score = 0
    max_score = 30
    symbols_found = set()
    issues = []
    
    # Get all text content
    all_text = ET.tostring(root, encoding='unicode', method='text')
    
    # 1. Check for tuple notation with $ delimiters (10 points)
    tuple_elem = root.find('.//uc:tuple-notation', NS)
    if tuple_elem is not None and tuple_elem.text:
        tuple_text = tuple_elem.text
        
        if '$' in tuple_text:
            score += 5
            symbols_found.add('$...$')
        else:
            issues.append("Missing $ delimiters in tuple notation")
        
        # Check for proper tuple structure
        if re.search(r'\([^)]+\)', tuple_text):
            score += 5
            symbols_found.add('(...)')
        else:
            issues.append("Missing tuple parentheses")
    else:
        issues.append("No tuple notation")
    
    # 2. Mathematical operators (5 points)
    operators = {
        '→': 'arrow (function mapping)',
        '\\to': 'LaTeX arrow',
        '×': 'cartesian product',
        '\\times': 'LaTeX times',
        '∈': 'element of',
        '⊆': 'subset',
        '∪': 'union',
        '∩': 'intersection',
    }
    
    found_operators = 0
    for op, desc in operators.items():
        if op in all_text or op.replace('\\', '') in all_text:
            symbols_found.add(f"{op} ({desc})")
            found_operators += 1
    
    score += min(5, found_operators)
    
    # 3. Set notation (5 points)
    set_patterns = [
        r'Set⟨[^⟩]+⟩',
        r'Map⟨[^⟩]+⟩',
        r'Sequence⟨[^⟩]+⟩',
        r'\{[^}]+\}',
        r'∀',
        r'∃',
    ]
    
    set_found = sum(1 for pattern in set_patterns if re.search(pattern, all_text))
    if set_found > 0:
        score += min(5, set_found)
        symbols_found.add('Set notation')
    else:
        issues.append("No set notation found")
    
    # 4. Quantifiers and logic (5 points)
    quantifiers = ['∀', '∃', '⇒', '∧', '∨', '¬', '\\forall', '\\exists']
    quant_found = sum(1 for q in quantifiers if q in all_text)
    if quant_found > 0:
        score += min(5, quant_found)
        symbols_found.add('Quantifiers')
    else:
        issues.append("No quantifiers (∀, ∃)")
    
    # 5. Greek letters and subscripts (5 points)
    greek = ['α', 'β', 'γ', 'δ', 'ε', 'λ', 'μ', 'π', 'σ', 'τ', 'φ', 'ψ', 'ω', 'Δ', 'Σ', 'Ω']
    subscript_patterns = [r'_\{[^}]+\}', r'_[a-zA-Z0-9]+']
    
    greek_found = sum(1 for g in greek if g in all_text)
    subscript_found = sum(1 for pattern in subscript_patterns if re.search(pattern, all_text))
    
    if greek_found > 0 or subscript_found > 0:
        score += min(5, greek_found + subscript_found)
        if greek_found > 0:
            symbols_found.add('Greek letters')
        if subscript_found > 0:
            symbols_found.add('Subscripts')
    
    return score, max_score, symbols_found, issues

def assess_formal_specifications(root):
    """Assess quality of formal specifications in properties and operations"""
    score = 0
    max_score = 40
    issues = []
    
    # 1. Properties with formal specifications (20 points)
    properties = root.findall('.//uc:property', NS)
    if len(properties) > 0:
        formal_props = 0
        math_in_props = 0
        
        for prop in properties:
            formal_spec = prop.find('uc:formal-spec', NS)
            if formal_spec is not None and formal_spec.text:
                spec_text = formal_spec.text
                
                # Check length
                if len(spec_text) > 10:
                    formal_props += 1
                
                # Check for mathematical content
                if any(sym in spec_text for sym in ['→', '∀', '∃', '=', '≠', '≤', '≥', '∈', '$']):
                    math_in_props += 1
        
        # Score based on completeness
        score += (formal_props / len(properties)) * 10
        score += (math_in_props / len(properties)) * 10
        
        if formal_props < len(properties):
            issues.append(f"Only {formal_props}/{len(properties)} properties have formal specs")
        if math_in_props < len(properties):
            issues.append(f"Only {math_in_props}/{len(properties)} properties have mathematical notation")
    else:
        issues.append("No properties defined")
    
    # 2. Operations with formal definitions (20 points)
    operations = root.findall('.//uc:operation', NS)
    if len(operations) > 0:
        formal_ops = 0
        algorithmic_ops = 0
        
        for op in operations:
            formal_def = op.find('uc:formal-definition', NS)
            if formal_def is not None and formal_def.text:
                def_text = formal_def.text
                
                # Check length
                if len(def_text) > 20:
                    formal_ops += 1
                
                # Check for algorithmic content
                if any(keyword in def_text for keyword in [':=', 'return', 'if', 'for', 'while', '→', 'λ']):
                    algorithmic_ops += 1
        
        # Score based on completeness
        score += (formal_ops / len(operations)) * 10
        score += (algorithmic_ops / len(operations)) * 10
        
        if formal_ops < len(operations):
            issues.append(f"Only {formal_ops}/{len(operations)} operations have formal definitions")
        if algorithmic_ops < len(operations):
            issues.append(f"Only {algorithmic_ops}/{len(operations)} operations have algorithmic notation")
    else:
        issues.append("No operations defined")
    
    return score, max_score, issues

def assess_cross_references(root, pattern_id, valid_ids):
    """Assess cross-reference integrity"""
    score = 0
    max_score = 30
    cross_refs = []
    broken_refs = []
    issues = []
    
    # Get all text to search for pattern references
    all_text = ET.tostring(root, encoding='unicode', method='text')
    
    # 1. Check dependencies section (15 points)
    deps_section = root.find('.//uc:dependencies', NS)
    if deps_section is not None:
        score += 5  # Has dependencies section
        
        # Check pattern-ref elements
        pattern_refs = deps_section.findall('.//uc:pattern-ref', NS)
        if pattern_refs:
            score += 5  # Has explicit references
            
            all_valid = True
            for ref in pattern_refs:
                if ref.text:
                    ref_id = ref.text.strip()
                    cross_refs.append(ref_id)
                    if ref_id not in valid_ids:
                        broken_refs.append(ref_id)
                        all_valid = False
            
            if all_valid and len(pattern_refs) > 0:
                score += 5  # All references are valid
            elif broken_refs:
                issues.append(f"Broken references: {', '.join(broken_refs[:3])}")
        else:
            issues.append("Dependencies section exists but no pattern-ref elements")
    
    # 2. Check for implicit references in text (15 points)
    # Look for pattern IDs mentioned in descriptions, properties, operations
    pattern_regex = r'\b([CPF]\d+(?:\.\d+)?)\b'
    implicit_refs = set(re.findall(pattern_regex, all_text))
    
    # Remove self-reference
    implicit_refs.discard(pattern_id)
    
    if implicit_refs:
        score += 5  # Has implicit references
        
        # Check if implicit refs are documented in dependencies
        documented_refs = set(cross_refs)
        undocumented = implicit_refs - documented_refs
        
        if len(undocumented) == 0:
            score += 10  # All implicit refs are documented
        elif len(undocumented) < len(implicit_refs) / 2:
            score += 5  # Most refs documented
            issues.append(f"Undocumented refs: {', '.join(list(undocumented)[:3])}")
        else:
            issues.append(f"Many undocumented refs: {len(undocumented)}")
        
        # Add to cross_refs list
        cross_refs.extend(implicit_refs)
    
    return score, max_score, cross_refs, broken_refs, issues

def assess_type_system(root):
    """Assess type definition completeness"""
    score = 0
    max_score = 20
    issues = []
    
    type_defs = root.findall('.//uc:type-def', NS)
    
    if len(type_defs) == 0:
        issues.append("No type definitions")
        return score, max_score, issues
    
    # Score based on number and quality
    score += min(5, len(type_defs))
    
    # Check for meaningful definitions
    complete_types = 0
    for td in type_defs:
        name = td.find('uc:name', NS)
        definition = td.find('uc:definition', NS)
        
        if name is not None and definition is not None:
            if definition.text and len(definition.text) > 10:
                # Check for type constructors
                if any(sym in definition.text for sym in [':=', '|', '×', '→', 'Set', 'Map', 'Sequence']):
                    complete_types += 1
    
    score += (complete_types / len(type_defs)) * 15
    
    if complete_types < len(type_defs):
        issues.append(f"Only {complete_types}/{len(type_defs)} types have complete definitions")
    
    return score, max_score, issues

def generate_formal_rigor_report(all_metrics, valid_ids, output_file):
    """Generate comprehensive formal rigor report"""
    
    report = []
    report.append("# Universal Corpus - Formal Rigor & Cross-Reference Assessment\n")
    report.append("**Date:** November 22, 2025")
    report.append(f"**Patterns Assessed:** {len(all_metrics)}\n")
    report.append("---\n")
    
    # Calculate statistics
    total_patterns = len(all_metrics)
    
    # Mathematical symbols
    avg_symbol_score = sum(m['symbol_score'] for m in all_metrics.values()) / total_patterns
    patterns_with_good_symbols = sum(1 for m in all_metrics.values() if m['symbol_score'] >= 20)
    
    # Formal specifications
    avg_formal_score = sum(m['formalism_score'] for m in all_metrics.values()) / total_patterns
    patterns_with_good_formalism = sum(1 for m in all_metrics.values() if m['formalism_score'] >= 30)
    
    # Cross-references
    avg_crossref_score = sum(m['cross_ref_score'] for m in all_metrics.values()) / total_patterns
    patterns_with_crossrefs = sum(1 for m in all_metrics.values() if len(m['cross_refs']) > 0)
    
    # Broken references
    total_broken = sum(len(m['broken_refs']) for m in all_metrics.values())
    
    # Executive Summary
    report.append("## Executive Summary\n")
    report.append(f"**Mathematical Symbols:** {avg_symbol_score:.1f}/30 ({avg_symbol_score/30*100:.1f}%)")
    report.append(f"**Formal Specifications:** {avg_formal_score:.1f}/40 ({avg_formal_score/40*100:.1f}%)")
    report.append(f"**Cross-References:** {avg_crossref_score:.1f}/30 ({avg_crossref_score/30*100:.1f}%)")
    report.append(f"**Broken References:** {total_broken} total\n")
    
    # Category Scores
    report.append("---\n")
    report.append("## Category Analysis\n")
    
    report.append("### 1. Mathematical Symbols & Notation\n")
    report.append(f"- **Average Score:** {avg_symbol_score:.1f}/30 ({avg_symbol_score/30*100:.1f}%)")
    report.append(f"- **Patterns with Good Symbols (≥20/30):** {patterns_with_good_symbols} ({patterns_with_good_symbols/total_patterns*100:.1f}%)")
    
    # Most common symbols
    all_symbols = defaultdict(int)
    for m in all_metrics.values():
        for sym in m['symbols']:
            all_symbols[sym] += 1
    
    report.append("\n**Most Common Symbols:**")
    for sym, count in sorted(all_symbols.items(), key=lambda x: x[1], reverse=True)[:10]:
        report.append(f"- {sym}: {count} patterns ({count/total_patterns*100:.1f}%)")
    
    report.append("\n### 2. Formal Specifications Quality\n")
    report.append(f"- **Average Score:** {avg_formal_score:.1f}/40 ({avg_formal_score/40*100:.1f}%)")
    report.append(f"- **Patterns with Strong Formalism (≥30/40):** {patterns_with_good_formalism} ({patterns_with_good_formalism/total_patterns*100:.1f}%)")
    
    report.append("\n### 3. Cross-Reference Integrity\n")
    report.append(f"- **Average Score:** {avg_crossref_score:.1f}/30 ({avg_crossref_score/30*100:.1f}%)")
    report.append(f"- **Patterns with Cross-Refs:** {patterns_with_crossrefs} ({patterns_with_crossrefs/total_patterns*100:.1f}%)")
    report.append(f"- **Total Broken References:** {total_broken}")
    
    if total_broken > 0:
        report.append("\n**⚠️ Broken References Found:**")
        for pid, m in all_metrics.items():
            if m['broken_refs']:
                report.append(f"- {pid}: {', '.join(m['broken_refs'])}")
    
    # Reference network
    report.append("\n### 4. Pattern Reference Network\n")
    
    # Most referenced patterns
    ref_counts = defaultdict(int)
    for m in all_metrics.values():
        for ref in m['cross_refs']:
            if ref in valid_ids:
                ref_counts[ref] += 1
    
    report.append("**Most Referenced Patterns:**")
    for pattern, count in sorted(ref_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
        report.append(f"- {pattern}: referenced by {count} patterns")
    
    # Patterns with most outgoing refs
    outgoing = [(pid, len(m['cross_refs'])) for pid, m in all_metrics.items()]
    outgoing.sort(key=lambda x: x[1], reverse=True)
    
    report.append("\n**Patterns Referencing Most Others:**")
    for pattern, count in outgoing[:15]:
        if count > 0:
            report.append(f"- {pattern}: references {count} patterns")
    
    # Detailed scores by category
    report.append("\n---\n")
    report.append("## Detailed Scores by Category\n")
    
    # Traditional vs AI-native
    traditional = {pid: m for pid, m in all_metrics.items() 
                   if pid.startswith(('C', 'F')) or (pid.startswith('P') and int(re.search(r'\d+', pid).group()) <= 63)}
    ai_native = {pid: m for pid, m in all_metrics.items() 
                 if pid.startswith('P') and int(re.search(r'\d+', pid).group()) >= 64}
    
    report.append("\n### Traditional Patterns (C, F, P1-P63)\n")
    if traditional:
        avg_sym = sum(m['symbol_score'] for m in traditional.values()) / len(traditional)
        avg_form = sum(m['formalism_score'] for m in traditional.values()) / len(traditional)
        avg_xref = sum(m['cross_ref_score'] for m in traditional.values()) / len(traditional)
        
        report.append(f"- **Count:** {len(traditional)}")
        report.append(f"- **Symbols:** {avg_sym:.1f}/30 ({avg_sym/30*100:.1f}%)")
        report.append(f"- **Formalism:** {avg_form:.1f}/40 ({avg_form/40*100:.1f}%)")
        report.append(f"- **Cross-Refs:** {avg_xref:.1f}/30 ({avg_xref/30*100:.1f}%)")
    
    report.append("\n### AI-Native Patterns (P64-P155)\n")
    if ai_native:
        avg_sym = sum(m['symbol_score'] for m in ai_native.values()) / len(ai_native)
        avg_form = sum(m['formalism_score'] for m in ai_native.values()) / len(ai_native)
        avg_xref = sum(m['cross_ref_score'] for m in ai_native.values()) / len(ai_native)
        
        report.append(f"- **Count:** {len(ai_native)}")
        report.append(f"- **Symbols:** {avg_sym:.1f}/30 ({avg_sym/30*100:.1f}%)")
        report.append(f"- **Formalism:** {avg_form:.1f}/40 ({avg_form/40*100:.1f}%)")
        report.append(f"- **Cross-Refs:** {avg_xref:.1f}/30 ({avg_xref/30*100:.1f}%)")
    
    # Patterns needing improvement
    report.append("\n---\n")
    report.append("## Patterns Needing Formal Rigor Improvement\n")
    
    weak_formalism = [(pid, m) for pid, m in all_metrics.items() 
                      if m['formalism_score'] < 20 or m['symbol_score'] < 15]
    weak_formalism.sort(key=lambda x: x[1]['formalism_score'] + x[1]['symbol_score'])
    
    if weak_formalism:
        for pid, m in weak_formalism[:20]:
            report.append(f"\n### {pid}")
            report.append(f"- **Symbols:** {m['symbol_score']:.1f}/30")
            report.append(f"- **Formalism:** {m['formalism_score']:.1f}/40")
            if m['issues']:
                report.append(f"- **Issues:** {'; '.join(m['issues'][:3])}")
    else:
        report.append("✅ All patterns have adequate formal rigor!\n")
    
    # Write report
    Path(output_file).write_text('\n'.join(report))

def main():
    """Main execution"""
    master_data_dir = Path('master_data')
    output_file = 'FORMAL_RIGOR_REPORT.md'
    
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║      FORMAL RIGOR & CROSS-REFERENCE ASSESSMENT                ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    # Get all valid pattern IDs
    print("📊 Loading pattern IDs...")
    valid_ids = extract_all_pattern_ids(master_data_dir)
    print(f"✅ Found {len(valid_ids)} valid patterns\n")
    
    print("🔍 Assessing formal rigor...\n")
    
    all_metrics = {}
    
    for xml_file in sorted(master_data_dir.glob('*.xml')):
        pattern_id = xml_file.stem.split('_')[0]
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
        except:
            continue
        
        metrics = {}
        
        # Assess mathematical symbols
        sym_score, sym_max, symbols, sym_issues = assess_mathematical_symbols(root, pattern_id)
        metrics['symbol_score'] = sym_score
        metrics['symbols'] = symbols
        
        # Assess formal specifications
        form_score, form_max, form_issues = assess_formal_specifications(root)
        metrics['formalism_score'] = form_score
        
        # Assess type system
        type_score, type_max, type_issues = assess_type_system(root)
        metrics['type_score'] = type_score
        
        # Assess cross-references
        xref_score, xref_max, cross_refs, broken_refs, xref_issues = assess_cross_references(root, pattern_id, valid_ids)
        metrics['cross_ref_score'] = xref_score
        metrics['cross_refs'] = cross_refs
        metrics['broken_refs'] = broken_refs
        
        # Combine issues
        metrics['issues'] = sym_issues + form_issues + type_issues + xref_issues
        
        all_metrics[pattern_id] = metrics
        
        # Progress indicator
        total_score = sym_score + form_score + xref_score + type_score
        max_total = sym_max + form_max + xref_max + type_max
        pct = (total_score / max_total * 100) if max_total > 0 else 0
        
        status = '✅' if pct >= 70 else '⚠️' if pct >= 50 else '❌'
        print(f"{status} {pattern_id}: {pct:.1f}% (Sym:{sym_score}/{sym_max}, Form:{form_score}/{form_max}, XRef:{xref_score}/{xref_max})")
    
    print(f"\n{'='*68}")
    print("📝 Generating formal rigor report...")
    
    generate_formal_rigor_report(all_metrics, valid_ids, output_file)
    
    print(f"✅ Report generated: {output_file}")
    print(f"{'='*68}")

if __name__ == '__main__':
    main()


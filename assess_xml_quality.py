#!/usr/bin/env python3
"""
Universal Corpus XML Quality Assessment Tool
Scores each pattern and generates comprehensive quality report
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
import re

NS = {'uc': 'http://universal-corpus.org/schema/v1'}

class QualityMetrics:
    """Track quality metrics for a pattern"""
    def __init__(self, pattern_id):
        self.pattern_id = pattern_id
        self.scores = {}
        self.issues = []
        self.warnings = []
        self.total_score = 0
    
    def add_score(self, category, score, max_score, note=""):
        self.scores[category] = (score, max_score)
        if note:
            if score < max_score * 0.7:
                self.issues.append(f"{category}: {note}")
            elif score < max_score:
                self.warnings.append(f"{category}: {note}")
    
    def calculate_total(self):
        total_earned = sum(s[0] for s in self.scores.values())
        total_possible = sum(s[1] for s in self.scores.values())
        self.total_score = (total_earned / total_possible * 100) if total_possible > 0 else 0
        return self.total_score

def assess_metadata(root):
    """Assess metadata completeness and quality"""
    score = 0
    max_score = 10
    issues = []
    
    metadata = root.find('.//uc:metadata', NS)
    if metadata is None:
        issues.append("Missing metadata section")
        return score, max_score, issues
    
    # Check required fields
    required = ['name', 'category', 'status', 'complexity']
    present = 0
    for field in required:
        elem = metadata.find(f'uc:{field}', NS)
        if elem is not None and elem.text and elem.text.strip():
            present += 1
            score += 2
        else:
            issues.append(f"Missing or empty {field}")
    
    # Check version
    version = root.get('version')
    if version and version == '1.1':
        score += 2
    else:
        issues.append(f"Invalid version: {version}")
    
    return score, max_score, issues

def assess_definition(root):
    """Assess definition quality and formal rigor"""
    score = 0
    max_score = 30
    issues = []
    
    definition = root.find('.//uc:definition', NS)
    if definition is None:
        issues.append("Missing definition section")
        return score, max_score, issues
    
    # 1. Tuple notation (15 points)
    tuple_elem = definition.find('uc:tuple-notation', NS)
    if tuple_elem is not None and tuple_elem.text:
        tuple_text = tuple_elem.text.strip()
        
        # Check for mathematical notation
        if '$' in tuple_text:
            score += 5
        else:
            issues.append("Tuple notation missing $ delimiters")
        
        # Check for tuple structure (parentheses)
        if '(' in tuple_text and ')' in tuple_text:
            score += 5
        else:
            issues.append("Tuple notation missing parentheses")
        
        # Check for mapping notation (→, :, etc.)
        if any(sym in tuple_text for sym in ['→', '\\to', ':', '×', '\\times']):
            score += 5
        else:
            issues.append("Tuple notation missing type mappings")
    else:
        issues.append("Empty or missing tuple notation")
    
    # 2. Components (10 points)
    components = definition.findall('.//uc:component', NS)
    if len(components) > 0:
        score += 5
        # Check component completeness
        complete_components = 0
        for comp in components:
            name = comp.find('uc:name', NS)
            comp_type = comp.find('uc:type', NS)
            desc = comp.find('uc:description', NS)
            if all(e is not None and e.text for e in [name, comp_type, desc]):
                complete_components += 1
        
        if complete_components == len(components):
            score += 5
        else:
            issues.append(f"Only {complete_components}/{len(components)} components fully specified")
    else:
        issues.append("No components defined")
    
    # 3. Type definitions (5 points)
    type_defs = definition.findall('.//uc:type-def', NS)
    if len(type_defs) > 0:
        score += 3
        # Check for meaningful type definitions
        meaningful = sum(1 for td in type_defs 
                        if td.find('uc:definition', NS) is not None 
                        and len(td.find('uc:definition', NS).text or '') > 20)
        if meaningful == len(type_defs):
            score += 2
    else:
        issues.append("No type definitions")
    
    return score, max_score, issues

def assess_properties(root):
    """Assess property quality"""
    score = 0
    max_score = 20
    issues = []
    
    properties = root.findall('.//uc:property', NS)
    
    if len(properties) == 0:
        issues.append("No properties defined")
        return score, max_score, issues
    
    # Expect at least 3 properties
    if len(properties) >= 3:
        score += 5
    else:
        issues.append(f"Only {len(properties)} properties (expected 3+)")
        score += len(properties) * 1.5
    
    # Check property completeness
    complete = 0
    has_formal_spec = 0
    
    for prop in properties:
        prop_id = prop.get('id')
        name = prop.find('uc:name', NS)
        formal_spec = prop.find('uc:formal-spec', NS)
        
        if prop_id and name is not None and name.text:
            complete += 1
        
        if formal_spec is not None and formal_spec.text and len(formal_spec.text) > 10:
            has_formal_spec += 1
    
    # Score completeness (10 points)
    if complete == len(properties):
        score += 10
    else:
        score += (complete / len(properties)) * 10
        issues.append(f"Only {complete}/{len(properties)} properties complete")
    
    # Score formal specifications (5 points)
    if has_formal_spec == len(properties):
        score += 5
    else:
        score += (has_formal_spec / len(properties)) * 5
        if has_formal_spec == 0:
            issues.append("No properties have formal specifications")
    
    return score, max_score, issues

def assess_operations(root):
    """Assess operation quality"""
    score = 0
    max_score = 20
    issues = []
    
    operations = root.findall('.//uc:operation', NS)
    
    if len(operations) == 0:
        issues.append("No operations defined")
        return score, max_score, issues
    
    # Expect at least 3 operations
    if len(operations) >= 3:
        score += 5
    else:
        issues.append(f"Only {len(operations)} operations (expected 3+)")
        score += len(operations) * 1.5
    
    # Check operation completeness
    has_name = 0
    has_signature = 0
    has_formal_def = 0
    
    for op in operations:
        name = op.find('uc:name', NS)
        signature = op.find('uc:signature', NS)
        formal_def = op.find('uc:formal-definition', NS)
        
        if name is not None and name.text:
            has_name += 1
        
        if signature is not None and signature.text and len(signature.text) > 5:
            has_signature += 1
        
        if formal_def is not None and formal_def.text and len(formal_def.text) > 20:
            has_formal_def += 1
    
    # Score components (5 points each)
    score += (has_name / len(operations)) * 5
    score += (has_signature / len(operations)) * 5
    score += (has_formal_def / len(operations)) * 5
    
    if has_signature < len(operations):
        issues.append(f"Only {has_signature}/{len(operations)} operations have signatures")
    
    if has_formal_def < len(operations):
        issues.append(f"Only {has_formal_def}/{len(operations)} operations have formal definitions")
    
    return score, max_score, issues

def assess_manifestations(root):
    """Assess manifestation examples"""
    score = 0
    max_score = 10
    issues = []
    
    manifestations = root.findall('.//uc:manifestation', NS)
    
    if len(manifestations) == 0:
        issues.append("No manifestations defined")
        return score, max_score, issues
    
    # Expect at least 3 manifestations
    if len(manifestations) >= 3:
        score += 5
    else:
        score += len(manifestations) * 1.5
    
    # Check for meaningful descriptions
    with_desc = sum(1 for m in manifestations 
                   if m.find('uc:description', NS) is not None 
                   and len(m.find('uc:description', NS).text or '') > 5)
    
    score += (with_desc / len(manifestations)) * 5
    
    if with_desc < len(manifestations):
        issues.append(f"Only {with_desc}/{len(manifestations)} manifestations have descriptions")
    
    return score, max_score, issues

def assess_consistency(root, pattern_id):
    """Assess naming and structural consistency"""
    score = 0
    max_score = 10
    issues = []
    
    # Check ID consistency
    xml_id = root.get('id')
    if xml_id == pattern_id:
        score += 3
    else:
        issues.append(f"ID mismatch: file={pattern_id}, xml={xml_id}")
    
    # Check property ID format
    properties = root.findall('.//uc:property', NS)
    correct_format = 0
    for prop in properties:
        prop_id = prop.get('id')
        if prop_id:
            # Should be P.{PatternID}.{Number}
            if re.match(rf'P\.{pattern_id}\.\d+', prop_id):
                correct_format += 1
    
    if len(properties) > 0:
        score += (correct_format / len(properties)) * 4
        if correct_format < len(properties):
            issues.append(f"Only {correct_format}/{len(properties)} properties follow ID convention")
    
    # Check namespace usage
    if root.get('xmlns') == 'http://universal-corpus.org/schema/v1':
        score += 3
    else:
        issues.append("Missing or incorrect namespace")
    
    return score, max_score, issues

def assess_pattern(xml_file):
    """Assess a single pattern"""
    pattern_id = xml_file.stem.split('_')[0]
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except Exception as e:
        metrics = QualityMetrics(pattern_id)
        metrics.issues.append(f"XML parse error: {e}")
        return metrics
    
    metrics = QualityMetrics(pattern_id)
    
    # Run assessments
    score, max_s, issues = assess_metadata(root)
    metrics.add_score("Metadata", score, max_s, "; ".join(issues) if issues else "")
    
    score, max_s, issues = assess_definition(root)
    metrics.add_score("Definition", score, max_s, "; ".join(issues) if issues else "")
    
    score, max_s, issues = assess_properties(root)
    metrics.add_score("Properties", score, max_s, "; ".join(issues) if issues else "")
    
    score, max_s, issues = assess_operations(root)
    metrics.add_score("Operations", score, max_s, "; ".join(issues) if issues else "")
    
    score, max_s, issues = assess_manifestations(root)
    metrics.add_score("Manifestations", score, max_s, "; ".join(issues) if issues else "")
    
    score, max_s, issues = assess_consistency(root, pattern_id)
    metrics.add_score("Consistency", score, max_s, "; ".join(issues) if issues else "")
    
    metrics.calculate_total()
    
    return metrics

def generate_report(all_metrics, output_file):
    """Generate comprehensive quality report"""
    
    # Calculate statistics
    total_patterns = len(all_metrics)
    scores = [m.total_score for m in all_metrics]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    # Grade distribution
    grades = defaultdict(list)
    for m in all_metrics:
        if m.total_score >= 90:
            grades['A'].append(m.pattern_id)
        elif m.total_score >= 80:
            grades['B'].append(m.pattern_id)
        elif m.total_score >= 70:
            grades['C'].append(m.pattern_id)
        elif m.total_score >= 60:
            grades['D'].append(m.pattern_id)
        else:
            grades['F'].append(m.pattern_id)
    
    # Category scores
    category_scores = defaultdict(list)
    for m in all_metrics:
        for category, (score, max_score) in m.scores.items():
            category_scores[category].append(score / max_score * 100)
    
    # Generate report
    report = []
    report.append("# Universal Corpus XML Quality Assessment Report")
    report.append(f"\n**Date:** November 22, 2025")
    report.append(f"**Patterns Assessed:** {total_patterns}")
    report.append(f"**Average Score:** {avg_score:.1f}/100")
    report.append(f"\n---\n")
    
    # Executive Summary
    report.append("## Executive Summary\n")
    report.append(f"The Universal Corpus contains {total_patterns} patterns with an average quality score of **{avg_score:.1f}/100**.\n")
    
    # Grade distribution
    report.append("### Grade Distribution\n")
    report.append("| Grade | Count | Percentage | Patterns |")
    report.append("|-------|-------|------------|----------|")
    for grade in ['A', 'B', 'C', 'D', 'F']:
        count = len(grades[grade])
        pct = count / total_patterns * 100 if total_patterns > 0 else 0
        pattern_list = ", ".join(grades[grade][:5])
        if count > 5:
            pattern_list += f" (+{count-5} more)"
        report.append(f"| {grade} (90-100) | {count} | {pct:.1f}% | {pattern_list} |" if grade == 'A' else
                     f"| {grade} | {count} | {pct:.1f}% | {pattern_list} |")
    
    report.append(f"\n---\n")
    
    # Category Analysis
    report.append("## Category Quality Scores\n")
    report.append("| Category | Average Score | Status |")
    report.append("|----------|---------------|--------|")
    for category, scores in sorted(category_scores.items()):
        avg = sum(scores) / len(scores)
        status = "✅ Excellent" if avg >= 90 else "✅ Good" if avg >= 80 else "⚠️ Needs Work" if avg >= 70 else "❌ Critical"
        report.append(f"| {category} | {avg:.1f}% | {status} |")
    
    report.append(f"\n---\n")
    
    # Top Issues
    report.append("## Most Common Issues\n")
    all_issues = []
    for m in all_metrics:
        all_issues.extend(m.issues)
    
    issue_counts = defaultdict(int)
    for issue in all_issues:
        # Extract issue type
        issue_type = issue.split(':')[0] if ':' in issue else issue
        issue_counts[issue_type] += 1
    
    report.append("| Issue | Occurrences |")
    report.append("|-------|-------------|")
    for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        report.append(f"| {issue} | {count} |")
    
    report.append(f"\n---\n")
    
    # Detailed Pattern Scores
    report.append("## Pattern Scores (Sorted by Quality)\n")
    sorted_metrics = sorted(all_metrics, key=lambda m: m.total_score, reverse=True)
    
    report.append("| Pattern | Score | Grade | Key Issues |")
    report.append("|---------|-------|-------|------------|")
    for m in sorted_metrics[:30]:  # Top 30
        grade = 'A' if m.total_score >= 90 else 'B' if m.total_score >= 80 else 'C' if m.total_score >= 70 else 'D' if m.total_score >= 60 else 'F'
        issues = "; ".join(m.issues[:2]) if m.issues else "None"
        if len(issues) > 80:
            issues = issues[:77] + "..."
        report.append(f"| {m.pattern_id} | {m.total_score:.1f} | {grade} | {issues} |")
    
    if len(sorted_metrics) > 30:
        report.append(f"| ... | ... | ... | ... |")
        report.append(f"| ({len(sorted_metrics) - 30} more patterns) | | | |")
    
    report.append(f"\n---\n")
    
    # Patterns Needing Attention
    report.append("## Patterns Needing Attention (Score < 70)\n")
    low_scores = [m for m in sorted_metrics if m.total_score < 70]
    
    if low_scores:
        for m in low_scores:
            report.append(f"\n### {m.pattern_id} (Score: {m.total_score:.1f})\n")
            report.append("**Issues:**")
            for issue in m.issues:
                report.append(f"- {issue}")
            report.append("")
    else:
        report.append("✅ **No patterns below 70%**\n")
    
    report.append(f"\n---\n")
    
    # Recommendations
    report.append("## Recommendations\n")
    report.append(f"1. **High Priority:** Fix {len([m for m in all_metrics if m.total_score < 70])} patterns scoring below 70%")
    report.append(f"2. **Medium Priority:** Enhance {len([m for m in all_metrics if 70 <= m.total_score < 85])} patterns scoring 70-85%")
    report.append(f"3. **Low Priority:** Polish {len([m for m in all_metrics if 85 <= m.total_score < 90])} patterns scoring 85-90%")
    report.append(f"4. **Maintain:** {len([m for m in all_metrics if m.total_score >= 90])} patterns scoring 90+% are excellent")
    
    # Write report
    output_path = Path(output_file)
    output_path.write_text('\n'.join(report))
    
    return avg_score, grades

def main():
    """Main execution"""
    master_data_dir = Path('master_data')
    output_file = 'XML_QUALITY_REPORT.md'
    
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║         UNIVERSAL CORPUS XML QUALITY ASSESSMENT                ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    if not master_data_dir.exists():
        print(f"❌ Error: {master_data_dir} not found")
        return
    
    xml_files = sorted(master_data_dir.glob('*.xml'))
    print(f"📊 Assessing {len(xml_files)} XML patterns...\n")
    
    all_metrics = []
    for xml_file in xml_files:
        metrics = assess_pattern(xml_file)
        all_metrics.append(metrics)
        
        # Progress indicator
        grade = '✅' if metrics.total_score >= 80 else '⚠️' if metrics.total_score >= 70 else '❌'
        print(f"{grade} {metrics.pattern_id}: {metrics.total_score:.1f}/100")
    
    print(f"\n{'='*68}")
    print("📝 Generating quality report...")
    
    avg_score, grades = generate_report(all_metrics, output_file)
    
    print(f"✅ Report generated: {output_file}")
    print(f"\n📊 Summary:")
    print(f"   Average Score: {avg_score:.1f}/100")
    print(f"   Grade A (90+): {len(grades['A'])} patterns")
    print(f"   Grade B (80-89): {len(grades['B'])} patterns")
    print(f"   Grade C (70-79): {len(grades['C'])} patterns")
    print(f"   Grade D (60-69): {len(grades['D'])} patterns")
    print(f"   Grade F (<60): {len(grades['F'])} patterns")
    print(f"{'='*68}")

if __name__ == '__main__':
    main()


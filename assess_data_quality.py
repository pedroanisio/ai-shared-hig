#!/usr/bin/env python3
"""
Data Quality Assessment for Universal Corpus Pattern Database

This script performs comprehensive quality analysis following production-ready principles:
- No placeholders or incomplete analysis
- Root cause identification for quality issues
- Production-ready reporting with actionable insights
"""

import sys
import json
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal, PatternRepository, init_db
from models import Pattern, CategoryType, StatusType, ComplexityType


class DataQualityAssessor:
    """Comprehensive data quality assessment for pattern database."""
    
    def __init__(self):
        """Initialize database connection."""
        init_db()
        self.db = SessionLocal()
        self.repo = PatternRepository(self.db)
        self.issues = defaultdict(list)
        self.stats = defaultdict(int)
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
    
    def assess_all(self) -> Dict[str, Any]:
        """Run complete quality assessment."""
        patterns = self.repo.list(limit=10000)
        
        print(f"📊 Assessing {len(patterns)} patterns...")
        
        for pattern in patterns:
            self.assess_pattern(pattern)
        
        return self.generate_report()
    
    def assess_pattern(self, pattern: Pattern) -> None:
        """Assess individual pattern for quality issues."""
        pid = pattern.id
        
        # 1. METADATA QUALITY
        self.check_metadata(pid, pattern.metadata)
        
        # 2. DEFINITION QUALITY
        self.check_definition(pid, pattern.definition)
        
        # 3. TYPE DEFINITIONS QUALITY
        self.check_type_definitions(pid, pattern.type_definitions)
        
        # 4. PROPERTIES QUALITY
        self.check_properties(pid, pattern.properties)
        
        # 5. OPERATIONS QUALITY
        self.check_operations(pid, pattern.operations)
        
        # 6. DEPENDENCIES QUALITY
        self.check_dependencies(pid, pattern.dependencies)
        
        # 7. MANIFESTATIONS QUALITY
        self.check_manifestations(pid, pattern.manifestations)
        
        # 8. CROSS-FIELD CONSISTENCY
        self.check_consistency(pid, pattern)
    
    def check_metadata(self, pid: str, metadata: Any) -> None:
        """Check metadata quality."""
        if not metadata:
            self.issues['critical'].append(f"{pid}: Missing metadata")
            return
        
        # Check required fields
        if not metadata.name or metadata.name.strip() == "":
            self.issues['critical'].append(f"{pid}: Empty or missing name")
        
        # Check for generic/placeholder names
        if metadata.name and any(placeholder in metadata.name.lower() for placeholder in 
                                ['pattern f', 'pattern p', 'tbd', 'todo', 'unnamed']):
            self.issues['warning'].append(f"{pid}: Generic/placeholder name: '{metadata.name}'")
            self.stats['generic_names'] += 1
        
        # Check category validity
        if not metadata.category:
            self.issues['critical'].append(f"{pid}: Missing category")
        
        # Check for missing domains
        if not metadata.domains or not metadata.domains.domain:
            self.issues['minor'].append(f"{pid}: Missing domain classification")
            self.stats['missing_domains'] += 1
        
        # Check if last_updated is None (all should have update tracking)
        if metadata.last_updated is None:
            self.stats['missing_timestamps'] += 1
    
    def check_definition(self, pid: str, definition: Any) -> None:
        """Check definition quality."""
        if not definition:
            self.issues['critical'].append(f"{pid}: Missing definition")
            return
        
        # Check tuple notation
        if not definition.tuple_notation or not definition.tuple_notation.content:
            self.issues['warning'].append(f"{pid}: Missing tuple notation")
            self.stats['missing_tuple_notation'] += 1
        elif definition.tuple_notation.content.strip() == "":
            self.issues['warning'].append(f"{pid}: Empty tuple notation")
        
        # Check components
        if not definition.components or not definition.components.component:
            self.issues['warning'].append(f"{pid}: No components defined")
            self.stats['missing_components'] += 1
        else:
            for idx, comp in enumerate(definition.components.component):
                if not comp.name or comp.name.strip() == "":
                    self.issues['critical'].append(f"{pid}: Component #{idx} has no name")
                if not comp.type or comp.type.strip() == "":
                    self.issues['warning'].append(f"{pid}: Component '{comp.name}' missing type")
                    self.stats['components_missing_type'] += 1
                if not comp.description or comp.description.strip() == "":
                    self.issues['minor'].append(f"{pid}: Component '{comp.name}' missing description")
                    self.stats['components_missing_description'] += 1
    
    def check_type_definitions(self, pid: str, type_defs: Any) -> None:
        """Check type definitions quality."""
        if not type_defs or not type_defs.type_def:
            # Type definitions are optional, only note for statistics
            self.stats['no_type_definitions'] += 1
            return
        
        for typedef in type_defs.type_def:
            if not typedef.name or typedef.name.strip() == "":
                self.issues['critical'].append(f"{pid}: Type definition without name")
            
            if not typedef.definition or not typedef.definition.content:
                self.issues['warning'].append(f"{pid}: Type '{typedef.name}' has empty definition")
                self.stats['empty_type_definitions'] += 1
            elif typedef.definition.content.strip() == "":
                self.issues['warning'].append(f"{pid}: Type '{typedef.name}' has empty definition content")
    
    def check_properties(self, pid: str, properties: Any) -> None:
        """Check properties quality."""
        if not properties or not properties.property:
            self.issues['warning'].append(f"{pid}: No properties defined")
            self.stats['no_properties'] += 1
            return
        
        for prop in properties.property:
            if not prop.id or prop.id.strip() == "":
                self.issues['critical'].append(f"{pid}: Property without ID")
            
            if not prop.name or prop.name.strip() == "":
                self.issues['critical'].append(f"{pid}: Property {prop.id} without name")
            
            # Check formal specification
            if not prop.formal_spec or not prop.formal_spec.content:
                self.issues['warning'].append(f"{pid}: Property {prop.id} missing formal spec")
                self.stats['properties_missing_formal_spec'] += 1
            elif prop.formal_spec.content.strip() == "":
                self.issues['warning'].append(f"{pid}: Property {prop.id} has empty formal spec")
            
            # Check for incomplete/truncated specs
            if prop.formal_spec and prop.formal_spec.content:
                content = prop.formal_spec.content.strip()
                if content.endswith('→') or content.endswith('⇒') or content.endswith('|'):
                    self.issues['critical'].append(f"{pid}: Property {prop.id} appears truncated: '{content[-50:]}'")
                    self.stats['truncated_properties'] += 1
    
    def check_operations(self, pid: str, operations: Any) -> None:
        """Check operations quality."""
        if not operations or not operations.operation:
            self.issues['warning'].append(f"{pid}: No operations defined")
            self.stats['no_operations'] += 1
            return
        
        for op in operations.operation:
            if not op.name or op.name.strip() == "":
                self.issues['critical'].append(f"{pid}: Operation without name")
                continue
            
            # Check signature
            if not op.signature or op.signature.strip() == "":
                self.issues['critical'].append(f"{pid}: Operation '{op.name}' missing signature")
                self.stats['operations_missing_signature'] += 1
            else:
                # Check for truncated signatures
                sig = op.signature.strip()
                if sig.endswith('→') or sig.endswith(':') or (sig.count('(') != sig.count(')')):
                    self.issues['critical'].append(f"{pid}: Operation '{op.name}' has truncated signature: '{sig}'")
                    self.stats['truncated_signatures'] += 1
            
            # Check formal definition
            if not op.formal_definition or not op.formal_definition.content:
                self.issues['warning'].append(f"{pid}: Operation '{op.name}' missing formal definition")
                self.stats['operations_missing_formal_def'] += 1
            elif op.formal_definition.content.strip() == "":
                self.issues['warning'].append(f"{pid}: Operation '{op.name}' has empty formal definition")
                self.stats['operations_empty_formal_def'] += 1
    
    def check_dependencies(self, pid: str, dependencies: Any) -> None:
        """Check dependencies quality."""
        # Dependencies are optional, but patterns should have them
        if not dependencies:
            # Only flag for non-concept patterns
            if not pid.startswith('C'):
                self.stats['no_dependencies'] += 1
        else:
            # Check if all dependency fields are empty
            has_any = False
            if dependencies.requires or dependencies.uses or dependencies.specializes or dependencies.specialized_by:
                has_any = True
            if not has_any and not pid.startswith('C'):
                self.stats['empty_dependencies'] += 1
    
    def check_manifestations(self, pid: str, manifestations: Any) -> None:
        """Check manifestations quality."""
        if not manifestations or not manifestations.manifestation:
            self.issues['minor'].append(f"{pid}: No manifestations defined")
            self.stats['no_manifestations'] += 1
            return
        
        for manif in manifestations.manifestation:
            if not manif.name or manif.name.strip() == "":
                self.issues['warning'].append(f"{pid}: Manifestation without name")
                self.stats['empty_manifestations'] += 1
    
    def check_consistency(self, pid: str, pattern: Pattern) -> None:
        """Check cross-field consistency."""
        # Check if complexity matches definition complexity
        if pattern.metadata.complexity == "high":
            # High complexity patterns should have multiple operations
            if pattern.operations and pattern.operations.operation:
                if len(pattern.operations.operation) < 3:
                    self.issues['minor'].append(
                        f"{pid}: Marked as HIGH complexity but only {len(pattern.operations.operation)} operations"
                    )
        
        # Check property IDs match pattern ID
        if pattern.properties and pattern.properties.property:
            for prop in pattern.properties.property:
                if prop.id and not prop.id.startswith(f"P.{pid}."):
                    self.issues['warning'].append(
                        f"{pid}: Property ID '{prop.id}' doesn't follow convention 'P.{pid}.N'"
                    )
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive quality report."""
        total_patterns = self.repo.get_statistics()['total_patterns']
        
        report = {
            "summary": {
                "total_patterns": total_patterns,
                "critical_issues": len(self.issues['critical']),
                "warnings": len(self.issues['warning']),
                "minor_issues": len(self.issues['minor']),
                "overall_quality_score": self.calculate_quality_score(total_patterns)
            },
            "statistics": dict(self.stats),
            "issues_by_severity": {
                "critical": self.issues['critical'][:50],  # Top 50
                "warning": self.issues['warning'][:50],
                "minor": self.issues['minor'][:30]
            },
            "quality_metrics": self.calculate_metrics(total_patterns),
            "recommendations": self.generate_recommendations()
        }
        
        return report
    
    def calculate_quality_score(self, total: int) -> float:
        """Calculate overall quality score (0-100)."""
        if total == 0:
            return 0.0
        
        # Weighted deductions
        critical_penalty = len(self.issues['critical']) * 2.0
        warning_penalty = len(self.issues['warning']) * 0.5
        minor_penalty = len(self.issues['minor']) * 0.1
        
        total_penalty = critical_penalty + warning_penalty + minor_penalty
        max_score = 100.0
        
        score = max(0, max_score - (total_penalty / total * 100))
        return round(score, 2)
    
    def calculate_metrics(self, total: int) -> Dict[str, Any]:
        """Calculate detailed quality metrics."""
        if total == 0:
            return {}
        
        return {
            "completeness": {
                "patterns_with_tuple_notation": round((1 - self.stats.get('missing_tuple_notation', 0) / total) * 100, 2),
                "patterns_with_components": round((1 - self.stats.get('missing_components', 0) / total) * 100, 2),
                "patterns_with_properties": round((1 - self.stats.get('no_properties', 0) / total) * 100, 2),
                "patterns_with_operations": round((1 - self.stats.get('no_operations', 0) / total) * 100, 2),
                "patterns_with_manifestations": round((1 - self.stats.get('no_manifestations', 0) / total) * 100, 2),
            },
            "accuracy": {
                "truncated_signatures_count": self.stats.get('truncated_signatures', 0),
                "truncated_properties_count": self.stats.get('truncated_properties', 0),
                "empty_formal_definitions": self.stats.get('operations_empty_formal_def', 0),
            },
            "consistency": {
                "generic_names_count": self.stats.get('generic_names', 0),
                "missing_timestamps_count": self.stats.get('missing_timestamps', 0),
            }
        }
    
    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if self.stats.get('truncated_signatures', 0) > 0:
            recommendations.append(
                f"CRITICAL: Fix {self.stats['truncated_signatures']} truncated operation signatures - "
                "these indicate incomplete data migration or parsing errors"
            )
        
        if self.stats.get('truncated_properties', 0) > 0:
            recommendations.append(
                f"CRITICAL: Fix {self.stats['truncated_properties']} truncated property specifications - "
                "formal specifications must be complete"
            )
        
        if self.stats.get('generic_names', 0) > 0:
            recommendations.append(
                f"WARNING: Replace {self.stats['generic_names']} generic placeholder names with "
                "descriptive pattern names"
            )
        
        if self.stats.get('missing_domains', 0) > 0:
            recommendations.append(
                f"Add domain classification to {self.stats['missing_domains']} patterns for better categorization"
            )
        
        if self.stats.get('operations_missing_formal_def', 0) > 0:
            recommendations.append(
                f"Add formal definitions to {self.stats['operations_missing_formal_def']} operations "
                "for completeness"
            )
        
        if self.stats.get('components_missing_description', 0) > 0:
            recommendations.append(
                f"Add descriptions to {self.stats['components_missing_description']} components "
                "to improve understandability"
            )
        
        if not recommendations:
            recommendations.append("Data quality is excellent - no major issues identified")
        
        return recommendations


def main():
    """Run quality assessment and generate report."""
    print("🔍 Universal Corpus Data Quality Assessment")
    print("=" * 60)
    
    with DataQualityAssessor() as assessor:
        report = assessor.assess_all()
    
    # Print report
    print("\n📊 SUMMARY")
    print("=" * 60)
    for key, value in report['summary'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\n📈 QUALITY METRICS")
    print("=" * 60)
    print("\n  Completeness:")
    for metric, value in report['quality_metrics']['completeness'].items():
        print(f"    {metric.replace('_', ' ').title()}: {value}%")
    
    print("\n  Accuracy Issues:")
    for metric, value in report['quality_metrics']['accuracy'].items():
        print(f"    {metric.replace('_', ' ').title()}: {value}")
    
    print("\n  Consistency Issues:")
    for metric, value in report['quality_metrics']['consistency'].items():
        print(f"    {metric.replace('_', ' ').title()}: {value}")
    
    print("\n🔧 RECOMMENDATIONS")
    print("=" * 60)
    for idx, rec in enumerate(report['recommendations'], 1):
        print(f"  {idx}. {rec}")
    
    print("\n⚠️  TOP CRITICAL ISSUES")
    print("=" * 60)
    for issue in report['issues_by_severity']['critical'][:10]:
        print(f"  • {issue}")
    
    if len(report['issues_by_severity']['critical']) > 10:
        print(f"  ... and {len(report['issues_by_severity']['critical']) - 10} more")
    
    print("\n📝 TOP WARNINGS")
    print("=" * 60)
    for issue in report['issues_by_severity']['warning'][:10]:
        print(f"  • {issue}")
    
    if len(report['issues_by_severity']['warning']) > 10:
        print(f"  ... and {len(report['issues_by_severity']['warning']) - 10} more")
    
    # Save detailed report
    output_file = Path(__file__).parent / "data_quality_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed report saved to: {output_file}")
    print("=" * 60)
    
    return 0 if report['summary']['critical_issues'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())


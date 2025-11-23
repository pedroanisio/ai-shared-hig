#!/usr/bin/env python3
"""
Dependency Assessment Tool
Validates inter-pattern dependencies and generates quality metrics.
"""

import json
import sys
from collections import defaultdict
from typing import Dict, List, Set, Tuple


class DependencyAnalyzer:
    def __init__(self, patterns_file: str):
        """Initialize analyzer with patterns from JSONL export."""
        self.patterns = {}
        self.pattern_ids = set()
        
        # Load all patterns
        with open(patterns_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    pattern = json.loads(line)
                    self.patterns[pattern['id']] = pattern
                    self.pattern_ids.add(pattern['id'])
        
        print(f"✅ Loaded {len(self.patterns)} patterns for analysis\n")
    
    def analyze(self) -> Dict:
        """Perform comprehensive dependency analysis."""
        results = {
            "total_patterns": len(self.patterns),
            "patterns_with_dependencies": 0,
            "total_dependency_links": 0,
            "issues": {
                "broken_references": [],
                "missing_bidirectional": [],
                "circular_dependencies": [],
                "orphaned_patterns": []
            },
            "dependency_types": {
                "requires": 0,
                "uses": 0,
                "specializes": 0,
                "specialized_by": 0
            },
            "statistics": {},
            "quality_score": 0.0
        }
        
        # Track dependency relationships
        all_references = set()
        dependency_graph = defaultdict(set)
        reverse_graph = defaultdict(set)
        
        # Analyze each pattern
        for pattern_id, pattern in self.patterns.items():
            dependencies = pattern.get('dependencies')
            
            if not dependencies:
                continue
            
            has_deps = False
            
            # Check requires
            requires = dependencies.get('requires')
            if requires:
                has_deps = True
                # Handle both list and dict formats
                dep_list = requires.get('pattern_ref', []) if isinstance(requires, dict) else requires
                for dep_id in dep_list:
                    results['dependency_types']['requires'] += 1
                    results['total_dependency_links'] += 1
                    all_references.add(dep_id)
                    dependency_graph[pattern_id].add(dep_id)
                    reverse_graph[dep_id].add(pattern_id)
                    
                    # Validate reference
                    if dep_id not in self.pattern_ids:
                        results['issues']['broken_references'].append({
                            "pattern_id": pattern_id,
                            "dependency_type": "requires",
                            "missing_reference": dep_id
                        })
            
            # Check uses
            uses = dependencies.get('uses')
            if uses:
                has_deps = True
                # Handle both list and dict formats
                dep_list = uses.get('pattern_ref', []) if isinstance(uses, dict) else uses
                for dep_id in dep_list:
                    results['dependency_types']['uses'] += 1
                    results['total_dependency_links'] += 1
                    all_references.add(dep_id)
                    dependency_graph[pattern_id].add(dep_id)
                    reverse_graph[dep_id].add(pattern_id)
                    
                    if dep_id not in self.pattern_ids:
                        results['issues']['broken_references'].append({
                            "pattern_id": pattern_id,
                            "dependency_type": "uses",
                            "missing_reference": dep_id
                        })
            
            # Check specializes
            specializes = dependencies.get('specializes')
            if specializes:
                has_deps = True
                # Handle both list and dict formats
                dep_list = specializes.get('pattern_ref', []) if isinstance(specializes, dict) else specializes
                for dep_id in dep_list:
                    results['dependency_types']['specializes'] += 1
                    results['total_dependency_links'] += 1
                    all_references.add(dep_id)
                    dependency_graph[pattern_id].add(dep_id)
                    reverse_graph[dep_id].add(pattern_id)
                    
                    if dep_id not in self.pattern_ids:
                        results['issues']['broken_references'].append({
                            "pattern_id": pattern_id,
                            "dependency_type": "specializes",
                            "missing_reference": dep_id
                        })
                    else:
                        # Check bidirectional: if A specializes B, B should have A in specialized_by
                        target_deps = self.patterns[dep_id].get('dependencies', {})
                        specialized_by_data = target_deps.get('specialized_by', [])
                        specialized_by_list = specialized_by_data.get('pattern_ref', []) if isinstance(specialized_by_data, dict) else specialized_by_data
                        if pattern_id not in specialized_by_list:
                            results['issues']['missing_bidirectional'].append({
                                "pattern_id": pattern_id,
                                "specializes": dep_id,
                                "issue": f"{dep_id} missing {pattern_id} in specialized_by"
                            })
            
            # Check specialized_by
            specialized_by = dependencies.get('specialized_by')
            if specialized_by:
                has_deps = True
                # Handle both list and dict formats
                dep_list = specialized_by.get('pattern_ref', []) if isinstance(specialized_by, dict) else specialized_by
                for dep_id in dep_list:
                    results['dependency_types']['specialized_by'] += 1
                    results['total_dependency_links'] += 1
                    all_references.add(dep_id)
                    reverse_graph[pattern_id].add(dep_id)
                    
                    if dep_id not in self.pattern_ids:
                        results['issues']['broken_references'].append({
                            "pattern_id": pattern_id,
                            "dependency_type": "specialized_by",
                            "missing_reference": dep_id
                        })
                    else:
                        # Check bidirectional: if A has B in specialized_by, B should specialize A
                        target_deps = self.patterns[dep_id].get('dependencies', {})
                        specializes_data = target_deps.get('specializes', [])
                        specializes_list = specializes_data.get('pattern_ref', []) if isinstance(specializes_data, dict) else specializes_data
                        if pattern_id not in specializes_list:
                            results['issues']['missing_bidirectional'].append({
                                "pattern_id": pattern_id,
                                "specialized_by": dep_id,
                                "issue": f"{dep_id} missing {pattern_id} in specializes"
                            })
            
            if has_deps:
                results['patterns_with_dependencies'] += 1
        
        # Find orphaned patterns (no incoming or outgoing dependencies)
        for pattern_id in self.pattern_ids:
            if pattern_id not in dependency_graph and pattern_id not in reverse_graph:
                # Check if it has any dependency fields
                deps = self.patterns[pattern_id].get('dependencies')
                if not deps:
                    results['issues']['orphaned_patterns'].append(pattern_id)
                    continue
                
                # Check for non-empty dependency fields
                has_any_deps = False
                for dep_type in ['requires', 'uses', 'specializes', 'specialized_by']:
                    dep_data = deps.get(dep_type)
                    if dep_data:
                        dep_list = dep_data.get('pattern_ref', []) if isinstance(dep_data, dict) else dep_data
                        if dep_list:
                            has_any_deps = True
                            break
                
                if not has_any_deps:
                    results['issues']['orphaned_patterns'].append(pattern_id)
        
        # Detect circular dependencies
        results['issues']['circular_dependencies'] = self._detect_cycles(dependency_graph)
        
        # Calculate statistics
        results['statistics'] = {
            "patterns_with_deps_percent": round(
                (results['patterns_with_dependencies'] / results['total_patterns']) * 100, 2
            ) if results['total_patterns'] > 0 else 0,
            "avg_deps_per_pattern": round(
                results['total_dependency_links'] / results['total_patterns'], 2
            ) if results['total_patterns'] > 0 else 0,
            "broken_reference_count": len(results['issues']['broken_references']),
            "missing_bidirectional_count": len(results['issues']['missing_bidirectional']),
            "circular_dependency_count": len(results['issues']['circular_dependencies']),
            "orphaned_pattern_count": len(results['issues']['orphaned_patterns'])
        }
        
        # Calculate quality score
        results['quality_score'] = self._calculate_quality_score(results)
        
        return results
    
    def _detect_cycles(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Detect circular dependencies using DFS."""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
                    return True
            
            path.pop()
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                dfs(node)
        
        return cycles
    
    def _calculate_quality_score(self, results: Dict) -> float:
        """
        Calculate dependency quality score (0-100).
        
        Scoring criteria:
        - No broken references: 40 points
        - Bidirectional consistency: 30 points
        - No circular dependencies: 20 points
        - Low orphan rate (<10%): 10 points
        """
        score = 100.0
        total = results['total_patterns']
        stats = results['statistics']
        
        # Deduct for broken references (up to 40 points)
        broken_count = stats['broken_reference_count']
        if broken_count > 0:
            # Severe penalty: -10 points per broken reference, capped at 40
            deduction = min(40, broken_count * 10)
            score -= deduction
        
        # Deduct for missing bidirectional links (up to 30 points)
        bidirectional_count = stats['missing_bidirectional_count']
        if bidirectional_count > 0:
            # Moderate penalty: -5 points per missing bidirectional, capped at 30
            deduction = min(30, bidirectional_count * 5)
            score -= deduction
        
        # Deduct for circular dependencies (up to 20 points)
        circular_count = stats['circular_dependency_count']
        if circular_count > 0:
            # Severe penalty: -20 points per cycle, capped at 20
            deduction = min(20, circular_count * 20)
            score -= deduction
        
        # Deduct for high orphan rate (up to 10 points)
        orphan_count = stats['orphaned_pattern_count']
        orphan_percent = (orphan_count / total * 100) if total > 0 else 0
        if orphan_percent > 10:
            # Minor penalty: -1 point per percent over 10%, capped at 10
            deduction = min(10, orphan_percent - 10)
            score -= deduction
        
        return max(0.0, round(score, 2))
    
    def generate_report(self, results: Dict) -> str:
        """Generate formatted dependency quality report."""
        report = []
        report.append("=" * 80)
        report.append("DEPENDENCY QUALITY ASSESSMENT REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        report.append("📊 SUMMARY")
        report.append("-" * 80)
        report.append(f"Total Patterns:              {results['total_patterns']}")
        report.append(f"Patterns with Dependencies:  {results['patterns_with_dependencies']} "
                     f"({results['statistics']['patterns_with_deps_percent']}%)")
        report.append(f"Total Dependency Links:      {results['total_dependency_links']}")
        report.append(f"Avg Dependencies/Pattern:    {results['statistics']['avg_deps_per_pattern']}")
        report.append("")
        
        # Dependency types
        report.append("🔗 DEPENDENCY TYPES")
        report.append("-" * 80)
        for dep_type, count in results['dependency_types'].items():
            report.append(f"{dep_type:20s}: {count:4d}")
        report.append("")
        
        # Issues
        report.append("⚠️  ISSUES DETECTED")
        report.append("-" * 80)
        stats = results['statistics']
        
        # Broken references
        broken_count = stats['broken_reference_count']
        status = "❌ CRITICAL" if broken_count > 0 else "✅ PASS"
        report.append(f"Broken References:           {broken_count:4d}  {status}")
        if broken_count > 0:
            report.append("\n  Details:")
            for issue in results['issues']['broken_references'][:10]:  # Show first 10
                report.append(f"    • {issue['pattern_id']} -> {issue['dependency_type']} -> "
                             f"{issue['missing_reference']} (NOT FOUND)")
            if broken_count > 10:
                report.append(f"    ... and {broken_count - 10} more")
        
        report.append("")
        
        # Missing bidirectional
        bidirectional_count = stats['missing_bidirectional_count']
        status = "⚠️  WARNING" if bidirectional_count > 0 else "✅ PASS"
        report.append(f"Missing Bidirectional:       {bidirectional_count:4d}  {status}")
        if bidirectional_count > 0:
            report.append("\n  Details:")
            for issue in results['issues']['missing_bidirectional'][:10]:
                report.append(f"    • {issue['pattern_id']}: {issue['issue']}")
            if bidirectional_count > 10:
                report.append(f"    ... and {bidirectional_count - 10} more")
        
        report.append("")
        
        # Circular dependencies
        circular_count = stats['circular_dependency_count']
        status = "❌ CRITICAL" if circular_count > 0 else "✅ PASS"
        report.append(f"Circular Dependencies:       {circular_count:4d}  {status}")
        if circular_count > 0:
            report.append("\n  Details:")
            for cycle in results['issues']['circular_dependencies']:
                report.append(f"    • {' -> '.join(cycle)}")
        
        report.append("")
        
        # Orphaned patterns
        orphan_count = stats['orphaned_pattern_count']
        total = results['total_patterns']
        status = "ℹ️  INFO" if orphan_count < total * 0.1 else "⚠️  WARNING"
        report.append(f"Orphaned Patterns:           {orphan_count:4d}  {status}")
        if orphan_count > 0 and orphan_count <= 20:
            report.append("\n  Details:")
            for pattern_id in results['issues']['orphaned_patterns'][:20]:
                pattern = self.patterns[pattern_id]
                name = pattern.get('metadata', {}).get('name', 'Unknown')
                report.append(f"    • {pattern_id}: {name}")
        
        report.append("")
        report.append("=" * 80)
        
        # Quality Score
        score = results['quality_score']
        if score >= 90:
            grade = "🏆 EXCELLENT"
        elif score >= 75:
            grade = "✅ GOOD"
        elif score >= 60:
            grade = "⚠️  FAIR"
        else:
            grade = "❌ POOR"
        
        report.append(f"DEPENDENCY QUALITY SCORE: {score}/100  {grade}")
        report.append("=" * 80)
        report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS")
        report.append("-" * 80)
        if broken_count > 0:
            report.append("• FIX CRITICAL: Resolve all broken dependency references")
        if bidirectional_count > 0:
            report.append("• IMPROVE: Add missing bidirectional links for specializes/specialized_by")
        if circular_count > 0:
            report.append("• FIX CRITICAL: Break circular dependency chains")
        if orphan_count > total * 0.2:
            report.append("• CONSIDER: Review orphaned patterns and add relevant dependencies")
        if score == 100:
            report.append("• ✅ All dependency quality checks passed!")
        
        report.append("")
        
        return "\n".join(report)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 assess_dependencies.py <patterns_jsonl_file>")
        sys.exit(1)
    
    patterns_file = sys.argv[1]
    
    print("🔍 Starting Dependency Quality Assessment...\n")
    
    analyzer = DependencyAnalyzer(patterns_file)
    results = analyzer.analyze()
    
    # Print report
    report = analyzer.generate_report(results)
    print(report)
    
    # Save detailed results as JSON
    output_file = "dependency_quality_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Detailed results saved to: {output_file}")
    
    # Exit with appropriate code
    if results['statistics']['broken_reference_count'] > 0:
        sys.exit(1)  # Critical issues
    elif results['quality_score'] < 75:
        sys.exit(1)  # Quality too low
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()


#!/usr/bin/env python3
"""
CLI tool for converting between full and compact pattern formats.

This tool demonstrates the token-efficient compact format and provides utilities
for conversion, validation, and compression analysis.

Usage:
    # Convert full JSONL to compact format
    python -m universal_corpus.cli.compact_converter to-compact input.jsonl output_compact.jsonl
    
    # Convert compact format back to full JSONL
    python -m universal_corpus.cli.compact_converter to-full compact.jsonl output_full.jsonl
    
    # Analyze compression ratio
    python -m universal_corpus.cli.compact_converter analyze input.jsonl
    
    # Validate round-trip conversion
    python -m universal_corpus.cli.compact_converter validate input.jsonl
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List
from universal_corpus.models import Pattern
from universal_corpus.compact_format import (
    pattern_to_compact,
    compact_to_pattern,
    export_compact_jsonl,
    import_compact_jsonl,
    calculate_compression_ratio
)
from universal_corpus.csv_compact import (
    patterns_to_csv,
    patterns_to_csv_simple,
    csv_to_patterns
)


def to_compact(input_file: Path, output_file: Path) -> None:
    """
    Convert full JSONL format to compact format.
    
    Args:
        input_file: Path to full JSONL file
        output_file: Path to output compact JSONL file
    """
    print(f"Reading full format from: {input_file}")
    
    # Read and parse full format
    patterns = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            
            try:
                pattern_data = json.loads(line)
                pattern = Pattern(**pattern_data)
                patterns.append(pattern)
            except Exception as e:
                print(f"Error parsing line {line_num}: {e}", file=sys.stderr)
                sys.exit(1)
    
    print(f"Loaded {len(patterns)} patterns")
    
    # Convert to compact format
    compact_jsonl = export_compact_jsonl(patterns)
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(compact_jsonl)
    
    print(f"Wrote compact format to: {output_file}")
    
    # Calculate and display statistics
    with open(input_file, 'r', encoding='utf-8') as f:
        full_content = f.read()
    
    stats = calculate_compression_ratio(full_content, compact_jsonl)
    
    print("\n=== Compression Statistics ===")
    print(f"Full size:     {stats['full_size_bytes']:,} bytes (~{stats['full_tokens_estimate']:,} tokens)")
    print(f"Compact size:  {stats['compact_size_bytes']:,} bytes (~{stats['compact_tokens_estimate']:,} tokens)")
    print(f"Reduction:     {stats['reduction_bytes']:,} bytes ({stats['reduction_percentage']:.1f}%)")
    print(f"Token savings: ~{stats['token_savings']:,} tokens")
    print(f"Compression:   {stats['compression_ratio']}x")


def to_full(input_file: Path, output_file: Path) -> None:
    """
    Convert compact format to full JSONL format.
    
    Args:
        input_file: Path to compact JSONL file
        output_file: Path to output full JSONL file
    """
    print(f"Reading compact format from: {input_file}")
    
    # Read compact format
    with open(input_file, 'r', encoding='utf-8') as f:
        compact_content = f.read()
    
    # Parse and convert to full patterns
    try:
        patterns = import_compact_jsonl(compact_content)
        print(f"Loaded {len(patterns)} patterns")
    except Exception as e:
        print(f"Error parsing compact format: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Write full format
    with open(output_file, 'w', encoding='utf-8') as f:
        for pattern in patterns:
            pattern_dict = pattern.model_dump(mode='json', exclude_none=False)
            f.write(json.dumps(pattern_dict, ensure_ascii=False) + '\n')
    
    print(f"Wrote full format to: {output_file}")


def analyze(input_file: Path) -> None:
    """
    Analyze compression ratio for a full JSONL file.
    
    Args:
        input_file: Path to full JSONL file
    """
    print(f"Analyzing: {input_file}")
    
    # Read full format
    with open(input_file, 'r', encoding='utf-8') as f:
        full_content = f.read()
    
    # Parse patterns
    patterns = []
    for line in full_content.strip().split('\n'):
        if not line.strip():
            continue
        try:
            pattern_data = json.loads(line)
            pattern = Pattern(**pattern_data)
            patterns.append(pattern)
        except Exception as e:
            print(f"Error parsing pattern: {e}", file=sys.stderr)
            continue
    
    print(f"Patterns: {len(patterns)}")
    
    # Convert to compact
    compact_jsonl = export_compact_jsonl(patterns)
    
    # Calculate statistics
    stats = calculate_compression_ratio(full_content, compact_jsonl)
    
    print("\n=== Compression Analysis ===")
    print(f"Full Format:")
    print(f"  Size:   {stats['full_size_bytes']:,} bytes")
    print(f"  Tokens: ~{stats['full_tokens_estimate']:,} (estimated)")
    print(f"\nCompact Format:")
    print(f"  Size:   {stats['compact_size_bytes']:,} bytes")
    print(f"  Tokens: ~{stats['compact_tokens_estimate']:,} (estimated)")
    print(f"\nSavings:")
    print(f"  Bytes:       {stats['reduction_bytes']:,} ({stats['reduction_percentage']:.1f}% reduction)")
    print(f"  Tokens:      ~{stats['token_savings']:,} saved")
    print(f"  Compression: {stats['compression_ratio']}x")
    
    # Show per-pattern average
    if len(patterns) > 0:
        avg_full = stats['full_tokens_estimate'] // len(patterns)
        avg_compact = stats['compact_tokens_estimate'] // len(patterns)
        print(f"\nPer-Pattern Average:")
        print(f"  Full:    ~{avg_full:,} tokens")
        print(f"  Compact: ~{avg_compact:,} tokens")
        print(f"  Savings: ~{avg_full - avg_compact:,} tokens per pattern")


def validate(input_file: Path) -> None:
    """
    Validate round-trip conversion (full → compact → full).
    
    Args:
        input_file: Path to full JSONL file
    """
    print(f"Validating round-trip conversion for: {input_file}")
    
    # Read original patterns
    original_patterns = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            
            try:
                pattern_data = json.loads(line)
                pattern = Pattern(**pattern_data)
                original_patterns.append(pattern)
            except Exception as e:
                print(f"Error parsing line {line_num}: {e}", file=sys.stderr)
                sys.exit(1)
    
    print(f"Loaded {len(original_patterns)} patterns")
    
    # Convert to compact and back
    errors = []
    for i, original in enumerate(original_patterns, start=1):
        try:
            # Convert to compact
            compact = pattern_to_compact(original)
            
            # Convert back to full
            restored = compact_to_pattern(compact)
            
            # Compare (using dict representation for deep comparison)
            original_dict = original.model_dump(mode='json', exclude_none=False)
            restored_dict = restored.model_dump(mode='json', exclude_none=False)
            
            if original_dict != restored_dict:
                errors.append(f"Pattern {i} (ID: {original.id}): Round-trip mismatch")
                
                # Find differences (basic check)
                def find_diffs(d1, d2, path=""):
                    diffs = []
                    if type(d1) != type(d2):
                        diffs.append(f"{path}: type mismatch")
                    elif isinstance(d1, dict):
                        for key in set(list(d1.keys()) + list(d2.keys())):
                            if key not in d1:
                                diffs.append(f"{path}.{key}: missing in original")
                            elif key not in d2:
                                diffs.append(f"{path}.{key}: missing in restored")
                            else:
                                diffs.extend(find_diffs(d1[key], d2[key], f"{path}.{key}"))
                    elif isinstance(d1, list):
                        if len(d1) != len(d2):
                            diffs.append(f"{path}: length mismatch ({len(d1)} vs {len(d2)})")
                        else:
                            for idx, (item1, item2) in enumerate(zip(d1, d2)):
                                diffs.extend(find_diffs(item1, item2, f"{path}[{idx}]"))
                    elif d1 != d2:
                        diffs.append(f"{path}: value mismatch ({d1} vs {d2})")
                    return diffs
                
                diffs = find_diffs(original_dict, restored_dict)
                for diff in diffs[:5]:  # Show first 5 differences
                    print(f"  - {diff}")
        
        except Exception as e:
            errors.append(f"Pattern {i} (ID: {original.id}): Conversion error: {e}")
    
    # Report results
    if errors:
        print(f"\n❌ Validation FAILED with {len(errors)} error(s):")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("\n✅ Validation PASSED: All patterns convert correctly")
        print("   Round-trip conversion preserves all data")


def to_csv(input_file: Path, output_file: Path, simple: bool = False) -> None:
    """
    Convert full JSONL to CSV compact format.
    
    Args:
        input_file: Path to full JSONL file
        output_file: Path to output CSV file
        simple: If True, use simplified CSV format
    """
    print(f"Reading full format from: {input_file}")
    
    # Read and parse full format
    patterns = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            
            try:
                pattern_data = json.loads(line)
                pattern = Pattern(**pattern_data)
                patterns.append(pattern)
            except Exception as e:
                print(f"Error parsing line {line_num}: {e}", file=sys.stderr)
                sys.exit(1)
    
    print(f"Loaded {len(patterns)} patterns")
    
    # Convert to CSV
    if simple:
        csv_content = patterns_to_csv_simple(patterns)
        print("Using simplified CSV format (no detail columns)")
    else:
        csv_content = patterns_to_csv(patterns)
        print("Using full CSV compact format (with detail columns)")
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(csv_content)
    
    print(f"Wrote CSV to: {output_file}")
    print(f"Size: {len(csv_content):,} bytes")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert between full and compact pattern formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # to-compact command
    compact_parser = subparsers.add_parser(
        'to-compact',
        help='Convert full JSONL to compact format'
    )
    compact_parser.add_argument('input', type=Path, help='Input full JSONL file')
    compact_parser.add_argument('output', type=Path, help='Output compact JSONL file')
    
    # to-full command
    full_parser = subparsers.add_parser(
        'to-full',
        help='Convert compact format to full JSONL'
    )
    full_parser.add_argument('input', type=Path, help='Input compact JSONL file')
    full_parser.add_argument('output', type=Path, help='Output full JSONL file')
    
    # to-csv command (NEW!)
    csv_parser = subparsers.add_parser(
        'to-csv',
        help='Convert full JSONL to CSV compact format'
    )
    csv_parser.add_argument('input', type=Path, help='Input full JSONL file')
    csv_parser.add_argument('output', type=Path, help='Output CSV file')
    csv_parser.add_argument('--simple', action='store_true',
                           help='Use simplified CSV format (no detail columns)')
    
    # analyze command
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze compression ratio'
    )
    analyze_parser.add_argument('input', type=Path, help='Input full JSONL file')
    
    # validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate round-trip conversion'
    )
    validate_parser.add_argument('input', type=Path, help='Input full JSONL file')
    
    args = parser.parse_args()
    
    # Execute command
    try:
        if args.command == 'to-compact':
            to_compact(args.input, args.output)
        elif args.command == 'to-full':
            to_full(args.input, args.output)
        elif args.command == 'to-csv':
            to_csv(args.input, args.output, simple=args.simple)
        elif args.command == 'analyze':
            analyze(args.input)
        elif args.command == 'validate':
            validate(args.input)
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()


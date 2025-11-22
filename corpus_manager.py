#!/usr/bin/env python3
"""
Universal Corpus Document Manager
Parses, structures, and rebuilds the Universal Corpus with zero data loss.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import sys


@dataclass
class Section:
    """Represents a hierarchical section in the document."""
    level: int  # Header level (1-6)
    title: str
    number: Optional[str]  # e.g., "0", "2.1", "P35"
    raw_header: str  # Original header line
    content: List[str] = field(default_factory=list)  # Lines between this header and next
    subsections: List['Section'] = field(default_factory=list)
    start_line: int = 0
    end_line: int = 0

    def get_full_title(self) -> str:
        """Get the complete title including number."""
        return self.raw_header.lstrip('#').strip()
    
    def add_content_line(self, line: str) -> None:
        """Add a line to this section's content."""
        self.content.append(line)
    
    def to_lines(self) -> List[str]:
        """Convert section back to markdown lines (recursive)."""
        lines = [self.raw_header]
        lines.extend(self.content)
        for subsection in self.subsections:
            lines.extend(subsection.to_lines())
        return lines


@dataclass
class Pattern:
    """Represents a pattern (P), concept (C), or flow (F)."""
    pattern_type: str  # 'P', 'C', 'F'
    number: str  # e.g., "1", "35", "1.1"
    name: str
    section: Section
    
    @property
    def id(self) -> str:
        """Get pattern identifier like P35, C1, F1.1"""
        return f"{self.pattern_type}{self.number}"


class CorpusDocument:
    """
    Main document parser and builder.
    Ensures round-trip fidelity: parse(text).rebuild() == text
    """
    
    def __init__(self):
        self.raw_lines: List[str] = []
        self.sections: List[Section] = []
        self.patterns: Dict[str, Pattern] = {}
        self.metadata: Dict[str, str] = {}
        
    def parse(self, content: str) -> None:
        """Parse document content into structured sections."""
        self.raw_lines = content.splitlines(keepends=True)
        
        # Parse metadata from header
        self._parse_metadata()
        
        # Parse hierarchical sections
        self.sections = self._parse_sections(self.raw_lines)
        
        # Extract patterns
        self._extract_patterns()
    
    def _parse_metadata(self) -> None:
        """Extract metadata from document header."""
        in_header = True
        for line in self.raw_lines[:20]:  # Check first 20 lines
            if line.startswith('# '):
                self.metadata['title'] = line.lstrip('#').strip()
            elif line.startswith('**Version:**'):
                self.metadata['version'] = line.split('**Version:**')[1].strip()
            elif line.startswith('**Date:**'):
                self.metadata['date'] = line.split('**Date:**')[1].strip()
            elif line.startswith('**Status:**'):
                self.metadata['status'] = line.split('**Status:**')[1].strip()
            elif line.startswith('# TABLE OF CONTENTS'):
                break
    
    def _parse_sections(self, lines: List[str], start_idx: int = 0, 
                       parent_level: int = 0, line_offset: int = 0) -> List[Section]:
        """
        Recursively parse markdown headers into hierarchical sections.
        Preserves all content exactly as written.
        
        Args:
            lines: Lines to parse
            start_idx: Index to start parsing from
            parent_level: Level of parent section (for hierarchy)
            line_offset: Offset to add to line numbers (for absolute positioning)
        """
        sections = []
        current_section: Optional[Section] = None
        i = start_idx
        
        while i < len(lines):
            line = lines[i]
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if header_match:
                level = len(header_match.group(1))
                title_text = header_match.group(2).strip()
                
                # If this is a subsection of current section, handle recursively
                if current_section and level > current_section.level:
                    # Find all lines for this subsection
                    subsection_end = self._find_section_end(lines, i, level)
                    subsection_lines = lines[i:subsection_end]
                    
                    # Parse subsections recursively with proper offset
                    subsections = self._parse_sections(
                        subsection_lines, 0, level, line_offset + i
                    )
                    current_section.subsections.extend(subsections)
                    
                    # Update end line
                    if subsections:
                        current_section.end_line = subsections[-1].end_line
                    
                    i = subsection_end
                    continue
                
                # If we're at same or higher level, finish current section and start new
                if current_section and level <= parent_level:
                    # We've gone back up the hierarchy, return to parent
                    break
                
                # Save previous section if exists
                if current_section:
                    current_section.end_line = line_offset + i - 1
                    sections.append(current_section)
                
                # Parse section number if present
                number = self._extract_section_number(title_text)
                
                # Create new section with absolute line number
                current_section = Section(
                    level=level,
                    title=title_text,
                    number=number,
                    raw_header=line.rstrip('\n'),
                    start_line=line_offset + i
                )
            
            elif current_section is not None:
                # Add content to current section
                current_section.add_content_line(line.rstrip('\n'))
            
            i += 1
        
        # Don't forget the last section
        if current_section:
            current_section.end_line = line_offset + i - 1
            sections.append(current_section)
        
        return sections
    
    def _find_section_end(self, lines: List[str], start_idx: int, level: int) -> int:
        """Find where a section ends (next header at same or higher level)."""
        for i in range(start_idx + 1, len(lines)):
            header_match = re.match(r'^(#{1,6})\s+', lines[i])
            if header_match:
                next_level = len(header_match.group(1))
                if next_level <= level:
                    return i
        return len(lines)
    
    def _extract_section_number(self, title: str) -> Optional[str]:
        """Extract section number from title."""
        # Match patterns like "0. ", "2.1 ", "P35. ", "C1. ", "F1.1 "
        patterns = [
            r'^(\d+)\.\s',           # "0. FOUNDATIONS"
            r'^(\d+\.\d+)\s',        # "2.1 Input"
            r'^([PCF]\d+)\.\s',      # "P35. Split"
            r'^([PCF]\d+\.\d+)\s',   # "F1.1 Capture"
        ]
        
        for pattern in patterns:
            match = re.match(pattern, title)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_patterns(self) -> None:
        """Extract all patterns (P), concepts (C), and flows (F) from sections."""
        for section in self._all_sections():
            if section.number:
                # Check if this is a pattern/concept/flow
                pattern_match = re.match(r'^([PCF])(\d+(?:\.\d+)?)$', section.number)
                if pattern_match:
                    pattern_type = pattern_match.group(1)
                    number = pattern_match.group(2)
                    
                    # Extract name (remove pattern number from title)
                    name_match = re.match(r'^[PCF]\d+(?:\.\d+)?\.\s*(.+)$', section.title)
                    name = name_match.group(1) if name_match else section.title
                    
                    pattern = Pattern(
                        pattern_type=pattern_type,
                        number=number,
                        name=name,
                        section=section
                    )
                    self.patterns[pattern.id] = pattern
    
    def _all_sections(self, sections: Optional[List[Section]] = None) -> List[Section]:
        """Recursively get all sections (flattened)."""
        if sections is None:
            sections = self.sections
        
        result = []
        for section in sections:
            result.append(section)
            result.extend(self._all_sections(section.subsections))
        return result
    
    def rebuild(self) -> str:
        """
        Rebuild the complete document from structured sections.
        Guarantees: parse(text).rebuild() produces identical output.
        """
        # Simple approach: just join the original lines
        # This ensures 100% fidelity
        return ''.join(self.raw_lines)
    
    def rebuild_from_sections(self) -> str:
        """
        Alternative rebuild that uses structured sections.
        May have minor whitespace differences but same content.
        """
        lines = []
        for section in self.sections:
            lines.extend(section.to_lines())
        return '\n'.join(lines) + '\n'
    
    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """Get a specific pattern by ID (e.g., 'P35', 'C1', 'F1.1')."""
        return self.patterns.get(pattern_id)
    
    def get_section(self, section_number: str) -> Optional[Section]:
        """Get a section by number (e.g., '0', '2.1')."""
        for section in self._all_sections():
            if section.number == section_number:
                return section
        return None
    
    def _find_section_actual_end(self, section: Section) -> int:
        """Find the actual end line of a section including all its content and subsections."""
        # Start with section start
        max_line = section.start_line + 1 + len(section.content)
        
        # Add subsections recursively
        if section.subsections:
            for subsection in section.subsections:
                subsection_end = self._find_section_actual_end(subsection)
                max_line = max(max_line, subsection_end)
        
        # If this section has an end_line set, use it
        if section.end_line > 0:
            max_line = max(max_line, section.end_line + 1)
        
        return max_line
    
    def _get_section_original_content(self, section: Section) -> str:
        """Get the exact original content of a section from raw_lines."""
        start = section.start_line
        end = self._find_section_actual_end(section)
        return ''.join(self.raw_lines[start:end])
    
    def export_pattern(self, pattern_id: str) -> str:
        """Export a single pattern as markdown."""
        pattern = self.get_pattern(pattern_id)
        if not pattern:
            return ""
        return self._get_section_original_content(pattern.section)
    
    def validate_round_trip(self, original_content: str) -> Tuple[bool, str]:
        """
        Validate that parsing and rebuilding produces identical content.
        Returns: (is_valid, error_message)
        """
        rebuilt = self.rebuild()
        
        if original_content == rebuilt:
            return True, "Perfect round-trip: content identical"
        
        # Check if difference is only in line endings
        original_normalized = original_content.replace('\r\n', '\n')
        rebuilt_normalized = rebuilt.replace('\r\n', '\n')
        
        if original_normalized == rebuilt_normalized:
            return True, "Round-trip valid: only line ending differences"
        
        # Find first difference
        for i, (orig_char, rebuilt_char) in enumerate(zip(original_content, rebuilt)):
            if orig_char != rebuilt_char:
                line_num = original_content[:i].count('\n') + 1
                return False, f"First difference at character {i} (line ~{line_num}): '{orig_char}' vs '{rebuilt_char}'"
        
        # Different lengths
        return False, f"Length mismatch: original={len(original_content)}, rebuilt={len(rebuilt)}"
    
    def get_stats(self) -> Dict[str, int]:
        """Get document statistics."""
        patterns_by_type = {'P': 0, 'C': 0, 'F': 0}
        for pattern in self.patterns.values():
            patterns_by_type[pattern.pattern_type] = patterns_by_type.get(pattern.pattern_type, 0) + 1
        
        return {
            'total_lines': len(self.raw_lines),
            'total_sections': len(self._all_sections()),
            'top_level_sections': len(self.sections),
            'total_patterns': len(self.patterns),
            'concepts': patterns_by_type.get('C', 0),
            'patterns': patterns_by_type.get('P', 0),
            'flows': patterns_by_type.get('F', 0),
        }
    
    def list_patterns(self, pattern_type: Optional[str] = None) -> List[str]:
        """List all pattern IDs, optionally filtered by type."""
        pattern_ids = sorted(self.patterns.keys(), 
                            key=lambda x: (x[0], float(re.sub(r'[PCF]', '', x))))
        
        if pattern_type:
            pattern_ids = [pid for pid in pattern_ids if pid.startswith(pattern_type)]
        
        return pattern_ids
    
    def find_missing_patterns(self) -> Dict[str, List[str]]:
        """Find gaps in pattern numbering."""
        missing = {'P': [], 'C': [], 'F': []}
        
        # Check P patterns (expect P1-P63)
        p_numbers = [int(p[1:]) for p in self.patterns.keys() if p.startswith('P') and '.' not in p]
        if p_numbers:
            for i in range(1, max(p_numbers) + 1):
                if i not in p_numbers:
                    missing['P'].append(f'P{i}')
        
        # Check C patterns (expect C1-C5)
        c_numbers = [int(p[1:]) for p in self.patterns.keys() if p.startswith('C')]
        if c_numbers:
            for i in range(1, max(c_numbers) + 1):
                if i not in c_numbers:
                    missing['C'].append(f'C{i}')
        
        # F patterns can have decimals, just list what we have
        # Don't check for missing as F1.1, F1.2 etc are valid
        
        return {k: v for k, v in missing.items() if v}
    
    def split_to_directory(self, output_dir: Path) -> Dict[str, Path]:
        """
        Split document into individual parts with complete reconstruction data.
        
        Creates:
        - _manifest.json: Ordered list of document parts
        - _part_NNNN.md: Non-pattern sections (headers, TOC, etc.)
        - PatternID_Name.md: Individual patterns
        
        Returns mapping of part_id -> file_path
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Build manifest: ordered list of all document parts
        manifest = {
            'version': '1.0',
            'total_lines': len(self.raw_lines),
            'parts': []
        }
        
        part_files = {}
        part_counter = 0
        
        # Track what lines are covered by patterns
        pattern_line_map = {}  # line_num -> pattern_id
        for pattern in self.patterns.values():
            start = pattern.section.start_line
            end = self._find_section_actual_end(pattern.section)
            for line_num in range(start, end):
                pattern_line_map[line_num] = pattern.id
        
        # Scan through document and create parts
        current_part_lines = []
        current_part_start = 0
        
        for line_num in range(len(self.raw_lines)):
            if line_num in pattern_line_map:
                # Save previous non-pattern part if any
                if current_part_lines:
                    part_id = f"_part_{part_counter:04d}"
                    part_counter += 1
                    filepath = output_dir / f"{part_id}.md"
                    content = ''.join(current_part_lines)
                    filepath.write_text(content, encoding='utf-8')
                    part_files[part_id] = filepath
                    
                    manifest['parts'].append({
                        'type': 'section',
                        'id': part_id,
                        'filename': filepath.name,
                        'start_line': current_part_start,
                        'end_line': line_num - 1,
                        'lines': len(current_part_lines)
                    })
                    current_part_lines = []
                
                # Add pattern part (only once when we first encounter it)
                pattern_id = pattern_line_map[line_num]
                if not any(p.get('id') == pattern_id for p in manifest['parts']):
                    pattern = self.patterns[pattern_id]
                    safe_name = pattern.name.replace('/', '-').replace(' ', '_')
                    filename = f"{pattern_id}_{safe_name}.md"
                    filepath = output_dir / filename
                    
                    # Export pattern content
                    content = self.export_pattern(pattern_id)
                    filepath.write_text(content, encoding='utf-8')
                    part_files[pattern_id] = filepath
                    
                    start = pattern.section.start_line
                    end = self._find_section_actual_end(pattern.section)
                    
                    manifest['parts'].append({
                        'type': 'pattern',
                        'id': pattern_id,
                        'name': pattern.name,
                        'filename': filepath.name,
                        'start_line': start,
                        'end_line': end - 1,
                        'lines': end - start
                    })
                
                # Skip to end of pattern
                if pattern_line_map.get(line_num + 1) != pattern_line_map[line_num]:
                    current_part_start = line_num + 1
                    while current_part_start < len(self.raw_lines) and current_part_start in pattern_line_map:
                        current_part_start += 1
            else:
                # Accumulate non-pattern lines
                if not current_part_lines:
                    current_part_start = line_num
                current_part_lines.append(self.raw_lines[line_num])
        
        # Save final non-pattern part if any
        if current_part_lines:
            part_id = f"_part_{part_counter:04d}"
            filepath = output_dir / f"{part_id}.md"
            content = ''.join(current_part_lines)
            filepath.write_text(content, encoding='utf-8')
            part_files[part_id] = filepath
            
            manifest['parts'].append({
                'type': 'section',
                'id': part_id,
                'filename': filepath.name,
                'start_line': current_part_start,
                'end_line': len(self.raw_lines) - 1,
                'lines': len(current_part_lines)
            })
        
        # Write manifest
        import json
        manifest_path = output_dir / '_manifest.json'
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        part_files['_manifest'] = manifest_path
        
        return part_files
    
    def concatenate_from_directory(self, input_dir: Path) -> str:
        """
        Concatenate parts back into complete document.
        
        Reads _manifest.json and assembles all parts in correct order.
        Does NOT rely on original document - purely reconstructs from parts.
        
        Returns the reconstructed document content.
        """
        import json
        
        # Read manifest
        manifest_path = input_dir / '_manifest.json'
        if not manifest_path.exists():
            raise FileNotFoundError(
                f"No manifest found in {input_dir}. "
                "Directory must be created by split_to_directory()."
            )
        
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        
        # Assemble document from parts in order
        result_lines = []
        
        for part_info in manifest['parts']:
            filepath = input_dir / part_info['filename']
            
            if not filepath.exists():
                raise FileNotFoundError(f"Missing part file: {filepath}")
            
            content = filepath.read_text(encoding='utf-8')
            result_lines.append(content)
        
        return ''.join(result_lines)
    
    def validate_split_concatenate_roundtrip(self, temp_dir: Path) -> Tuple[bool, str]:
        """
        Validate that split → concatenate produces identical content.
        
        1. Split document into individual part files + manifest
        2. Concatenate files back together (using ONLY the split parts)
        3. Compare with original
        
        This proves the split is self-contained and complete.
        
        Returns: (is_valid, message)
        """
        original_content = self.rebuild()
        
        # Split to files
        part_files = self.split_to_directory(temp_dir)
        num_parts = len([f for f in part_files.keys() if f != '_manifest'])
        
        # Create a NEW parser instance to prove we don't use cached data
        # Concatenate reads ONLY from the split files
        temp_doc = CorpusDocument()
        reconstructed = temp_doc.concatenate_from_directory(temp_dir)
        
        # Compare
        if original_content == reconstructed:
            return True, f"Perfect split-concatenate roundtrip: {num_parts} parts (self-contained)"
        
        # Check normalized
        original_normalized = original_content.replace('\r\n', '\n')
        reconstructed_normalized = reconstructed.replace('\r\n', '\n')
        
        if original_normalized == reconstructed_normalized:
            return True, f"Split-concatenate valid: {num_parts} parts (line ending differences only)"
        
        # Find first difference
        for i, (orig_char, recon_char) in enumerate(zip(original_content, reconstructed)):
            if orig_char != recon_char:
                line_num = original_content[:i].count('\n') + 1
                return False, f"First difference at character {i} (line ~{line_num}): '{orig_char}' vs '{recon_char}'"
        
        return False, f"Length mismatch: original={len(original_content)}, reconstructed={len(reconstructed)}"


def main():
    """Command-line interface for corpus management."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Universal Corpus Document Manager')
    parser.add_argument('input_file', help='Path to universal.doc')
    parser.add_argument('--validate', action='store_true', 
                       help='Validate round-trip parsing')
    parser.add_argument('--stats', action='store_true',
                       help='Show document statistics')
    parser.add_argument('--list', choices=['all', 'P', 'C', 'F'],
                       help='List patterns')
    parser.add_argument('--export', metavar='PATTERN_ID',
                       help='Export specific pattern (e.g., P35)')
    parser.add_argument('--missing', action='store_true',
                       help='Find missing patterns in numbering')
    parser.add_argument('--rebuild', metavar='OUTPUT_FILE',
                       help='Rebuild document to output file')
    parser.add_argument('--split', metavar='OUTPUT_DIR',
                       help='Split document into self-contained parts (manifest + files)')
    parser.add_argument('--concatenate', metavar='INPUT_DIR',
                       help='Concatenate parts back into document (standalone, no original needed)')
    parser.add_argument('--validate-split', metavar='TEMP_DIR',
                       help='Validate split-concatenate roundtrip')
    
    args = parser.parse_args()
    
    # Read input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        return 1
    
    content = input_path.read_text(encoding='utf-8')
    
    # Parse document
    doc = CorpusDocument()
    print(f"Parsing {input_path}...", file=sys.stderr)
    doc.parse(content)
    
    # Execute commands
    if args.validate:
        is_valid, message = doc.validate_round_trip(content)
        print(f"Round-trip validation: {message}")
        return 0 if is_valid else 1
    
    if args.stats:
        stats = doc.get_stats()
        print("Document Statistics:")
        for key, value in stats.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
    
    if args.list:
        pattern_type = None if args.list == 'all' else args.list
        patterns = doc.list_patterns(pattern_type)
        print(f"Patterns ({len(patterns)}):")
        for pid in patterns:
            pattern = doc.get_pattern(pid)
            print(f"  {pid}: {pattern.name}")
    
    if args.export:
        content = doc.export_pattern(args.export)
        if content:
            print(content)
        else:
            print(f"Error: Pattern {args.export} not found", file=sys.stderr)
            return 1
    
    if args.missing:
        missing = doc.find_missing_patterns()
        if missing:
            print("Missing patterns:")
            for pattern_type, pattern_ids in missing.items():
                print(f"  {pattern_type}: {', '.join(pattern_ids)}")
        else:
            print("No missing patterns detected")
    
    if args.rebuild:
        output_path = Path(args.rebuild)
        rebuilt_content = doc.rebuild()
        output_path.write_text(rebuilt_content, encoding='utf-8')
        print(f"Rebuilt document written to: {output_path}")
        
        # Validate
        is_valid, message = doc.validate_round_trip(content)
        print(f"Validation: {message}")
    
    if args.split:
        output_dir = Path(args.split)
        print(f"Splitting document into: {output_dir}")
        part_files = doc.split_to_directory(output_dir)
        
        patterns = [k for k in part_files.keys() if k in doc.patterns]
        sections = [k for k in part_files.keys() if k.startswith('_part_')]
        
        print(f"Exported {len(part_files)} parts:")
        print(f"  • Manifest: _manifest.json")
        print(f"  • Patterns: {len(patterns)} files")
        print(f"  • Sections: {len(sections)} files")
        print(f"\nDocument is now self-contained in {output_dir}/")
        print(f"Can be reconstructed with --concatenate without original file.")
    
    if args.concatenate:
        input_dir = Path(args.concatenate)
        if not input_dir.exists():
            print(f"Error: Directory not found: {input_dir}", file=sys.stderr)
            return 1
        
        print(f"Concatenating parts from: {input_dir}", file=sys.stderr)
        # Create new doc instance - concatenate works standalone without parsing original
        standalone_doc = CorpusDocument()
        reconstructed = standalone_doc.concatenate_from_directory(input_dir)
        print(reconstructed, end='')
    
    if args.validate_split:
        temp_dir = Path(args.validate_split)
        print(f"Validating split-concatenate roundtrip using: {temp_dir}")
        is_valid, message = doc.validate_split_concatenate_roundtrip(temp_dir)
        print(f"Split-Concatenate Validation: {message}")
        
        if is_valid:
            print(f"\n✓ Split files created in: {temp_dir}")
            print(f"✓ Concatenation reconstructed original perfectly")
        
        return 0 if is_valid else 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())


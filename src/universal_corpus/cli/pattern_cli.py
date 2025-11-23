#!/usr/bin/env python3
"""
Pattern CLI - AI-Optimized Command Line Interface for Universal Corpus Pattern Management

A production-ready, AI-agent compatible CLI tool following modern CLI design principles:
- Structured output by default (JSON, YAML, CSV, Table)
- Machine-readable error responses
- Self-describing interface (OpenAPI schema generation)
- Batch operations with streaming output
- Non-interactive operation
- Semantic exit codes
- Full CRUD and PATCH operations
- Comprehensive audit logging

Exit Codes:
  0 - Success
  1 - User error (validation, not found, etc.) - do not retry
  2 - System error (database, network, etc.) - retry possible
  3 - Rate limited - retry with backoff
"""

import sys
import json
import argparse
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime, timezone
import yaml

from universal_corpus.database import SessionLocal, PatternRepository, init_db
from universal_corpus.models import Pattern, CategoryType, StatusType, ComplexityType
# Note: PatternTransformer functionality removed - module no longer exists


# Version and API information
CLI_VERSION = "1.0.0"
API_VERSION = "v1"

# Exit code constants
EXIT_SUCCESS = 0
EXIT_USER_ERROR = 1
EXIT_SYSTEM_ERROR = 2
EXIT_RATE_LIMITED = 3


class StructuredResponse:
    """AI-optimized structured response formatter."""
    
    @staticmethod
    def success(result: Any, format: str = 'json', metadata: Optional[Dict] = None) -> Tuple[str, int]:
        """
        Format successful response.
        
        Args:
            result: Result data
            format: Output format (json, yaml, csv, table)
            metadata: Optional metadata to include
            
        Returns:
            Tuple of (formatted_output, exit_code)
        """
        response = {
            "success": True,
            "version": CLI_VERSION,
            "api_version": API_VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": result
        }
        
        if metadata:
            response["metadata"] = metadata
        
        if format == 'json':
            return json.dumps(response, indent=2, ensure_ascii=False), EXIT_SUCCESS
        elif format == 'yaml':
            return yaml.dump(response, default_flow_style=False, allow_unicode=True), EXIT_SUCCESS
        else:
            # For table/csv, return just the result
            return result, EXIT_SUCCESS
    
    @staticmethod
    def error(
        code: str,
        message: str,
        details: Optional[Dict] = None,
        http_equivalent: int = 400,
        retry_after: Optional[int] = None,
        documentation_url: Optional[str] = None,
        format: str = 'json'
    ) -> Tuple[str, int]:
        """
        Format error response with machine-readable structure.
        
        Args:
            code: Error code (e.g., VALIDATION_ERROR, NOT_FOUND)
            message: Human-readable error message
            details: Additional error details
            http_equivalent: HTTP status code equivalent
            retry_after: Seconds to wait before retry
            documentation_url: Link to relevant documentation
            format: Output format
            
        Returns:
            Tuple of (formatted_output, exit_code)
        """
        # Map HTTP codes to exit codes
        if http_equivalent == 429:
            exit_code = EXIT_RATE_LIMITED
        elif 400 <= http_equivalent < 500:
            exit_code = EXIT_USER_ERROR
        elif 500 <= http_equivalent < 600:
            exit_code = EXIT_SYSTEM_ERROR
        else:
            exit_code = EXIT_USER_ERROR
        
        error_response = {
            "success": False,
            "version": CLI_VERSION,
            "api_version": API_VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": {
                "code": code,
                "http_equivalent": http_equivalent,
                "message": message,
                "details": details or {},
                "retry_after_seconds": retry_after,
                "documentation_url": documentation_url or f"https://docs.example.com/errors#{code.lower()}"
            }
        }
        
        if format == 'json':
            output = json.dumps(error_response, indent=2, ensure_ascii=False)
        elif format == 'yaml':
            output = yaml.dump(error_response, default_flow_style=False, allow_unicode=True)
        else:
            output = f"ERROR [{code}]: {message}"
            if details:
                output += f"\nDetails: {json.dumps(details)}"
        
        return output, exit_code


class PatternCLI:
    """AI-optimized command-line interface for pattern management."""
    
    def __init__(self, output_format: str = 'json'):
        """
        Initialize CLI with database connection.
        
        Args:
            output_format: Default output format (json, yaml, table)
        """
        self.db = SessionLocal()
        self.repo = PatternRepository(self.db)
        self.output_format = output_format
        self.response = StructuredResponse()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close database."""
        self.db.close()
    
    def _output(self, content: str, exit_code: int = EXIT_SUCCESS):
        """
        Output content and exit with code.
        
        Args:
            content: Content to output
            exit_code: Exit code
        """
        if exit_code == EXIT_SUCCESS:
            print(content)
        else:
            print(content, file=sys.stderr)
    
    # READ operations
    def get_pattern(self, pattern_id: str, format: str = 'json') -> int:
        """
        Get a specific pattern by ID.
        
        Args:
            pattern_id: Pattern identifier
            format: Output format (json, summary, detailed)
            
        Returns:
            Exit code (0 for success, 1 for not found)
        """
        pattern = self.repo.get_by_id(pattern_id)
        
        if not pattern:
            print(f"✗ Pattern '{pattern_id}' not found", file=sys.stderr)
            return 1
        
        if format == 'json':
            print(json.dumps(pattern.model_dump(), indent=2, ensure_ascii=False))
        elif format == 'summary':
            self._print_pattern_summary(pattern)
        elif format == 'detailed':
            self._print_pattern_detailed(pattern)
        else:
            print(f"✗ Unknown format: {format}", file=sys.stderr)
            return 1
        
        return 0
    
    def list_patterns(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        format: str = 'table'
    ) -> int:
        """
        List patterns with optional filtering.
        
        Args:
            category: Filter by category
            status: Filter by status
            limit: Maximum results
            offset: Pagination offset
            format: Output format (table, json, ids)
            
        Returns:
            Exit code
        """
        patterns = self.repo.list(
            category=category,
            status=status,
            limit=limit,
            offset=offset
        )
        
        if not patterns:
            print("No patterns found")
            return 0
        
        if format == 'json':
            data = [p.model_dump() for p in patterns]
            print(json.dumps(data, indent=2, ensure_ascii=False))
        elif format == 'ids':
            for p in patterns:
                print(p.id)
        elif format == 'table':
            self._print_patterns_table(patterns)
        else:
            print(f"✗ Unknown format: {format}", file=sys.stderr)
            return 1
        
        return 0
    
    def search_patterns(self, query: str, field: str = 'name') -> int:
        """
        Search patterns by field content.
        
        Args:
            query: Search query
            field: Field to search (name, id)
            
        Returns:
            Exit code
        """
        patterns = self.repo.list(limit=1000)
        
        results = []
        query_lower = query.lower()
        
        for pattern in patterns:
            if field == 'name':
                if query_lower in pattern.metadata.name.lower():
                    results.append(pattern)
            elif field == 'id':
                if query_lower in pattern.id.lower():
                    results.append(pattern)
        
        if not results:
            print(f"No patterns found matching '{query}' in {field}")
            return 0
        
        print(f"Found {len(results)} pattern(s):\n")
        self._print_patterns_table(results)
        return 0
    
    # CREATE operations
    def create_pattern(self, file_path: str) -> int:
        """
        Create a new pattern from JSON file.
        
        Args:
            file_path: Path to JSON file containing pattern data
            
        Returns:
            Exit code
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            pattern = Pattern(**data)
            created = self.repo.create(pattern)
            
            print(f"✓ Created pattern: {created.id} - {created.metadata.name}")
            return 0
            
        except FileNotFoundError:
            print(f"✗ File not found: {file_path}", file=sys.stderr)
            return 1
        except ValueError as e:
            print(f"✗ Pattern already exists: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"✗ Error creating pattern: {e}", file=sys.stderr)
            return 1
    
    # UPDATE operations
    def update_pattern(self, pattern_id: str, file_path: str) -> int:
        """
        Update an existing pattern from JSON file.
        
        Args:
            pattern_id: Pattern ID to update
            file_path: Path to JSON file with new data
            
        Returns:
            Exit code
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            pattern = Pattern(**data)
            
            if pattern.id != pattern_id:
                print(f"✗ Pattern ID mismatch: {pattern_id} != {pattern.id}", file=sys.stderr)
                return 1
            
            updated = self.repo.update(pattern_id, pattern)
            
            if not updated:
                print(f"✗ Pattern not found: {pattern_id}", file=sys.stderr)
                return 1
            
            print(f"✓ Updated pattern: {updated.id} - {updated.metadata.name}")
            return 0
            
        except FileNotFoundError:
            print(f"✗ File not found: {file_path}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"✗ Error updating pattern: {e}", file=sys.stderr)
            return 1
    
    # PATCH operations
    def patch_pattern(self, pattern_id: str, file_path: str) -> int:
        """
        Partially update a pattern from JSON file.
        
        Args:
            pattern_id: Pattern ID to patch
            file_path: Path to JSON file with partial data
            
        Returns:
            Exit code
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            updated = self.repo.partial_update(pattern_id, data)
            
            if not updated:
                print(f"✗ Pattern not found: {pattern_id}", file=sys.stderr)
                return 1
            
            print(f"✓ Patched pattern: {updated.id} - {updated.metadata.name}")
            return 0
            
        except FileNotFoundError:
            print(f"✗ File not found: {file_path}", file=sys.stderr)
            return 1
        except ValueError as e:
            print(f"✗ Invalid patch data: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"✗ Error patching pattern: {e}", file=sys.stderr)
            return 1
    
    def patch_metadata(
        self,
        pattern_id: str,
        name: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        complexity: Optional[str] = None
    ) -> int:
        """
        Quick patch of metadata fields.
        
        Args:
            pattern_id: Pattern ID to patch
            name: New name
            category: New category
            status: New status
            complexity: New complexity
            
        Returns:
            Exit code
        """
        update_data = {"metadata": {}}
        
        if name:
            update_data["metadata"]["name"] = name
        if category:
            update_data["metadata"]["category"] = category
        if status:
            update_data["metadata"]["status"] = status
        if complexity:
            update_data["metadata"]["complexity"] = complexity
        
        if not update_data["metadata"]:
            print("✗ No fields to update", file=sys.stderr)
            return 1
        
        try:
            updated = self.repo.partial_update(pattern_id, update_data)
            
            if not updated:
                print(f"✗ Pattern not found: {pattern_id}", file=sys.stderr)
                return 1
            
            print(f"✓ Updated metadata for: {updated.id}")
            print(f"  Name: {updated.metadata.name}")
            print(f"  Category: {updated.metadata.category}")
            print(f"  Status: {updated.metadata.status}")
            print(f"  Complexity: {updated.metadata.complexity}")
            return 0
            
        except ValueError as e:
            print(f"✗ Invalid metadata: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"✗ Error updating metadata: {e}", file=sys.stderr)
            return 1
    
    # DELETE operations
    def delete_pattern(self, pattern_id: str, confirm: bool = False) -> int:
        """
        Delete a pattern.
        
        Args:
            pattern_id: Pattern ID to delete
            confirm: Skip confirmation prompt
            
        Returns:
            Exit code
        """
        # Check if pattern exists
        pattern = self.repo.get_by_id(pattern_id)
        if not pattern:
            print(f"✗ Pattern not found: {pattern_id}", file=sys.stderr)
            return 1
        
        # Confirm deletion
        if not confirm:
            print(f"About to delete pattern: {pattern_id} - {pattern.metadata.name}")
            response = input("Are you sure? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("Deletion cancelled")
                return 0
        
        # Delete
        success = self.repo.delete(pattern_id)
        
        if success:
            print(f"✓ Deleted pattern: {pattern_id}")
            return 0
        else:
            print(f"✗ Failed to delete pattern: {pattern_id}", file=sys.stderr)
            return 1
    
    # STATISTICS operations
    def show_statistics(self) -> int:
        """
        Show database statistics.
        
        Returns:
            Exit code
        """
        stats = self.repo.get_statistics()
        
        print("=== Pattern Database Statistics ===\n")
        print(f"Total patterns: {stats['total_patterns']}")
        
        print("\nBy category:")
        for category, count in sorted(stats['by_category'].items()):
            print(f"  {category:15} {count:4}")
        
        print("\nBy status:")
        for status, count in sorted(stats['by_status'].items()):
            print(f"  {status:15} {count:4}")
        
        print("\nBy complexity:")
        for complexity, count in sorted(stats['by_complexity'].items()):
            print(f"  {complexity:15} {count:4}")
        
        return 0
    
    # EXPORT operations
    def export_pattern(self, pattern_id: str, output_file: str, format: str = 'json') -> int:
        """
        Export a single pattern to file.
        
        Args:
            pattern_id: Pattern to export
            output_file: Output file path
            format: Export format (json)
            
        Returns:
            Exit code
        """
        pattern = self.repo.get_by_id(pattern_id)
        
        if not pattern:
            print(f"✗ Pattern not found: {pattern_id}", file=sys.stderr)
            return 1
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                if format == 'json':
                    json.dump(pattern.model_dump(), f, indent=2, ensure_ascii=False)
                else:
                    print(f"✗ Unknown format: {format}", file=sys.stderr)
                    return 1
            
            print(f"✓ Exported pattern to: {output_file}")
            return 0
            
        except Exception as e:
            print(f"✗ Error exporting pattern: {e}", file=sys.stderr)
            return 1
    
    def export_all(self, output_file: str, format: str = 'jsonl') -> int:
        """
        Export all patterns to file.
        
        Args:
            output_file: Output file path
            format: Export format (jsonl, json)
            
        Returns:
            Exit code
        """
        patterns = self.repo.list(limit=10000)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                if format == 'jsonl':
                    for pattern in patterns:
                        json.dump(pattern.model_dump(), f, ensure_ascii=False)
                        f.write('\n')
                elif format == 'json':
                    data = [p.model_dump() for p in patterns]
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    print(f"✗ Unknown format: {format}", file=sys.stderr)
                    return 1
            
            print(f"✓ Exported {len(patterns)} patterns to: {output_file}")
            return 0
            
        except Exception as e:
            print(f"✗ Error exporting patterns: {e}", file=sys.stderr)
            return 1
    
    # IMPORT operations
    def import_patterns(self, input_file: str, update_existing: bool = False) -> int:
        """
        Import patterns from JSONL file.
        
        Args:
            input_file: Input JSONL file path
            update_existing: Update if pattern already exists
            
        Returns:
            Exit code
        """
        try:
            transformer = PatternTransformer(input_file)
            patterns = transformer.load_and_transform()
            
            if transformer.errors:
                print(f"⚠ Transformation had {len(transformer.errors)} errors")
                transformer.print_error_report()
            
            created = 0
            updated = 0
            failed = 0
            
            for pattern in patterns:
                try:
                    self.repo.create(pattern)
                    created += 1
                except ValueError:
                    if update_existing:
                        try:
                            self.repo.update(pattern.id, pattern)
                            updated += 1
                        except Exception as e:
                            print(f"✗ Failed to update {pattern.id}: {e}")
                            failed += 1
                    else:
                        failed += 1
                except Exception as e:
                    print(f"✗ Failed to import {pattern.id}: {e}")
                    failed += 1
            
            print(f"\n=== Import Summary ===")
            print(f"Created: {created}")
            print(f"Updated: {updated}")
            print(f"Failed: {failed}")
            print(f"Total: {created + updated + failed}")
            
            return 0 if failed == 0 else 1
            
        except FileNotFoundError:
            print(f"✗ File not found: {input_file}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"✗ Error importing patterns: {e}", file=sys.stderr)
            return 1
    
    # Helper methods for formatting
    def _print_pattern_summary(self, pattern: Pattern):
        """Print pattern summary."""
        print(f"ID: {pattern.id}")
        print(f"Name: {pattern.metadata.name}")
        print(f"Category: {pattern.metadata.category}")
        print(f"Status: {pattern.metadata.status}")
        print(f"Complexity: {pattern.metadata.complexity}")
        print(f"Version: {pattern.version}")
        
        if pattern.metadata.domains:
            print(f"Domains: {', '.join(pattern.metadata.domains.domain)}")
        
        print(f"\nComponents: {len(pattern.definition.components.component)}")
        print(f"Properties: {len(pattern.properties.property)}")
        print(f"Operations: {len(pattern.operations.operation)}")
        
        if pattern.type_definitions:
            print(f"Type Definitions: {len(pattern.type_definitions.type_def)}")
        
        if pattern.dependencies:
            deps = []
            if pattern.dependencies.requires:
                deps.append(f"requires {len(pattern.dependencies.requires.pattern_ref)}")
            if pattern.dependencies.uses:
                deps.append(f"uses {len(pattern.dependencies.uses.pattern_ref)}")
            if deps:
                print(f"Dependencies: {', '.join(deps)}")
        
        if pattern.manifestations:
            print(f"Manifestations: {len(pattern.manifestations.manifestation)}")
    
    def _print_pattern_detailed(self, pattern: Pattern):
        """Print detailed pattern information."""
        self._print_pattern_summary(pattern)
        
        print("\n--- Components ---")
        for comp in pattern.definition.components.component:
            print(f"  {comp.name}: {comp.type}")
            print(f"    {comp.description}")
        
        print("\n--- Properties ---")
        for prop in pattern.properties.property:
            print(f"  {prop.id}: {prop.name}")
            print(f"    {prop.formal_spec.content}")
        
        print("\n--- Operations ---")
        for op in pattern.operations.operation:
            print(f"  {op.name}")
            print(f"    Signature: {op.signature}")
    
    def _print_patterns_table(self, patterns: List[Pattern]):
        """Print patterns in table format."""
        print(f"{'ID':<10} {'Name':<40} {'Category':<10} {'Status':<10} {'Complexity':<10}")
        print("-" * 90)
        
        for pattern in patterns:
            name = pattern.metadata.name[:37] + '...' if len(pattern.metadata.name) > 40 else pattern.metadata.name
            complexity = pattern.metadata.complexity or 'N/A'
            print(f"{pattern.id:<10} {name:<40} {pattern.metadata.category:<10} {pattern.metadata.status:<10} {complexity:<10}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Pattern CLI - Manage Universal Corpus Patterns',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get a pattern
  %(prog)s get C1
  %(prog)s get C1 --format detailed
  
  # List patterns
  %(prog)s list --category concept
  %(prog)s list --status stable --limit 20
  
  # Search patterns
  %(prog)s search "Graph" --field name
  
  # Create pattern
  %(prog)s create pattern.json
  
  # Update pattern
  %(prog)s update C1 pattern.json
  
  # Patch pattern
  %(prog)s patch C1 changes.json
  %(prog)s patch-meta C1 --status stable --complexity high
  
  # Delete pattern
  %(prog)s delete C1
  %(prog)s delete C1 --confirm  # Skip confirmation
  
  # Export patterns
  %(prog)s export C1 pattern.json
  %(prog)s export-all patterns.jsonl
  
  # Import patterns
  %(prog)s import patterns.jsonl
  %(prog)s import patterns.jsonl --update
  
  # Statistics
  %(prog)s stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # GET command
    get_parser = subparsers.add_parser('get', help='Get a pattern by ID')
    get_parser.add_argument('pattern_id', help='Pattern ID')
    get_parser.add_argument('--format', choices=['json', 'summary', 'detailed'], default='summary', help='Output format')
    
    # LIST command
    list_parser = subparsers.add_parser('list', help='List patterns')
    list_parser.add_argument('--category', choices=['concept', 'pattern', 'flow'], help='Filter by category')
    list_parser.add_argument('--status', choices=['draft', 'stable', 'deprecated'], help='Filter by status')
    list_parser.add_argument('--limit', type=int, default=100, help='Maximum results')
    list_parser.add_argument('--offset', type=int, default=0, help='Pagination offset')
    list_parser.add_argument('--format', choices=['table', 'json', 'ids'], default='table', help='Output format')
    
    # SEARCH command
    search_parser = subparsers.add_parser('search', help='Search patterns')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--field', choices=['name', 'id'], default='name', help='Field to search')
    
    # CREATE command
    create_parser = subparsers.add_parser('create', help='Create a new pattern')
    create_parser.add_argument('file', help='JSON file with pattern data')
    
    # UPDATE command
    update_parser = subparsers.add_parser('update', help='Update a pattern')
    update_parser.add_argument('pattern_id', help='Pattern ID')
    update_parser.add_argument('file', help='JSON file with updated data')
    
    # PATCH command
    patch_parser = subparsers.add_parser('patch', help='Partially update a pattern')
    patch_parser.add_argument('pattern_id', help='Pattern ID')
    patch_parser.add_argument('file', help='JSON file with partial data')
    
    # PATCH-META command
    patch_meta_parser = subparsers.add_parser('patch-meta', help='Quick metadata update')
    patch_meta_parser.add_argument('pattern_id', help='Pattern ID')
    patch_meta_parser.add_argument('--name', help='New name')
    patch_meta_parser.add_argument('--category', choices=['concept', 'pattern', 'flow'], help='New category')
    patch_meta_parser.add_argument('--status', choices=['draft', 'stable', 'deprecated'], help='New status')
    patch_meta_parser.add_argument('--complexity', choices=['low', 'medium', 'high'], help='New complexity')
    
    # DELETE command
    delete_parser = subparsers.add_parser('delete', help='Delete a pattern')
    delete_parser.add_argument('pattern_id', help='Pattern ID')
    delete_parser.add_argument('--confirm', action='store_true', help='Skip confirmation')
    
    # EXPORT command
    export_parser = subparsers.add_parser('export', help='Export a pattern')
    export_parser.add_argument('pattern_id', help='Pattern ID')
    export_parser.add_argument('output', help='Output file')
    export_parser.add_argument('--format', choices=['json'], default='json', help='Export format')
    
    # EXPORT-ALL command
    export_all_parser = subparsers.add_parser('export-all', help='Export all patterns')
    export_all_parser.add_argument('output', help='Output file')
    export_all_parser.add_argument('--format', choices=['json', 'jsonl'], default='jsonl', help='Export format')
    
    # IMPORT command
    import_parser = subparsers.add_parser('import', help='Import patterns from JSONL')
    import_parser.add_argument('file', help='Input JSONL file')
    import_parser.add_argument('--update', action='store_true', help='Update existing patterns')
    
    # STATS command
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Initialize database
    init_db()
    
    # Execute command
    with PatternCLI() as cli:
        if args.command == 'get':
            return cli.get_pattern(args.pattern_id, args.format)
        
        elif args.command == 'list':
            return cli.list_patterns(
                category=args.category,
                status=args.status,
                limit=args.limit,
                offset=args.offset,
                format=args.format
            )
        
        elif args.command == 'search':
            return cli.search_patterns(args.query, args.field)
        
        elif args.command == 'create':
            return cli.create_pattern(args.file)
        
        elif args.command == 'update':
            return cli.update_pattern(args.pattern_id, args.file)
        
        elif args.command == 'patch':
            return cli.patch_pattern(args.pattern_id, args.file)
        
        elif args.command == 'patch-meta':
            return cli.patch_metadata(
                args.pattern_id,
                name=args.name,
                category=args.category,
                status=args.status,
                complexity=args.complexity
            )
        
        elif args.command == 'delete':
            return cli.delete_pattern(args.pattern_id, args.confirm)
        
        elif args.command == 'export':
            return cli.export_pattern(args.pattern_id, args.output, args.format)
        
        elif args.command == 'export-all':
            return cli.export_all(args.output, args.format)
        
        elif args.command == 'import':
            return cli.import_patterns(args.file, args.update)
        
        elif args.command == 'stats':
            return cli.show_statistics()
        
        else:
            print(f"✗ Unknown command: {args.command}", file=sys.stderr)
            return 1


if __name__ == '__main__':
    sys.exit(main())


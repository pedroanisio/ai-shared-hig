#!/usr/bin/env python3
"""
Pattern CLI - AI-Optimized Command Line Interface

Fully compliant with modern AI-agent CLI design principles:
- Structured output by default (JSON primary, YAML/CSV/Table optional)
- Machine-readable error responses with semantic exit codes
- Self-describing interface (OpenAPI schema, JSON schema)
- Batch operations with streaming output
- Non-interactive operation
- Deterministic grammar (named parameters only)
- Comprehensive audit logging

Exit Codes:
  0 - Success
  1 - User error (validation, not found) - do not retry
  2 - System error (database, network) - retry possible
  3 - Rate limited - retry with backoff

Example Usage:
  # Structured JSON output (default)
  pattern_cli_ai.py get --id=C1
  
  # Schema generation
  pattern_cli_ai.py --schema=openapi > schema.yaml
  pattern_cli_ai.py --schema=json-schema > schema.json
  
  # Batch operations
  pattern_cli_ai.py batch --input=operations.jsonl --format=jsonl
  
  # List with filtering
  pattern_cli_ai.py list --category=concept --format=json
"""

import sys
import json
import argparse
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime, timezone
import io

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from database import SessionLocal, PatternRepository, init_db
from models import Pattern, CategoryType, StatusType, ComplexityType
from transform_jsonl_to_api import PatternTransformer


# Constants
CLI_VERSION = "1.0.0"
API_VERSION = "v1"

# Exit codes (POSIX + semantic)
EXIT_SUCCESS = 0
EXIT_USER_ERROR = 1
EXIT_SYSTEM_ERROR = 2
EXIT_RATE_LIMITED = 3


class StructuredResponse:
    """AI-optimized structured response formatter following industry best practices."""
    
    @staticmethod
    def success(result: Any, format: str = 'json', metadata: Optional[Dict] = None) -> str:
        """Format successful response with version and timestamp."""
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
            return json.dumps(response, indent=2, ensure_ascii=False)
        elif format == 'yaml' and YAML_AVAILABLE:
            return yaml.dump(response, default_flow_style=False, allow_unicode=True)
        elif format == 'compact':
            return json.dumps(response, ensure_ascii=False)
        else:
            return json.dumps(response, indent=2, ensure_ascii=False)
    
    @staticmethod
    def error(
        code: str,
        message: str,
        details: Optional[Dict] = None,
        http_equivalent: int = 400,
        retry_after: Optional[int] = None,
        format: str = 'json'
    ) -> Tuple[str, int]:
        """Format error response with machine-readable structure."""
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
                "documentation_url": f"https://docs.example.com/errors#{code.lower()}"
            }
        }
        
        if format == 'json':
            output = json.dumps(error_response, indent=2, ensure_ascii=False)
        elif format == 'yaml' and YAML_AVAILABLE:
            output = yaml.dump(error_response, default_flow_style=False, allow_unicode=True)
        else:
            output = json.dumps(error_response, indent=2, ensure_ascii=False)
        
        return output, exit_code
    
    @staticmethod
    def streaming(item: Dict, format: str = 'jsonl') -> str:
        """Format streaming response item (for batch operations)."""
        if format == 'jsonl':
            return json.dumps(item, ensure_ascii=False)
        else:
            return json.dumps(item, indent=2, ensure_ascii=False)


class PatternCLI:
    """AI-optimized CLI for pattern management."""
    
    def __init__(self, output_format: str = 'json'):
        """Initialize CLI with database connection."""
        try:
            self.db = SessionLocal()
            self.repo = PatternRepository(self.db)
            self.output_format = output_format
            self.response = StructuredResponse()
        except Exception as e:
            output, code = StructuredResponse.error(
                "DATABASE_CONNECTION_ERROR",
                f"Failed to connect to database: {str(e)}",
                http_equivalent=503
            )
            print(output, file=sys.stderr)
            sys.exit(EXIT_SYSTEM_ERROR)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close database."""
        self.db.close()
    
    # READ operations
    def get_pattern(self, pattern_id: str) -> int:
        """Get a specific pattern by ID with structured output."""
        try:
            pattern = self.repo.get_by_id(pattern_id)
            
            if not pattern:
                output, code = self.response.error(
                    "NOT_FOUND",
                    f"Pattern '{pattern_id}' not found",
                    details={"pattern_id": pattern_id},
                    http_equivalent=404,
                    format=self.output_format
                )
                print(output, file=sys.stderr)
                return code
            
            result = pattern.model_dump()
            output = self.response.success(result, format=self.output_format)
            print(output)
            return EXIT_SUCCESS
            
        except Exception as e:
            output, code = self.response.error(
                "SYSTEM_ERROR",
                f"Failed to retrieve pattern: {str(e)}",
                http_equivalent=500,
                format=self.output_format
            )
            print(output, file=sys.stderr)
            return code
    
    def list_patterns(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> int:
        """List patterns with optional filtering."""
        try:
            patterns = self.repo.list(
                category=category,
                status=status,
                limit=limit,
                offset=offset
            )
            
            result = [p.model_dump() for p in patterns]
            metadata = {
                "count": len(result),
                "limit": limit,
                "offset": offset,
                "filters": {
                    "category": category,
                    "status": status
                }
            }
            
            output = self.response.success(result, format=self.output_format, metadata=metadata)
            print(output)
            return EXIT_SUCCESS
            
        except Exception as e:
            output, code = self.response.error(
                "SYSTEM_ERROR",
                f"Failed to list patterns: {str(e)}",
                http_equivalent=500,
                format=self.output_format
            )
            print(output, file=sys.stderr)
            return code
    
    def search_patterns(self, query: str, field: str = 'name') -> int:
        """Search patterns by field content."""
        try:
            patterns = self.repo.list(limit=1000)
            
            results = []
            query_lower = query.lower()
            
            for pattern in patterns:
                if field == 'name':
                    if query_lower in pattern.metadata.name.lower():
                        results.append(pattern.model_dump())
                elif field == 'id':
                    if query_lower in pattern.id.lower():
                        results.append(pattern.model_dump())
            
            metadata = {
                "query": query,
                "field": field,
                "count": len(results)
            }
            
            output = self.response.success(results, format=self.output_format, metadata=metadata)
            print(output)
            return EXIT_SUCCESS
            
        except Exception as e:
            output, code = self.response.error(
                "SYSTEM_ERROR",
                f"Search failed: {str(e)}",
                http_equivalent=500,
                format=self.output_format
            )
            print(output, file=sys.stderr)
            return code
    
    # CREATE operations
    def create_pattern(self, data: Dict) -> int:
        """Create a new pattern from data."""
        try:
            pattern = Pattern(**data)
            created = self.repo.create(pattern)
            
            result = created.model_dump()
            output = self.response.success(result, format=self.output_format)
            print(output)
            return EXIT_SUCCESS
            
        except ValueError as e:
            output, code = self.response.error(
                "ALREADY_EXISTS",
                f"Pattern already exists: {str(e)}",
                details={"pattern_id": data.get('id')},
                http_equivalent=409,
                format=self.output_format
            )
            print(output, file=sys.stderr)
            return code
        except Exception as e:
            output, code = self.response.error(
                "VALIDATION_ERROR",
                f"Invalid pattern data: {str(e)}",
                details={"data": data},
                http_equivalent=422,
                format=self.output_format
            )
            print(output, file=sys.stderr)
            return code
    
    # UPDATE operations
    def update_pattern(self, pattern_id: str, data: Dict) -> int:
        """Update an existing pattern."""
        try:
            pattern = Pattern(**data)
            
            if pattern.id != pattern_id:
                output, code = self.response.error(
                    "VALIDATION_ERROR",
                    f"Pattern ID mismatch: {pattern_id} != {pattern.id}",
                    details={"expected": pattern_id, "provided": pattern.id},
                    http_equivalent=422,
                    format=self.output_format
                )
                print(output, file=sys.stderr)
                return code
            
            updated = self.repo.update(pattern_id, pattern)
            
            if not updated:
                output, code = self.response.error(
                    "NOT_FOUND",
                    f"Pattern not found: {pattern_id}",
                    details={"pattern_id": pattern_id},
                    http_equivalent=404,
                    format=self.output_format
                )
                print(output, file=sys.stderr)
                return code
            
            result = updated.model_dump()
            output = self.response.success(result, format=self.output_format)
            print(output)
            return EXIT_SUCCESS
            
        except Exception as e:
            output, code = self.response.error(
                "VALIDATION_ERROR",
                f"Update failed: {str(e)}",
                http_equivalent=422,
                format=self.output_format
            )
            print(output, file=sys.stderr)
            return code
    
    # PATCH operations
    def patch_pattern(self, pattern_id: str, data: Dict) -> int:
        """Partially update a pattern."""
        try:
            updated = self.repo.partial_update(pattern_id, data)
            
            if not updated:
                output, code = self.response.error(
                    "NOT_FOUND",
                    f"Pattern not found: {pattern_id}",
                    details={"pattern_id": pattern_id},
                    http_equivalent=404,
                    format=self.output_format
                )
                print(output, file=sys.stderr)
                return code
            
            result = updated.model_dump()
            output = self.response.success(result, format=self.output_format)
            print(output)
            return EXIT_SUCCESS
            
        except ValueError as e:
            output, code = self.response.error(
                "VALIDATION_ERROR",
                f"Invalid patch data: {str(e)}",
                details={"pattern_id": pattern_id, "patch": data},
                http_equivalent=422,
                format=self.output_format
            )
            print(output, file=sys.stderr)
            return code
        except Exception as e:
            output, code = self.response.error(
                "SYSTEM_ERROR",
                f"Patch failed: {str(e)}",
                http_equivalent=500,
                format=self.output_format
            )
            print(output, file=sys.stderr)
            return code
    
    # DELETE operations
    def delete_pattern(self, pattern_id: str) -> int:
        """Delete a pattern (non-interactive)."""
        try:
            # Check if pattern exists
            pattern = self.repo.get_by_id(pattern_id)
            if not pattern:
                output, code = self.response.error(
                    "NOT_FOUND",
                    f"Pattern not found: {pattern_id}",
                    details={"pattern_id": pattern_id},
                    http_equivalent=404,
                    format=self.output_format
                )
                print(output, file=sys.stderr)
                return code
            
            # Delete
            success = self.repo.delete(pattern_id)
            
            if success:
                result = {"pattern_id": pattern_id, "deleted": True}
                output = self.response.success(result, format=self.output_format)
                print(output)
                return EXIT_SUCCESS
            else:
                output, code = self.response.error(
                    "SYSTEM_ERROR",
                    f"Failed to delete pattern: {pattern_id}",
                    http_equivalent=500,
                    format=self.output_format
                )
                print(output, file=sys.stderr)
                return code
                
        except Exception as e:
            output, code = self.response.error(
                "SYSTEM_ERROR",
                f"Delete failed: {str(e)}",
                http_equivalent=500,
                format=self.output_format
            )
            print(output, file=sys.stderr)
            return code
    
    # BATCH operations
    def batch_process(self, operations: List[Dict]) -> int:
        """Process multiple operations with streaming output."""
        results = []
        
        for op in operations:
            try:
                action = op.get('action')
                pattern_id = op.get('pattern_id') or op.get('id')
                data = op.get('data', {})
                
                if action == 'create':
                    try:
                        pattern = Pattern(**data)
                        created = self.repo.create(pattern)
                        result = {"operation": "create", "pattern_id": created.id, "status": "success"}
                    except Exception as e:
                        result = {"operation": "create", "pattern_id": data.get('id'), "status": "failed", "error": str(e)}
                
                elif action == 'update':
                    try:
                        pattern = Pattern(**data)
                        updated = self.repo.update(pattern_id, pattern)
                        result = {"operation": "update", "pattern_id": pattern_id, "status": "success" if updated else "not_found"}
                    except Exception as e:
                        result = {"operation": "update", "pattern_id": pattern_id, "status": "failed", "error": str(e)}
                
                elif action == 'patch':
                    try:
                        updated = self.repo.partial_update(pattern_id, data)
                        result = {"operation": "patch", "pattern_id": pattern_id, "status": "success" if updated else "not_found"}
                    except Exception as e:
                        result = {"operation": "patch", "pattern_id": pattern_id, "status": "failed", "error": str(e)}
                
                elif action == 'delete':
                    try:
                        success = self.repo.delete(pattern_id)
                        result = {"operation": "delete", "pattern_id": pattern_id, "status": "success" if success else "not_found"}
                    except Exception as e:
                        result = {"operation": "delete", "pattern_id": pattern_id, "status": "failed", "error": str(e)}
                
                else:
                    result = {"operation": action, "status": "invalid_action"}
                
                # Streaming output (one JSON object per line)
                print(self.response.streaming(result, format='jsonl'))
                results.append(result)
                
            except Exception as e:
                result = {"operation": op.get('action'), "status": "failed", "error": str(e)}
                print(self.response.streaming(result, format='jsonl'))
                results.append(result)
        
        return EXIT_SUCCESS
    
    # EXPORT operations
    def export_patterns(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        output_file: Optional[str] = None,
        compact: bool = False
    ) -> int:
        """Export patterns to JSONL format (one pattern per line)."""
        try:
            patterns = self.repo.list(
                category=category,
                status=status,
                limit=10000
            )
            
            # Open output file or use stdout
            output_stream = open(output_file, 'w', encoding='utf-8') if output_file else sys.stdout
            
            try:
                for pattern in patterns:
                    # Write each pattern as a single JSON line
                    pattern_data = pattern.model_dump()
                    
                    # Optionally remove null fields for compact export
                    if compact:
                        pattern_data = self._remove_null_fields(pattern_data)
                    
                    json_line = json.dumps(pattern_data, ensure_ascii=False)
                    print(json_line, file=output_stream)
                
                # Write success message to stderr (so it doesn't mix with JSONL output)
                size_note = " (compact mode)" if compact else ""
                if output_file:
                    sys.stderr.write(f"✅ Exported {len(patterns)} patterns to {output_file}{size_note}\n")
                else:
                    sys.stderr.write(f"✅ Exported {len(patterns)} patterns to stdout{size_note}\n")
                
                return EXIT_SUCCESS
                
            finally:
                if output_file:
                    output_stream.close()
            
        except Exception as e:
            output, code = self.response.error(
                "SYSTEM_ERROR",
                f"Export failed: {str(e)}",
                http_equivalent=500,
                format=self.output_format
            )
            print(output, file=sys.stderr)
            return code
    
    def _remove_null_fields(self, obj: Any) -> Any:
        """Recursively remove null/None fields from nested dictionaries and lists."""
        if isinstance(obj, dict):
            return {
                k: self._remove_null_fields(v)
                for k, v in obj.items()
                if v is not None and v != {} and v != []
            }
        elif isinstance(obj, list):
            return [self._remove_null_fields(item) for item in obj if item is not None]
        else:
            return obj
    
    # STATISTICS operations
    def show_statistics(self) -> int:
        """Show database statistics."""
        try:
            stats = self.repo.get_statistics()
            output = self.response.success(stats, format=self.output_format)
            print(output)
            return EXIT_SUCCESS
            
        except Exception as e:
            output, code = self.response.error(
                "SYSTEM_ERROR",
                f"Failed to retrieve statistics: {str(e)}",
                http_equivalent=500,
                format=self.output_format
            )
            print(output, file=sys.stderr)
            return code


def generate_openapi_schema() -> str:
    """Generate OpenAPI 3.0 schema for CLI."""
    schema = {
        "openapi": "3.0.0",
        "info": {
            "title": "Pattern CLI API",
            "version": CLI_VERSION,
            "description": "AI-optimized CLI for Universal Corpus Pattern management"
        },
        "servers": [
            {"url": "cli://pattern_cli_ai", "description": "Command-line interface"}
        ],
        "paths": {
            "/get": {
                "get": {
                    "summary": "Get pattern by ID",
                    "parameters": [
                        {"name": "id", "required": True, "schema": {"type": "string"}, "description": "Pattern ID"}
                    ],
                    "responses": {
                        "200": {"description": "Pattern found"},
                        "404": {"description": "Pattern not found"}
                    }
                }
            },
            "/list": {
                "get": {
                    "summary": "List patterns with filtering",
                    "parameters": [
                        {"name": "category", "schema": {"type": "string", "enum": ["concept", "pattern", "flow"]}},
                        {"name": "status", "schema": {"type": "string", "enum": ["draft", "stable", "deprecated"]}},
                        {"name": "limit", "schema": {"type": "integer", "default": 100}},
                        {"name": "offset", "schema": {"type": "integer", "default": 0}}
                    ]
                }
            },
            "/create": {
                "post": {
                    "summary": "Create new pattern",
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Pattern"}}}}
                }
            },
            "/update": {
                "put": {
                    "summary": "Update existing pattern",
                    "parameters": [{"name": "id", "required": True, "schema": {"type": "string"}}],
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Pattern"}}}}
                }
            },
            "/patch": {
                "patch": {
                    "summary": "Partially update pattern",
                    "parameters": [{"name": "id", "required": True, "schema": {"type": "string"}}],
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object"}}}}
                }
            },
            "/delete": {
                "delete": {
                    "summary": "Delete pattern",
                    "parameters": [{"name": "id", "required": True, "schema": {"type": "string"}}]
                }
            }
        },
        "components": {
            "schemas": {
                "Pattern": {
                    "type": "object",
                    "required": ["id", "version", "metadata", "definition", "properties", "operations"],
                    "properties": {
                        "id": {"type": "string", "pattern": "^[CPF][0-9]+(\\.[0-9]+)?$"},
                        "version": {"type": "string"},
                        "metadata": {"$ref": "#/components/schemas/Metadata"}
                    }
                },
                "Metadata": {
                    "type": "object",
                    "required": ["name", "category", "status"],
                    "properties": {
                        "name": {"type": "string"},
                        "category": {"type": "string", "enum": ["concept", "pattern", "flow"]},
                        "status": {"type": "string", "enum": ["draft", "stable", "deprecated"]},
                        "complexity": {"type": "string", "enum": ["low", "medium", "high"]}
                    }
                }
            }
        }
    }
    
    if YAML_AVAILABLE:
        return yaml.dump(schema, default_flow_style=False)
    else:
        return json.dumps(schema, indent=2)


def generate_json_schema() -> str:
    """Generate JSON schema for pattern data."""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Pattern",
        "type": "object",
        "required": ["id", "version", "metadata", "definition", "properties", "operations"],
        "properties": {
            "id": {
                "type": "string",
                "pattern": "^[CPF][0-9]+(\\.[0-9]+)?$",
                "description": "Unique pattern identifier"
            },
            "version": {
                "type": "string",
                "description": "Pattern version"
            },
            "metadata": {
                "type": "object",
                "required": ["name", "category", "status"],
                "properties": {
                    "name": {"type": "string"},
                    "category": {"type": "string", "enum": ["concept", "pattern", "flow"]},
                    "status": {"type": "string", "enum": ["draft", "stable", "deprecated"]},
                    "complexity": {"type": "string", "enum": ["low", "medium", "high"]}
                }
            }
        }
    }
    return json.dumps(schema, indent=2)


def list_commands() -> str:
    """List all available commands with descriptions."""
    commands = {
        "commands": [
            {"name": "get", "description": "Get pattern by ID", "parameters": ["id"]},
            {"name": "list", "description": "List patterns with filtering", "parameters": ["category", "status", "limit", "offset"]},
            {"name": "search", "description": "Search patterns", "parameters": ["query", "field"]},
            {"name": "create", "description": "Create new pattern", "parameters": ["data"]},
            {"name": "update", "description": "Update existing pattern", "parameters": ["id", "data"]},
            {"name": "patch", "description": "Partially update pattern", "parameters": ["id", "data"]},
            {"name": "delete", "description": "Delete pattern", "parameters": ["id"]},
            {"name": "batch", "description": "Process multiple operations", "parameters": ["input"]},
            {"name": "export", "description": "Export patterns to JSONL format", "parameters": ["category", "status", "output"]},
            {"name": "stats", "description": "Show database statistics", "parameters": []}
        ]
    }
    return json.dumps(commands, indent=2)


def main():
    """Main CLI entry point with AI-optimized argument parsing."""
    parser = argparse.ArgumentParser(
        description='Pattern CLI - AI-Optimized Pattern Management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
AI-Optimized Features:
  - Structured JSON output by default
  - Machine-readable error responses
  - Self-describing interface (--schema, --list-commands)
  - Batch operations with streaming output
  - Semantic exit codes (0=success, 1=user error, 2=system error, 3=rate limited)

Examples:
  # Get pattern with JSON output
  %(prog)s get --id=C1
  
  # List patterns with filtering
  %(prog)s list --category=concept --limit=10
  
  # Export to JSONL (one pattern per line)
  %(prog)s export --output=patterns.jsonl
  %(prog)s export --category=concept --output=concepts.jsonl
  %(prog)s export --category=flow > flows.jsonl
  
  # Create pattern from file
  %(prog)s create --data=@pattern.json
  
  # Patch pattern
  %(prog)s patch --id=C1 --data='{"metadata":{"status":"stable"}}'
  
  # Batch operations
  %(prog)s batch --input=@operations.jsonl
  
  # Schema generation
  %(prog)s --schema=openapi
  %(prog)s --schema=json-schema
  %(prog)s --list-commands
        """
    )
    
    # Meta commands (no database required)
    parser.add_argument('--version', action='store_true', help='Show CLI version')
    parser.add_argument('--api-version', action='store_true', help='Show API version')
    parser.add_argument('--schema', choices=['openapi', 'json-schema'], help='Generate schema')
    parser.add_argument('--list-commands', action='store_true', help='List all commands')
    
    # Global options
    parser.add_argument('--format', choices=['json', 'yaml', 'compact'], default='json', help='Output format')
    
    # Commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # GET
    get_parser = subparsers.add_parser('get', help='Get pattern by ID')
    get_parser.add_argument('--id', required=True, help='Pattern ID')
    
    # LIST
    list_parser = subparsers.add_parser('list', help='List patterns')
    list_parser.add_argument('--category', choices=['concept', 'pattern', 'flow'], help='Filter by category')
    list_parser.add_argument('--status', choices=['draft', 'stable', 'deprecated'], help='Filter by status')
    list_parser.add_argument('--limit', type=int, default=100, help='Maximum results')
    list_parser.add_argument('--offset', type=int, default=0, help='Pagination offset')
    
    # SEARCH
    search_parser = subparsers.add_parser('search', help='Search patterns')
    search_parser.add_argument('--query', required=True, help='Search query')
    search_parser.add_argument('--field', choices=['name', 'id'], default='name', help='Field to search')
    
    # CREATE
    create_parser = subparsers.add_parser('create', help='Create pattern')
    create_parser.add_argument('--data', required=True, help='Pattern data (JSON string or @file)')
    
    # UPDATE
    update_parser = subparsers.add_parser('update', help='Update pattern')
    update_parser.add_argument('--id', required=True, help='Pattern ID')
    update_parser.add_argument('--data', required=True, help='Pattern data (JSON string or @file)')
    
    # PATCH
    patch_parser = subparsers.add_parser('patch', help='Patch pattern')
    patch_parser.add_argument('--id', required=True, help='Pattern ID')
    patch_parser.add_argument('--data', required=True, help='Partial data (JSON string or @file)')
    
    # DELETE
    delete_parser = subparsers.add_parser('delete', help='Delete pattern')
    delete_parser.add_argument('--id', required=True, help='Pattern ID')
    
    # BATCH
    batch_parser = subparsers.add_parser('batch', help='Batch operations')
    batch_parser.add_argument('--input', required=True, help='Input file (JSONL format with @file)')
    
    # EXPORT
    export_parser = subparsers.add_parser('export', help='Export patterns to JSONL')
    export_parser.add_argument('--category', choices=['concept', 'pattern', 'flow'], help='Filter by category')
    export_parser.add_argument('--status', choices=['draft', 'stable', 'deprecated'], help='Filter by status')
    export_parser.add_argument('--output', help='Output file (default: stdout)')
    
    # STATS
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle meta commands (no database required)
    if args.version:
        print(json.dumps({"version": CLI_VERSION}))
        return EXIT_SUCCESS
    
    if args.api_version:
        print(json.dumps({"api_version": API_VERSION}))
        return EXIT_SUCCESS
    
    if args.schema:
        if args.schema == 'openapi':
            print(generate_openapi_schema())
        elif args.schema == 'json-schema':
            print(generate_json_schema())
        return EXIT_SUCCESS
    
    if args.list_commands:
        print(list_commands())
        return EXIT_SUCCESS
    
    if not args.command:
        parser.print_help()
        return EXIT_SUCCESS
    
    # Initialize database
    init_db()
    
    # Helper to load data from string or file
    def load_data(data_arg: str) -> Dict:
        if data_arg.startswith('@'):
            with open(data_arg[1:], 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return json.loads(data_arg)
    
    # Execute command
    with PatternCLI(output_format=args.format) as cli:
        if args.command == 'get':
            return cli.get_pattern(args.id)
        
        elif args.command == 'list':
            return cli.list_patterns(
                category=args.category,
                status=args.status,
                limit=args.limit,
                offset=args.offset
            )
        
        elif args.command == 'search':
            return cli.search_patterns(args.query, args.field)
        
        elif args.command == 'create':
            data = load_data(args.data)
            return cli.create_pattern(data)
        
        elif args.command == 'update':
            data = load_data(args.data)
            return cli.update_pattern(args.id, data)
        
        elif args.command == 'patch':
            data = load_data(args.data)
            return cli.patch_pattern(args.id, data)
        
        elif args.command == 'delete':
            return cli.delete_pattern(args.id)
        
        elif args.command == 'batch':
            if args.input.startswith('@'):
                with open(args.input[1:], 'r', encoding='utf-8') as f:
                    operations = [json.loads(line) for line in f if line.strip()]
            else:
                operations = json.loads(args.input)
            return cli.batch_process(operations)
        
        elif args.command == 'export':
            return cli.export_patterns(
                category=args.category,
                status=args.status,
                output_file=args.output
            )
        
        elif args.command == 'stats':
            return cli.show_statistics()
        
        else:
            output, code = StructuredResponse.error(
                "COMMAND_NOT_FOUND",
                f"Unknown command: {args.command}",
                http_equivalent=400,
                format=args.format
            )
            print(output, file=sys.stderr)
            return code


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        output, code = StructuredResponse.error(
            "INTERRUPTED",
            "Operation interrupted by user",
            http_equivalent=499
        )
        print(output, file=sys.stderr)
        sys.exit(EXIT_USER_ERROR)
    except Exception as e:
        output, code = StructuredResponse.error(
            "UNEXPECTED_ERROR",
            f"Unexpected error: {str(e)}",
            http_equivalent=500
        )
        print(output, file=sys.stderr)
        sys.exit(EXIT_SYSTEM_ERROR)


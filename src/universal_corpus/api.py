"""
FastAPI application for Universal Corpus Pattern management.

This API provides endpoints to create, retrieve, update, and manage patterns
conforming to the Universal Corpus XML schema.
"""

from fastapi import FastAPI, HTTPException, status, Query, Depends
from fastapi.responses import JSONResponse, Response, StreamingResponse
from typing import List, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
import json
import csv
import io
import re
from sqlalchemy.orm import Session

from universal_corpus.models import Pattern, CategoryType, StatusType
from universal_corpus.database import get_db, init_db, PatternRepository


# Initialize FastAPI application
app = FastAPI(
    title="Universal Corpus Pattern API",
    description="API for managing formal mathematical and conceptual patterns",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup."""
    init_db()


# Helper functions for XML conversion
def pattern_to_xml(pattern: Pattern) -> str:
    """
    Convert a Pattern Pydantic model to XML string matching the XSD schema.
    
    Args:
        pattern: The pattern to convert
        
    Returns:
        XML string representation
    """
    # Create root element
    root = ET.Element(
        "pattern",
        attrib={
            "xmlns": "http://universal-corpus.org/schema/v1",
            "id": pattern.id,
            "version": pattern.version
        }
    )
    
    # Metadata
    metadata_elem = ET.SubElement(root, "metadata")
    ET.SubElement(metadata_elem, "name").text = pattern.metadata.name
    ET.SubElement(metadata_elem, "category").text = pattern.metadata.category
    ET.SubElement(metadata_elem, "status").text = pattern.metadata.status
    if pattern.metadata.complexity:
        ET.SubElement(metadata_elem, "complexity").text = pattern.metadata.complexity
    if pattern.metadata.domains:
        domains_elem = ET.SubElement(metadata_elem, "domains")
        for domain in pattern.metadata.domains.domain:
            ET.SubElement(domains_elem, "domain").text = domain
    if pattern.metadata.last_updated:
        ET.SubElement(metadata_elem, "last-updated").text = pattern.metadata.last_updated
    
    # Definition
    definition_elem = ET.SubElement(root, "definition")
    tuple_notation = ET.SubElement(definition_elem, "tuple-notation")
    tuple_notation.text = pattern.definition.tuple_notation.content
    tuple_notation.set("format", pattern.definition.tuple_notation.format)
    
    components_elem = ET.SubElement(definition_elem, "components")
    for comp in pattern.definition.components.component:
        comp_elem = ET.SubElement(components_elem, "component")
        ET.SubElement(comp_elem, "name").text = comp.name
        ET.SubElement(comp_elem, "type").text = comp.type
        if comp.notation:
            ET.SubElement(comp_elem, "notation").text = comp.notation
        ET.SubElement(comp_elem, "description").text = comp.description
    
    if pattern.definition.description:
        ET.SubElement(definition_elem, "description").text = pattern.definition.description
    
    # Type definitions (optional)
    if pattern.type_definitions:
        type_defs_elem = ET.SubElement(root, "type-definitions")
        for typedef in pattern.type_definitions.type_def:
            typedef_elem = ET.SubElement(type_defs_elem, "type-def")
            ET.SubElement(typedef_elem, "name").text = typedef.name
            definition = ET.SubElement(typedef_elem, "definition")
            definition.text = typedef.definition.content
            definition.set("format", typedef.definition.format)
            if typedef.description:
                ET.SubElement(typedef_elem, "description").text = typedef.description
    
    # Properties
    properties_elem = ET.SubElement(root, "properties")
    for prop in pattern.properties.property:
        prop_elem = ET.SubElement(properties_elem, "property", attrib={"id": prop.id})
        ET.SubElement(prop_elem, "name").text = prop.name
        formal_spec = ET.SubElement(prop_elem, "formal-spec")
        formal_spec.text = prop.formal_spec.content
        formal_spec.set("format", prop.formal_spec.format)
        if prop.description:
            ET.SubElement(prop_elem, "description").text = prop.description
        if prop.invariants:
            invariants_elem = ET.SubElement(prop_elem, "invariants")
            for inv in prop.invariants.invariant:
                inv_elem = ET.SubElement(invariants_elem, "invariant")
                inv_elem.text = inv.content
                inv_elem.set("format", inv.format)
    
    # Operations
    operations_elem = ET.SubElement(root, "operations")
    for op in pattern.operations.operation:
        op_elem = ET.SubElement(operations_elem, "operation")
        ET.SubElement(op_elem, "name").text = op.name
        ET.SubElement(op_elem, "signature").text = op.signature
        formal_def = ET.SubElement(op_elem, "formal-definition")
        formal_def.text = op.formal_definition.content
        formal_def.set("format", op.formal_definition.format)
        
        if op.preconditions:
            precond_elem = ET.SubElement(op_elem, "preconditions")
            for cond in op.preconditions.condition:
                cond_elem = ET.SubElement(precond_elem, "condition")
                cond_elem.text = cond.content
                cond_elem.set("format", cond.format)
        
        if op.postconditions:
            postcond_elem = ET.SubElement(op_elem, "postconditions")
            for cond in op.postconditions.condition:
                cond_elem = ET.SubElement(postcond_elem, "condition")
                cond_elem.text = cond.content
                cond_elem.set("format", cond.format)
        
        if op.effects:
            effects_elem = ET.SubElement(op_elem, "effects")
            for effect in op.effects.effect:
                ET.SubElement(effects_elem, "effect").text = effect
    
    # Dependencies (optional)
    if pattern.dependencies:
        deps_elem = ET.SubElement(root, "dependencies")
        if pattern.dependencies.requires:
            requires_elem = ET.SubElement(deps_elem, "requires")
            for ref in pattern.dependencies.requires.pattern_ref:
                ET.SubElement(requires_elem, "pattern-ref").text = ref
        if pattern.dependencies.uses:
            uses_elem = ET.SubElement(deps_elem, "uses")
            for ref in pattern.dependencies.uses.pattern_ref:
                ET.SubElement(uses_elem, "pattern-ref").text = ref
        if pattern.dependencies.specializes:
            specializes_elem = ET.SubElement(deps_elem, "specializes")
            for ref in pattern.dependencies.specializes.pattern_ref:
                ET.SubElement(specializes_elem, "pattern-ref").text = ref
        if pattern.dependencies.specialized_by:
            specialized_by_elem = ET.SubElement(deps_elem, "specialized-by")
            for ref in pattern.dependencies.specialized_by.pattern_ref:
                ET.SubElement(specialized_by_elem, "pattern-ref").text = ref
    
    # Manifestations (optional)
    if pattern.manifestations:
        manifestations_elem = ET.SubElement(root, "manifestations")
        for manif in pattern.manifestations.manifestation:
            manif_elem = ET.SubElement(manifestations_elem, "manifestation")
            ET.SubElement(manif_elem, "name").text = manif.name
            if manif.description:
                ET.SubElement(manif_elem, "description").text = manif.description
    
    # Convert to pretty-printed string
    xml_string = ET.tostring(root, encoding="unicode")
    dom = minidom.parseString(xml_string)
    return dom.toprettyxml(indent="  ")


# API Endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "api": "Universal Corpus Pattern API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "create_pattern": "POST /patterns",
            "list_patterns": "GET /patterns",
            "get_pattern": "GET /patterns/{pattern_id}",
            "get_pattern_xml": "GET /patterns/{pattern_id}/xml",
            "update_pattern": "PUT /patterns/{pattern_id}",
            "partial_update_pattern": "PATCH /patterns/{pattern_id}",
            "delete_pattern": "DELETE /patterns/{pattern_id}",
            "get_dependencies": "GET /patterns/{pattern_id}/dependencies",
            "export_csv": "GET /export/csv",
            "statistics": "GET /statistics",
            "health": "GET /health"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    repo = PatternRepository(db)
    return {
        "status": "healthy",
        "patterns_count": repo.count()
    }


@app.post(
    "/patterns",
    response_model=Pattern,
    status_code=status.HTTP_201_CREATED,
    tags=["Patterns"]
)
async def create_pattern(pattern: Pattern, db: Session = Depends(get_db)):
    """
    Create a new pattern.
    
    Args:
        pattern: Pattern object conforming to the schema
        db: Database session
        
    Returns:
        The created pattern
        
    Raises:
        HTTPException: If pattern ID already exists
    """
    repo = PatternRepository(db)
    try:
        return repo.create(pattern)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@app.get("/patterns", response_model=List[Pattern], tags=["Patterns"])
async def list_patterns(
    category: Optional[CategoryType] = Query(None, description="Filter by category"),
    status_filter: Optional[StatusType] = Query(None, alias="status", description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    List all patterns with optional filtering.
    
    Args:
        category: Optional category filter
        status_filter: Optional status filter
        limit: Maximum number of results
        offset: Pagination offset
        db: Database session
        
    Returns:
        List of patterns matching the filters
    """
    repo = PatternRepository(db)
    return repo.list(
        category=category,
        status=status_filter,
        limit=limit,
        offset=offset
    )


@app.get("/patterns/{pattern_id}", response_model=Pattern, tags=["Patterns"])
async def get_pattern(pattern_id: str, db: Session = Depends(get_db)):
    """
    Get a specific pattern by ID.
    
    Args:
        pattern_id: Pattern identifier
        db: Database session
        
    Returns:
        The requested pattern
        
    Raises:
        HTTPException: If pattern not found
    """
    repo = PatternRepository(db)
    pattern = repo.get_by_id(pattern_id)
    
    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pattern with ID '{pattern_id}' not found"
        )
    
    return pattern


@app.get("/patterns/{pattern_id}/xml", tags=["Patterns"])
async def get_pattern_xml(pattern_id: str, db: Session = Depends(get_db)):
    """
    Get a specific pattern as XML.
    
    Args:
        pattern_id: Pattern identifier
        db: Database session
        
    Returns:
        XML representation of the pattern
        
    Raises:
        HTTPException: If pattern not found
    """
    repo = PatternRepository(db)
    pattern = repo.get_by_id(pattern_id)
    
    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pattern with ID '{pattern_id}' not found"
        )
    
    xml_content = pattern_to_xml(pattern)
    
    return Response(content=xml_content, media_type="application/xml")


@app.put("/patterns/{pattern_id}", response_model=Pattern, tags=["Patterns"])
async def update_pattern(pattern_id: str, pattern: Pattern, db: Session = Depends(get_db)):
    """
    Update an existing pattern.
    
    Args:
        pattern_id: Pattern identifier
        pattern: Updated pattern object
        db: Database session
        
    Returns:
        The updated pattern
        
    Raises:
        HTTPException: If pattern not found or ID mismatch
    """
    repo = PatternRepository(db)
    
    try:
        updated_pattern = repo.update(pattern_id, pattern)
        if not updated_pattern:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pattern with ID '{pattern_id}' not found"
            )
        return updated_pattern
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.patch("/patterns/{pattern_id}", response_model=Pattern, tags=["Patterns"])
async def partial_update_pattern(
    pattern_id: str, 
    update_data: dict,
    db: Session = Depends(get_db)
):
    """
    Partially update an existing pattern.
    
    Only updates the fields provided in the request body. Nested objects
    are deep-merged, so you can update specific nested fields without
    replacing the entire object.
    
    Examples:
        Update status only:
            {"metadata": {"status": "deprecated"}}
        
        Update complexity and add a new property:
            {
                "metadata": {"complexity": "high"},
                "properties": {
                    "property": [
                        {"id": "P.P1.5", "name": "New Property", ...}
                    ]
                }
            }
        
        Update operation signature:
            {
                "operations": {
                    "operation": [
                        {"name": "Execute", "signature": "execute: Input → Output"}
                    ]
                }
            }
    
    Args:
        pattern_id: Pattern identifier
        update_data: Dictionary with fields to update (partial)
        db: Database session
        
    Returns:
        The updated pattern
        
    Raises:
        HTTPException: If pattern not found or invalid update data
    """
    repo = PatternRepository(db)
    
    try:
        updated_pattern = repo.partial_update(pattern_id, update_data)
        if not updated_pattern:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pattern with ID '{pattern_id}' not found"
            )
        return updated_pattern
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.delete("/patterns/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Patterns"])
async def delete_pattern(pattern_id: str, db: Session = Depends(get_db)):
    """
    Delete a pattern.
    
    Args:
        pattern_id: Pattern identifier
        db: Database session
        
    Raises:
        HTTPException: If pattern not found
    """
    repo = PatternRepository(db)
    
    if not repo.delete(pattern_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pattern with ID '{pattern_id}' not found"
        )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/patterns/{pattern_id}/dependencies", tags=["Patterns"])
async def get_pattern_dependencies(pattern_id: str, db: Session = Depends(get_db)):
    """
    Get all dependencies for a pattern.
    
    Args:
        pattern_id: Pattern identifier
        db: Database session
        
    Returns:
        Dependencies information
        
    Raises:
        HTTPException: If pattern not found
    """
    repo = PatternRepository(db)
    pattern = repo.get_by_id(pattern_id)
    
    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pattern with ID '{pattern_id}' not found"
        )
    
    return pattern.dependencies if pattern.dependencies else {}


@app.get("/export/csv", tags=["Export"])
async def export_patterns_csv(
    category: Optional[CategoryType] = Query(None, description="Filter by category"),
    status_filter: Optional[StatusType] = Query(None, alias="status", description="Filter by status"),
    db: Session = Depends(get_db)
):
    """
    Export all patterns to a comprehensive CSV file with complete details.
    
    This endpoint returns a single CSV file containing ALL pattern data including:
    - Pattern metadata (id, name, category, status, complexity, version)
    - All components with their types, notations, and descriptions
    - All type definitions with formal specifications
    - All properties with formal specs and invariants
    - All operations with signatures, formal definitions, and conditions
    - All manifestations
    - All dependencies
    - Domains and other metadata
    
    Args:
        category: Optional category filter
        status_filter: Optional status filter
        db: Database session
        
    Returns:
        CSV file with complete pattern data (all nested details included)
    """
    repo = PatternRepository(db)
    patterns = repo.list(
        category=category,
        status=status_filter,
        limit=10000,  # Get all patterns
        offset=0
    )
    
    # Create CSV in memory with proper quoting for fields containing special characters
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    
    # Write comprehensive header with all detail columns
    writer.writerow([
        # Pattern metadata
        'pattern_id',
        'pattern_name',
        'pattern_type',
        'category',
        'status',
        'complexity',
        'version',
        'domains',
        'last_updated',
        # Definition
        'tuple_notation',
        'tuple_notation_format',
        'definition_description',
        # Components (all details)
        'components',
        # Type definitions (all details)
        'type_definitions',
        # Properties (all details)
        'properties',
        # Operations (all details)
        'operations',
        # Dependencies
        'requires_dependencies',
        'uses_dependencies',
        'specializes_dependencies',
        'specialized_by_dependencies',
        # Manifestations
        'manifestations'
    ])
    
    # Helper function to clean text for CSV (remove newlines and normalize whitespace)
    def clean_text(text: str) -> str:
        """Remove newlines and normalize whitespace for CSV output."""
        if not text:
            return ""
        # Replace newlines with spaces
        text = text.replace('\n', ' ').replace('\r', ' ')
        # Normalize multiple spaces to single space
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    # Write pattern data
    for pattern in patterns:
        # Pattern type based on ID prefix
        pattern_type = "concept" if pattern.id.startswith('C') else "flow" if pattern.id.startswith('F') else "pattern"
        
        # Extract tuple notation (clean it)
        tuple_notation = clean_text(pattern.definition.tuple_notation.content)
        tuple_notation_format = pattern.definition.tuple_notation.format
        
        # Extract description (clean it)
        definition_description = clean_text(pattern.definition.description or "")
        
        # Extract domains
        domains = "; ".join(pattern.metadata.domains.domain) if pattern.metadata.domains else ""
        
        # Build components string with full details
        components_list = []
        for comp in pattern.definition.components.component:
            comp_str = f"{comp.name}[type: {clean_text(comp.type)}"
            if comp.notation:
                comp_str += f", notation: {clean_text(comp.notation)}"
            comp_str += f", desc: {clean_text(comp.description)}]"
            components_list.append(comp_str)
        components_str = " | ".join(components_list)
        
        # Build type definitions string with full details
        type_defs_list = []
        if pattern.type_definitions:
            for td in pattern.type_definitions.type_def:
                td_str = f"{td.name}[def: {clean_text(td.definition.content)}, format: {td.definition.format}"
                if td.description:
                    td_str += f", desc: {clean_text(td.description)}"
                td_str += "]"
                type_defs_list.append(td_str)
        type_defs_str = " | ".join(type_defs_list)
        
        # Build properties string with full details
        properties_list = []
        for prop in pattern.properties.property:
            prop_str = f"{prop.id}:{prop.name}[spec: {clean_text(prop.formal_spec.content)}, format: {prop.formal_spec.format}"
            if prop.description:
                prop_str += f", desc: {clean_text(prop.description)}"
            if prop.invariants:
                inv_list = [f"{clean_text(inv.content)}({inv.format})" for inv in prop.invariants.invariant]
                prop_str += f", invariants: {'; '.join(inv_list)}"
            prop_str += "]"
            properties_list.append(prop_str)
        properties_str = " | ".join(properties_list)
        
        # Build operations string with full details
        operations_list = []
        for op in pattern.operations.operation:
            op_str = f"{op.name}[sig: {clean_text(op.signature)}, def: {clean_text(op.formal_definition.content)}, format: {op.formal_definition.format}"
            
            if op.preconditions:
                precond_list = [f"{clean_text(cond.content)}({cond.format})" for cond in op.preconditions.condition]
                op_str += f", preconditions: {'; '.join(precond_list)}"
            
            if op.postconditions:
                postcond_list = [f"{clean_text(cond.content)}({cond.format})" for cond in op.postconditions.condition]
                op_str += f", postconditions: {'; '.join(postcond_list)}"
            
            if op.effects:
                effects_cleaned = [clean_text(effect) for effect in op.effects.effect]
                op_str += f", effects: {'; '.join(effects_cleaned)}"
            
            op_str += "]"
            operations_list.append(op_str)
        operations_str = " | ".join(operations_list)
        
        # Extract dependencies
        requires_deps = ""
        uses_deps = ""
        specializes_deps = ""
        specialized_by_deps = ""
        
        if pattern.dependencies:
            if pattern.dependencies.requires:
                requires_deps = "; ".join(pattern.dependencies.requires.pattern_ref)
            if pattern.dependencies.uses:
                uses_deps = "; ".join(pattern.dependencies.uses.pattern_ref)
            if pattern.dependencies.specializes:
                specializes_deps = "; ".join(pattern.dependencies.specializes.pattern_ref)
            if pattern.dependencies.specialized_by:
                specialized_by_deps = "; ".join(pattern.dependencies.specialized_by.pattern_ref)
        
        # Build manifestations string
        manifestations_list = []
        if pattern.manifestations:
            for manif in pattern.manifestations.manifestation:
                manif_str = f"{clean_text(manif.name)}"
                if manif.description:
                    manif_str += f"[{clean_text(manif.description)}]"
                manifestations_list.append(manif_str)
        manifestations_str = " | ".join(manifestations_list)
        
        # Write row with all details
        writer.writerow([
            pattern.id,
            pattern.metadata.name,
            pattern_type,
            pattern.metadata.category,
            pattern.metadata.status,
            pattern.metadata.complexity or "",
            pattern.version,
            domains,
            pattern.metadata.last_updated or "",
            tuple_notation,
            tuple_notation_format,
            definition_description,
            components_str,
            type_defs_str,
            properties_str,
            operations_str,
            requires_deps,
            uses_deps,
            specializes_deps,
            specialized_by_deps,
            manifestations_str
        ])
    
    # Prepare response
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=patterns_complete_export.csv"
        }
    )


@app.get("/export/jsonl", tags=["Export"])
async def export_patterns_jsonl(
    category: Optional[CategoryType] = Query(None, description="Filter by category"),
    status_filter: Optional[StatusType] = Query(None, alias="status", description="Filter by status"),
    db: Session = Depends(get_db)
):
    """
    Export all patterns to JSONL (JSON Lines) format.
    
    JSONL format has one complete JSON object per line, making it ideal for:
    - Streaming large datasets
    - Processing records one at a time
    - Incremental loading
    - Line-by-line analysis
    
    Each line is a complete Pattern object with all nested data.
    
    Args:
        category: Optional category filter
        status_filter: Optional status filter
        db: Database session
        
    Returns:
        JSONL file where each line is a complete pattern as JSON
    """
    repo = PatternRepository(db)
    patterns = repo.list(
        category=category,
        status=status_filter,
        limit=10000,  # Get all patterns
        offset=0
    )
    
    # Generate JSONL content (one JSON object per line)
    def generate_jsonl():
        for pattern in patterns:
            # Convert pattern to dict and serialize to JSON
            pattern_dict = pattern.model_dump(mode='json', exclude_none=False)
            yield json.dumps(pattern_dict, ensure_ascii=False) + '\n'
    
    # Return streaming response with JSONL content
    return StreamingResponse(
        generate_jsonl(),
        media_type="application/x-ndjson",  # JSONL media type
        headers={
            "Content-Disposition": "attachment; filename=patterns.jsonl"
        }
    )


@app.get("/statistics", tags=["Statistics"])
async def get_statistics(db: Session = Depends(get_db)):
    """Get statistics about the pattern collection."""
    repo = PatternRepository(db)
    return repo.get_statistics()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


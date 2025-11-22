"""
FastAPI application for Universal Corpus Pattern management.

This API provides endpoints to create, retrieve, update, and manage patterns
conforming to the Universal Corpus XML schema.
"""

from fastapi import FastAPI, HTTPException, status, Query, Depends
from fastapi.responses import JSONResponse, Response
from typing import List, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
import json
from sqlalchemy.orm import Session

from models import Pattern, CategoryType, StatusType
from database import get_db, init_db, PatternRepository


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


@app.get("/statistics", tags=["Statistics"])
async def get_statistics(db: Session = Depends(get_db)):
    """Get statistics about the pattern collection."""
    repo = PatternRepository(db)
    return repo.get_statistics()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


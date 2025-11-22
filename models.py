"""
Pydantic models representing the Universal Corpus Pattern XML Schema.

This module provides complete type-safe models with validation matching the XSD constraints.
All enumerations, patterns, and cardinality rules from the schema are enforced.
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator
import re


# Enumerations matching XSD restrictions
CategoryType = Literal["concept", "pattern", "flow"]
StatusType = Literal["draft", "stable", "deprecated"]
ComplexityType = Literal["low", "medium", "high"]


class MathExpression(BaseModel):
    """Mathematical expression with optional format specification (defaults to latex)."""
    
    content: str = Field(..., description="The mathematical expression content")
    format: str = Field(default="latex", description="Format of the expression")
    
    class Config:
        populate_by_name = True


class Domains(BaseModel):
    """Collection of domain strings."""
    
    domain: List[str] = Field(..., min_length=1, description="List of domains")


class Metadata(BaseModel):
    """Pattern metadata including name, category, status, and optional complexity."""
    
    name: str = Field(..., description="Human-readable name of the pattern")
    category: CategoryType = Field(..., description="Pattern category")
    status: StatusType = Field(..., description="Development status")
    complexity: Optional[ComplexityType] = Field(None, description="Complexity level")
    domains: Optional[Domains] = Field(None, description="Applicable domains")
    last_updated: Optional[str] = Field(None, description="Last update date (ISO format)")
    
    @field_validator('last_updated')
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate that last_updated is in ISO date format (YYYY-MM-DD)."""
        if v is not None:
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', v):
                raise ValueError('last_updated must be in ISO date format (YYYY-MM-DD)')
        return v


class Component(BaseModel):
    """A component of a pattern definition with type and notation."""
    
    name: str = Field(..., description="Component name")
    type: str = Field(..., description="Type specification")
    notation: Optional[str] = Field(None, description="Mathematical notation")
    description: str = Field(..., description="Component description")


class Components(BaseModel):
    """Collection of pattern components."""
    
    component: List[Component] = Field(..., min_length=1, description="List of components")


class Definition(BaseModel):
    """Formal definition of a pattern including tuple notation and components."""
    
    tuple_notation: MathExpression = Field(..., alias="tuple-notation", description="Tuple notation")
    components: Components = Field(..., description="Pattern components")
    description: Optional[str] = Field(None, description="Optional description")
    
    class Config:
        populate_by_name = True


class TypeDef(BaseModel):
    """Type definition with formal mathematical specification."""
    
    name: str = Field(..., description="Type name")
    definition: MathExpression = Field(..., description="Formal type definition")
    description: Optional[str] = Field(None, description="Optional description")


class TypeDefinitions(BaseModel):
    """Collection of type definitions."""
    
    type_def: List[TypeDef] = Field(..., min_length=1, alias="type-def", description="List of type definitions")
    
    class Config:
        populate_by_name = True


class Invariants(BaseModel):
    """Collection of invariant expressions."""
    
    invariant: List[MathExpression] = Field(..., min_length=1, description="List of invariants")


class Property(BaseModel):
    """A property of a pattern with formal specification."""
    
    id: str = Field(..., description="Unique property identifier")
    name: str = Field(..., description="Property name")
    formal_spec: MathExpression = Field(..., alias="formal-spec", description="Formal specification")
    description: Optional[str] = Field(None, description="Optional description")
    invariants: Optional[Invariants] = Field(None, description="Optional invariants")
    
    class Config:
        populate_by_name = True


class Properties(BaseModel):
    """Collection of pattern properties."""
    
    property: List[Property] = Field(..., min_length=1, description="List of properties")


class Conditions(BaseModel):
    """
    Collection of condition expressions for preconditions/postconditions.
    
    Conditions are formal mathematical expressions that must hold before (preconditions)
    or after (postconditions) an operation executes.
    
    Example:
        Precondition: "x > 0 ∧ buffer ≠ ∅"
        Postcondition: "result = f(x) ∧ buffer unchanged"
    """
    
    condition: List[MathExpression] = Field(..., min_length=1, description="List of conditions")


class Effects(BaseModel):
    """Collection of effect descriptions."""
    
    effect: List[str] = Field(..., min_length=1, description="List of effects")


class Operation(BaseModel):
    """
    An operation with signature, formal definition, and optional conditions.
    
    Operations define the behavior of patterns with:
    - **Signature**: Type-level specification of inputs/outputs
    - **Formal Definition**: Mathematical definition of the operation
    - **Preconditions**: Conditions that must hold before execution
    - **Postconditions**: Conditions that must hold after execution
    - **Effects**: Observable side effects of the operation
    
    Example:
        name: "Push"
        signature: "push(item: T) → Stack⟨T⟩"
        formal_definition: "push(item, stack) = stack ++ [item]"
        preconditions: ["stack.size < MAX_SIZE"]
        postconditions: ["result.size = stack.size + 1", "result.top = item"]
        effects: ["Stack state modified", "Size counter incremented"]
    """
    
    name: str = Field(..., description="Operation name")
    signature: str = Field(..., description="Operation signature (e.g., 'op(x: T) → R')")
    formal_definition: MathExpression = Field(..., alias="formal-definition", description="Formal mathematical definition")
    preconditions: Optional[Conditions] = Field(None, description="Conditions that must hold before execution")
    postconditions: Optional[Conditions] = Field(None, description="Conditions that must hold after execution")
    effects: Optional[Effects] = Field(None, description="Observable side effects")
    
    class Config:
        populate_by_name = True


class Operations(BaseModel):
    """Collection of operations."""
    
    operation: List[Operation] = Field(..., min_length=1, description="List of operations")


class PatternRefs(BaseModel):
    """Collection of pattern reference identifiers."""
    
    pattern_ref: List[str] = Field(..., min_length=1, alias="pattern-ref", description="List of pattern IDs")
    
    @field_validator('pattern_ref')
    @classmethod
    def validate_pattern_ids(cls, v: List[str]) -> List[str]:
        """Validate that pattern references match the PatternIdType pattern."""
        pattern = re.compile(r'^[CPF][0-9]+(\.[0-9]+)?$')
        for ref in v:
            if not pattern.match(ref):
                raise ValueError(f'Pattern ID "{ref}" must match pattern [CPF][0-9]+(.[0-9]+)?')
        return v
    
    class Config:
        populate_by_name = True


class Dependencies(BaseModel):
    """Pattern dependencies including requires, uses, specializes, and specialized-by relationships."""
    
    requires: Optional[PatternRefs] = Field(None, description="Required patterns")
    uses: Optional[PatternRefs] = Field(None, description="Used patterns")
    specializes: Optional[PatternRefs] = Field(None, description="Patterns this specializes")
    specialized_by: Optional[PatternRefs] = Field(None, alias="specialized-by", description="Patterns that specialize this")
    
    class Config:
        populate_by_name = True


class Manifestation(BaseModel):
    """A real-world manifestation of the pattern."""
    
    name: str = Field(..., description="Manifestation name")
    description: Optional[str] = Field(None, description="Optional description")


class Manifestations(BaseModel):
    """Collection of pattern manifestations."""
    
    manifestation: List[Manifestation] = Field(..., min_length=1, description="List of manifestations")


class Pattern(BaseModel):
    """
    Complete pattern definition matching the Universal Corpus XSD schema.
    
    A pattern represents a formal mathematical or conceptual structure with
    metadata, formal definitions, properties, operations, and optional dependencies.
    """
    
    id: str = Field(..., description="Pattern identifier")
    version: str = Field(..., description="Pattern version")
    metadata: Metadata = Field(..., description="Pattern metadata")
    definition: Definition = Field(..., description="Formal definition")
    type_definitions: Optional[TypeDefinitions] = Field(None, alias="type-definitions", description="Optional type definitions")
    properties: Properties = Field(..., description="Pattern properties")
    operations: Operations = Field(..., description="Pattern operations")
    dependencies: Optional[Dependencies] = Field(None, description="Optional dependencies")
    manifestations: Optional[Manifestations] = Field(None, description="Optional manifestations")
    
    @field_validator('id')
    @classmethod
    def validate_pattern_id(cls, v: str) -> str:
        """Validate that id matches the PatternIdType pattern: [CPF][0-9]+(.[0-9]+)?"""
        if not re.match(r'^[CPF][0-9]+(\.[0-9]+)?$', v):
            raise ValueError('Pattern ID must match pattern [CPF][0-9]+(.[0-9]+)?')
        return v
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "C1",
                "version": "1.1",
                "metadata": {
                    "name": "Graph Structure",
                    "category": "concept",
                    "status": "stable",
                    "complexity": "medium"
                },
                "definition": {
                    "tuple-notation": {
                        "content": "$G = (N, E, \\lambda_n, \\lambda_e)$",
                        "format": "latex"
                    },
                    "components": {
                        "component": [
                            {
                                "name": "\\lambda_n",
                                "type": "N → Label_n",
                                "notation": "\\lambda_n",
                                "description": "**node labeling function**"
                            }
                        ]
                    }
                },
                "properties": {
                    "property": [
                        {
                            "id": "P.C1.1",
                            "name": "Connectivity",
                            "formal-spec": {
                                "content": "connected(G) ⇔ ∀n₁, n₂ ∈ N: ∃ path from n₁ to n₂",
                                "format": "latex"
                            }
                        }
                    ]
                },
                "operations": {
                    "operation": [
                        {
                            "name": "Traverse",
                            "signature": "traverse(n: N, depth: ℕ) → Set⟨N⟩",
                            "formal-definition": {
                                "content": "traverse(n: N, depth: ℕ) → Set⟨N⟩ = {n' ∈ N : distance(n, n') ≤ depth}",
                                "format": "latex"
                            },
                            "preconditions": {
                                "condition": [
                                    {
                                        "content": "n ∈ N ∧ depth ≥ 0",
                                        "format": "latex"
                                    }
                                ]
                            },
                            "postconditions": {
                                "condition": [
                                    {
                                        "content": "∀n' ∈ result: distance(n, n') ≤ depth",
                                        "format": "latex"
                                    },
                                    {
                                        "content": "n ∈ result",
                                        "format": "latex"
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }


"""
Compact format for sharing Universal Corpus patterns with AI/LLMs.

This module provides token-efficient serialization that preserves all semantic
information while drastically reducing token consumption for AI interactions.

Design Principles:
- Short but meaningful keys (e.g., 'id' stays 'id', 'formal_spec' becomes 'spec')
- Inline format notation (default latex assumed, only specify if different)
- Flatten nested structures where semantically clear
- Preserve all essential information for reconstruction

Token Savings: ~70-80% reduction compared to full JSONL format
"""

from typing import Dict, List, Any, Optional
from universal_corpus.models import Pattern
import json


def pattern_to_compact(pattern: Pattern) -> Dict[str, Any]:
    """
    Convert a full Pattern to compact format optimized for AI/LLM consumption.
    
    Compact Format Structure:
    {
        "id": "C1",
        "v": "1.1",                           # version
        "name": "Graph Structure",
        "cat": "concept",                     # category
        "status": "stable",
        "cx": "medium",                       # complexity
        "domains": ["Data Structures", ...],
        "updated": "2025-11-23",
        "def": "G = (N, E, λ_n, λ_e)",       # tuple notation (latex assumed)
        "desc": "A graph structure...",       # definition description
        "comps": [                            # components
            {"n": "λ_n", "t": "N → Label_n", "d": "node labeling function"},
            ...
        ],
        "types": [                            # type definitions (if any)
            {"n": "Graph", "def": "G = ...", "d": "description"}
        ],
        "props": [                            # properties
            {
                "id": "P.C1.1",
                "n": "Connectivity",
                "spec": "connected(G) ⇔ ∀n₁, n₂...",
                "d": "description",
                "inv": ["inv1", "inv2"]       # invariants (if any)
            }
        ],
        "ops": [                              # operations
            {
                "n": "Traverse",
                "sig": "traverse(n: N) → Set⟨N⟩",
                "def": "traverse(n) = ...",
                "pre": ["n ∈ N", ...],        # preconditions (if any)
                "post": ["∀n' ∈ result..."],  # postconditions (if any)
                "fx": ["effect1", ...]         # effects (if any)
            }
        ],
        "deps": {                             # dependencies (if any)
            "req": ["P1", "P2"],              # requires
            "use": ["C1"],                     # uses
            "spec": ["P.Base"],                # specializes
            "by": ["P.Derived"]                # specialized_by
        },
        "manif": [                            # manifestations (if any)
            {"n": "Knowledge graphs", "d": "semantic web, ontologies"}
        ]
    }
    
    Args:
        pattern: Full Pattern object
        
    Returns:
        Compact dictionary representation
    """
    compact = {
        "id": pattern.id,
        "v": pattern.version,
        "name": pattern.metadata.name,
        "cat": pattern.metadata.category,
        "status": pattern.metadata.status,
    }
    
    # Optional metadata fields
    if pattern.metadata.complexity:
        compact["cx"] = pattern.metadata.complexity
    
    if pattern.metadata.domains:
        compact["domains"] = pattern.metadata.domains.domain
    
    if pattern.metadata.last_updated:
        compact["updated"] = pattern.metadata.last_updated
    
    # Definition - tuple notation (assume latex, strip format unless different)
    tuple_content = pattern.definition.tuple_notation.content
    tuple_format = pattern.definition.tuple_notation.format
    
    if tuple_format == "latex":
        compact["def"] = tuple_content
    else:
        compact["def"] = {"content": tuple_content, "fmt": tuple_format}
    
    if pattern.definition.description:
        compact["desc"] = pattern.definition.description
    
    # Components - flatten to essential fields
    compact["comps"] = []
    for comp in pattern.definition.components.component:
        comp_dict = {
            "n": comp.name,
            "t": comp.type,
            "d": comp.description
        }
        if comp.notation:
            comp_dict["nota"] = comp.notation
        compact["comps"].append(comp_dict)
    
    # Type definitions (optional)
    if pattern.type_definitions:
        compact["types"] = []
        for td in pattern.type_definitions.type_def:
            type_dict = {"n": td.name}
            
            # Handle format
            if td.definition.format == "latex":
                type_dict["def"] = td.definition.content
            else:
                type_dict["def"] = {"content": td.definition.content, "fmt": td.definition.format}
            
            if td.description:
                type_dict["d"] = td.description
            
            compact["types"].append(type_dict)
    
    # Properties
    compact["props"] = []
    for prop in pattern.properties.property:
        prop_dict = {
            "id": prop.id,
            "n": prop.name,
        }
        
        # Formal spec
        if prop.formal_spec.format == "latex":
            prop_dict["spec"] = prop.formal_spec.content
        else:
            prop_dict["spec"] = {"content": prop.formal_spec.content, "fmt": prop.formal_spec.format}
        
        if prop.description:
            prop_dict["d"] = prop.description
        
        # Invariants
        if prop.invariants:
            inv_list = []
            for inv in prop.invariants.invariant:
                if inv.format == "latex":
                    inv_list.append(inv.content)
                else:
                    inv_list.append({"content": inv.content, "fmt": inv.format})
            prop_dict["inv"] = inv_list
        
        compact["props"].append(prop_dict)
    
    # Operations
    compact["ops"] = []
    for op in pattern.operations.operation:
        op_dict = {
            "n": op.name,
            "sig": op.signature,
        }
        
        # Formal definition
        if op.formal_definition.format == "latex":
            op_dict["def"] = op.formal_definition.content
        else:
            op_dict["def"] = {"content": op.formal_definition.content, "fmt": op.formal_definition.format}
        
        # Preconditions
        if op.preconditions:
            pre_list = []
            for cond in op.preconditions.condition:
                if cond.format == "latex":
                    pre_list.append(cond.content)
                else:
                    pre_list.append({"content": cond.content, "fmt": cond.format})
            op_dict["pre"] = pre_list
        
        # Postconditions
        if op.postconditions:
            post_list = []
            for cond in op.postconditions.condition:
                if cond.format == "latex":
                    post_list.append(cond.content)
                else:
                    post_list.append({"content": cond.content, "fmt": cond.format})
            op_dict["post"] = post_list
        
        # Effects
        if op.effects:
            op_dict["fx"] = op.effects.effect
        
        compact["ops"].append(op_dict)
    
    # Dependencies (optional)
    if pattern.dependencies:
        deps = {}
        if pattern.dependencies.requires:
            deps["req"] = pattern.dependencies.requires.pattern_ref
        if pattern.dependencies.uses:
            deps["use"] = pattern.dependencies.uses.pattern_ref
        if pattern.dependencies.specializes:
            deps["spec"] = pattern.dependencies.specializes.pattern_ref
        if pattern.dependencies.specialized_by:
            deps["by"] = pattern.dependencies.specialized_by.pattern_ref
        
        if deps:
            compact["deps"] = deps
    
    # Manifestations (optional)
    if pattern.manifestations:
        compact["manif"] = []
        for manif in pattern.manifestations.manifestation:
            manif_dict = {"n": manif.name}
            if manif.description:
                manif_dict["d"] = manif.description
            compact["manif"].append(manif_dict)
    
    return compact


def compact_to_pattern(compact: Dict[str, Any]) -> Pattern:
    """
    Reconstruct a full Pattern from compact format.
    
    This function performs the inverse transformation, expanding abbreviated
    keys and restoring the full nested structure required by the Pattern model.
    
    Args:
        compact: Compact dictionary representation
        
    Returns:
        Full Pattern object
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    from universal_corpus.models import (
        Metadata, Domains, Definition, MathExpression, Component, Components,
        TypeDef, TypeDefinitions, Property, Properties, Invariants,
        Operation, Operations, Conditions, Effects, Dependencies, PatternRefs,
        Manifestation, Manifestations
    )
    
    # Helper to expand math expression
    def expand_math_expr(value: Any, default_format: str = "latex") -> MathExpression:
        if isinstance(value, str):
            return MathExpression(content=value, format=default_format)
        else:
            return MathExpression(content=value["content"], format=value.get("fmt", default_format))
    
    # Metadata
    metadata_dict = {
        "name": compact["name"],
        "category": compact["cat"],
        "status": compact["status"],
    }
    
    if "cx" in compact:
        metadata_dict["complexity"] = compact["cx"]
    
    if "domains" in compact:
        metadata_dict["domains"] = Domains(domain=compact["domains"])
    
    if "updated" in compact:
        metadata_dict["last_updated"] = compact["updated"]
    
    metadata = Metadata(**metadata_dict)
    
    # Definition
    tuple_notation = expand_math_expr(compact["def"])
    
    components = []
    for comp_data in compact["comps"]:
        comp_dict = {
            "name": comp_data["n"],
            "type": comp_data["t"],
            "description": comp_data["d"]
        }
        if "nota" in comp_data:
            comp_dict["notation"] = comp_data["nota"]
        components.append(Component(**comp_dict))
    
    definition_dict = {
        "tuple_notation": tuple_notation,
        "components": Components(component=components)
    }
    
    if "desc" in compact:
        definition_dict["description"] = compact["desc"]
    
    definition = Definition(**definition_dict)
    
    # Type definitions (optional)
    type_definitions = None
    if "types" in compact:
        type_defs = []
        for td_data in compact["types"]:
            td_dict = {
                "name": td_data["n"],
                "definition": expand_math_expr(td_data["def"])
            }
            if "d" in td_data:
                td_dict["description"] = td_data["d"]
            type_defs.append(TypeDef(**td_dict))
        type_definitions = TypeDefinitions(type_def=type_defs)
    
    # Properties
    properties_list = []
    for prop_data in compact["props"]:
        prop_dict = {
            "id": prop_data["id"],
            "name": prop_data["n"],
            "formal_spec": expand_math_expr(prop_data["spec"])
        }
        
        if "d" in prop_data:
            prop_dict["description"] = prop_data["d"]
        
        if "inv" in prop_data:
            invariant_list = [expand_math_expr(inv) for inv in prop_data["inv"]]
            prop_dict["invariants"] = Invariants(invariant=invariant_list)
        
        properties_list.append(Property(**prop_dict))
    
    properties = Properties(property=properties_list)
    
    # Operations
    operations_list = []
    for op_data in compact["ops"]:
        op_dict = {
            "name": op_data["n"],
            "signature": op_data["sig"],
            "formal_definition": expand_math_expr(op_data["def"])
        }
        
        if "pre" in op_data:
            precond_list = [expand_math_expr(cond) for cond in op_data["pre"]]
            op_dict["preconditions"] = Conditions(condition=precond_list)
        
        if "post" in op_data:
            postcond_list = [expand_math_expr(cond) for cond in op_data["post"]]
            op_dict["postconditions"] = Conditions(condition=postcond_list)
        
        if "fx" in op_data:
            op_dict["effects"] = Effects(effect=op_data["fx"])
        
        operations_list.append(Operation(**op_dict))
    
    operations = Operations(operation=operations_list)
    
    # Dependencies (optional)
    dependencies = None
    if "deps" in compact:
        deps_dict = {}
        if "req" in compact["deps"]:
            deps_dict["requires"] = PatternRefs(pattern_ref=compact["deps"]["req"])
        if "use" in compact["deps"]:
            deps_dict["uses"] = PatternRefs(pattern_ref=compact["deps"]["use"])
        if "spec" in compact["deps"]:
            deps_dict["specializes"] = PatternRefs(pattern_ref=compact["deps"]["spec"])
        if "by" in compact["deps"]:
            deps_dict["specialized_by"] = PatternRefs(pattern_ref=compact["deps"]["by"])
        
        if deps_dict:
            dependencies = Dependencies(**deps_dict)
    
    # Manifestations (optional)
    manifestations = None
    if "manif" in compact:
        manif_list = []
        for manif_data in compact["manif"]:
            manif_dict = {"name": manif_data["n"]}
            if "d" in manif_data:
                manif_dict["description"] = manif_data["d"]
            manif_list.append(Manifestation(**manif_dict))
        manifestations = Manifestations(manifestation=manif_list)
    
    # Construct full pattern
    pattern_dict = {
        "id": compact["id"],
        "version": compact["v"],
        "metadata": metadata,
        "definition": definition,
        "properties": properties,
        "operations": operations
    }
    
    if type_definitions:
        pattern_dict["type_definitions"] = type_definitions
    if dependencies:
        pattern_dict["dependencies"] = dependencies
    if manifestations:
        pattern_dict["manifestations"] = manifestations
    
    return Pattern(**pattern_dict)


def export_compact_jsonl(patterns: List[Pattern]) -> str:
    """
    Export patterns to compact JSONL format.
    
    Args:
        patterns: List of Pattern objects
        
    Returns:
        JSONL string with one compact pattern per line
    """
    lines = []
    for pattern in patterns:
        compact = pattern_to_compact(pattern)
        lines.append(json.dumps(compact, ensure_ascii=False))
    return '\n'.join(lines)


def import_compact_jsonl(jsonl_content: str) -> List[Pattern]:
    """
    Import patterns from compact JSONL format.
    
    Args:
        jsonl_content: JSONL string with compact patterns
        
    Returns:
        List of full Pattern objects
        
    Raises:
        ValueError: If parsing or validation fails
    """
    patterns = []
    for line_num, line in enumerate(jsonl_content.strip().split('\n'), start=1):
        if not line.strip():
            continue
        
        try:
            compact = json.loads(line)
            pattern = compact_to_pattern(compact)
            patterns.append(pattern)
        except Exception as e:
            raise ValueError(f"Error parsing line {line_num}: {str(e)}") from e
    
    return patterns


def calculate_compression_ratio(full_jsonl: str, compact_jsonl: str) -> Dict[str, Any]:
    """
    Calculate compression statistics between full and compact formats.
    
    Args:
        full_jsonl: Full JSONL content
        compact_jsonl: Compact JSONL content
        
    Returns:
        Dictionary with compression statistics
    """
    full_size = len(full_jsonl)
    compact_size = len(compact_jsonl)
    
    # Rough token estimation (1 token ≈ 4 characters for English text)
    full_tokens = full_size // 4
    compact_tokens = compact_size // 4
    
    reduction = full_size - compact_size
    reduction_pct = (reduction / full_size) * 100 if full_size > 0 else 0
    
    return {
        "full_size_bytes": full_size,
        "compact_size_bytes": compact_size,
        "reduction_bytes": reduction,
        "reduction_percentage": round(reduction_pct, 2),
        "full_tokens_estimate": full_tokens,
        "compact_tokens_estimate": compact_tokens,
        "token_savings": full_tokens - compact_tokens,
        "compression_ratio": round(full_size / compact_size, 2) if compact_size > 0 else 0
    }


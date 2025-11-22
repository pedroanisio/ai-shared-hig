#!/usr/bin/env python3
"""
Database initialization script for Universal Corpus Pattern API.

This script initializes or resets the database and optionally loads sample data.
"""

import sys
from database import init_db, drop_db, SessionLocal, PatternRepository
from models import (
    Pattern, Metadata, Definition, MathExpression, Components, Component,
    Properties, Property, Operations, Operation, Manifestations, Manifestation
)


def create_sample_pattern() -> Pattern:
    """Create a sample pattern for testing/demonstration."""
    return Pattern(
        id="C1",
        version="1.1",
        metadata=Metadata(
            name="Graph Structure",
            category="concept",
            status="stable",
            complexity="medium"
        ),
        definition=Definition(
            tuple_notation=MathExpression(
                content="$G = (N, E, \\lambda_n, \\lambda_e)$",
                format="latex"
            ),
            components=Components(
                component=[
                    Component(
                        name="N",
                        type="Set",
                        notation="N",
                        description="Set of nodes"
                    ),
                    Component(
                        name="E",
                        type="Set",
                        notation="E",
                        description="Set of edges"
                    ),
                    Component(
                        name="\\lambda_n",
                        type="N → Label_n",
                        notation="\\lambda_n",
                        description="**node labeling function**"
                    ),
                    Component(
                        name="\\lambda_e",
                        type="E → Label_e",
                        notation="\\lambda_e",
                        description="**edge labeling function**"
                    )
                ]
            )
        ),
        properties=Properties(
            property=[
                Property(
                    id="P.C1.1",
                    name="Connectivity",
                    formal_spec=MathExpression(
                        content="connected(G) ⇔ ∀n₁, n₂ ∈ N: ∃ path from n₁ to n₂",
                        format="latex"
                    )
                ),
                Property(
                    id="P.C1.2",
                    name="Cycle Detection",
                    formal_spec=MathExpression(
                        content="acyclic(G) ⇔ ¬∃ path: n → ... → n",
                        format="latex"
                    )
                )
            ]
        ),
        operations=Operations(
            operation=[
                Operation(
                    name="Traverse",
                    signature="traverse(n: N, depth: ℕ) → Set⟨N⟩",
                    formal_definition=MathExpression(
                        content="traverse(n: N, depth: ℕ) = {n' ∈ N : distance(n, n') ≤ depth}",
                        format="latex"
                    )
                ),
                Operation(
                    name="Neighbors",
                    signature="neighbors(n: N) → Set⟨N⟩",
                    formal_definition=MathExpression(
                        content="neighbors(n: N) = {n' ∈ N : (n, n') ∈ E ∨ (n', n) ∈ E}",
                        format="latex"
                    )
                ),
                Operation(
                    name="Path",
                    signature="path(n₁: N, n₂: N) → Sequence⟨N⟩ | null",
                    formal_definition=MathExpression(
                        content="path(n₁: N, n₂: N) = shortest path from n₁ to n₂, or null if none exists",
                        format="latex"
                    )
                )
            ]
        ),
        manifestations=Manifestations(
            manifestation=[
                Manifestation(name="Knowledge graphs"),
                Manifestation(name="File trees"),
                Manifestation(name="Feature history", description="CAD"),
                Manifestation(name="Axiom dependencies", description="proof assistants"),
                Manifestation(name="Part hierarchies", description="engineering"),
                Manifestation(name="Social networks"),
                Manifestation(name="Dependency graphs")
            ]
        )
    )


def main():
    """Main initialization function."""
    print("Universal Corpus Pattern Database Initialization")
    print("=" * 50)
    
    # Check for reset flag
    reset = "--reset" in sys.argv or "-r" in sys.argv
    load_sample = "--sample" in sys.argv or "-s" in sys.argv
    
    if reset:
        print("\n⚠️  Resetting database (all data will be lost)...")
        response = input("Are you sure? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return
        drop_db()
        print("✓ Database reset complete")
    
    # Initialize database
    print("\n📦 Initializing database...")
    init_db()
    print("✓ Database initialized")
    
    # Load sample data if requested
    if load_sample:
        print("\n📝 Loading sample pattern...")
        db = SessionLocal()
        try:
            repo = PatternRepository(db)
            sample_pattern = create_sample_pattern()
            repo.create(sample_pattern)
            print(f"✓ Sample pattern '{sample_pattern.id}' loaded")
        except Exception as e:
            print(f"✗ Error loading sample pattern: {e}")
        finally:
            db.close()
    
    print("\n✅ Initialization complete!")
    print("\nNext steps:")
    print("  1. Start the API: python api.py")
    print("  2. View docs: http://localhost:8000/docs")
    print("  3. Run tests: pytest test_api.py -v")


if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python init_db.py [OPTIONS]")
        print("\nOptions:")
        print("  --reset, -r   Reset database (WARNING: deletes all data)")
        print("  --sample, -s  Load sample pattern")
        print("  --help, -h    Show this help message")
        print("\nExamples:")
        print("  python init_db.py              # Initialize empty database")
        print("  python init_db.py --sample     # Initialize with sample data")
        print("  python init_db.py --reset      # Reset and reinitialize")
        print("  python init_db.py -r -s        # Reset and load sample")
    else:
        main()


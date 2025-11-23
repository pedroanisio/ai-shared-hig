"""
Database layer for Universal Corpus Pattern API using SQLAlchemy.

This module provides:
- SQLAlchemy models for persistent storage
- Database session management
- CRUD operations with proper transaction handling
"""

from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional, List
import json

from universal_corpus.models import Pattern


# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./patterns.db"

# Create engine with connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    pool_pre_ping=True,  # Enable connection health checks
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class PatternDB(Base):
    """
    SQLAlchemy model for storing patterns.
    
    Stores the complete pattern as JSON to preserve all nested structures
    while maintaining queryable top-level fields for efficient filtering.
    """
    __tablename__ = "patterns"
    
    # Primary key and identifiers
    id = Column(String(50), primary_key=True, index=True)
    version = Column(String(20), nullable=False)
    
    # Metadata fields for efficient querying
    name = Column(String(200), nullable=False, index=True)
    category = Column(String(20), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)
    complexity = Column(String(20), nullable=True)
    
    # Complete pattern data as JSON
    data = Column(Text, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_pattern(self) -> Pattern:
        """Convert database model to Pydantic Pattern model."""
        pattern_dict = json.loads(self.data)
        return Pattern(**pattern_dict)
    
    @classmethod
    def from_pattern(cls, pattern: Pattern) -> "PatternDB":
        """Create database model from Pydantic Pattern model."""
        return cls(
            id=pattern.id,
            version=pattern.version,
            name=pattern.metadata.name,
            category=pattern.metadata.category,
            status=pattern.metadata.status,
            complexity=pattern.metadata.complexity,
            data=pattern.model_dump_json()
        )


def get_db() -> Session:
    """
    Dependency function to get database session.
    
    Yields a database session and ensures it's closed after use.
    This follows the dependency injection pattern for FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    This should be called once at application startup.
    """
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    Drop all database tables.
    
    WARNING: This will delete all data. Use only for testing or reset scenarios.
    """
    Base.metadata.drop_all(bind=engine)


# CRUD Operations
class PatternRepository:
    """
    Repository pattern for Pattern CRUD operations.
    
    Encapsulates all database operations to maintain clean separation
    between business logic and data access.
    """
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db
    
    def create(self, pattern: Pattern) -> Pattern:
        """
        Create a new pattern in the database.
        
        Args:
            pattern: Pattern to create
            
        Returns:
            The created pattern
            
        Raises:
            ValueError: If pattern with same ID already exists
        """
        existing = self.db.query(PatternDB).filter(PatternDB.id == pattern.id).first()
        if existing:
            raise ValueError(f"Pattern with ID '{pattern.id}' already exists")
        
        db_pattern = PatternDB.from_pattern(pattern)
        self.db.add(db_pattern)
        self.db.commit()
        self.db.refresh(db_pattern)
        return db_pattern.to_pattern()
    
    def get_by_id(self, pattern_id: str) -> Optional[Pattern]:
        """
        Retrieve a pattern by ID.
        
        Args:
            pattern_id: Pattern identifier
            
        Returns:
            Pattern if found, None otherwise
        """
        db_pattern = self.db.query(PatternDB).filter(PatternDB.id == pattern_id).first()
        return db_pattern.to_pattern() if db_pattern else None
    
    def list(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Pattern]:
        """
        List patterns with optional filtering and pagination.
        
        Args:
            category: Filter by category
            status: Filter by status
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of patterns matching filters
        """
        query = self.db.query(PatternDB)
        
        if category:
            query = query.filter(PatternDB.category == category)
        if status:
            query = query.filter(PatternDB.status == status)
        
        db_patterns = query.offset(offset).limit(limit).all()
        return [p.to_pattern() for p in db_patterns]
    
    def update(self, pattern_id: str, pattern: Pattern) -> Optional[Pattern]:
        """
        Update an existing pattern.
        
        Args:
            pattern_id: ID of pattern to update
            pattern: New pattern data
            
        Returns:
            Updated pattern if found, None otherwise
            
        Raises:
            ValueError: If pattern ID mismatch
        """
        if pattern.id != pattern_id:
            raise ValueError(f"Pattern ID mismatch: '{pattern_id}' != '{pattern.id}'")
        
        db_pattern = self.db.query(PatternDB).filter(PatternDB.id == pattern_id).first()
        if not db_pattern:
            return None
        
        # Update fields
        db_pattern.version = pattern.version
        db_pattern.name = pattern.metadata.name
        db_pattern.category = pattern.metadata.category
        db_pattern.status = pattern.metadata.status
        db_pattern.complexity = pattern.metadata.complexity
        db_pattern.data = pattern.model_dump_json()
        db_pattern.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_pattern)
        return db_pattern.to_pattern()
    
    def partial_update(self, pattern_id: str, update_data: dict) -> Optional[Pattern]:
        """
        Partially update an existing pattern.
        
        Only updates fields that are provided in update_data. Uses deep merge
        to update nested structures without losing existing data.
        
        Args:
            pattern_id: ID of pattern to update
            update_data: Dictionary containing fields to update (can be partial)
            
        Returns:
            Updated pattern if found, None otherwise
        """
        db_pattern = self.db.query(PatternDB).filter(PatternDB.id == pattern_id).first()
        if not db_pattern:
            return None
        
        # Load current pattern data
        current_data = json.loads(db_pattern.data)
        
        # Deep merge update_data into current_data
        merged_data = self._deep_merge(current_data, update_data)
        
        # Validate the merged data by creating a Pattern instance
        try:
            updated_pattern = Pattern(**merged_data)
        except Exception as e:
            raise ValueError(f"Invalid partial update data: {e}")
        
        # Update database fields
        db_pattern.version = updated_pattern.version
        db_pattern.name = updated_pattern.metadata.name
        db_pattern.category = updated_pattern.metadata.category
        db_pattern.status = updated_pattern.metadata.status
        db_pattern.complexity = updated_pattern.metadata.complexity
        db_pattern.data = updated_pattern.model_dump_json()
        db_pattern.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_pattern)
        return db_pattern.to_pattern()
    
    def _deep_merge(self, base: dict, update: dict) -> dict:
        """
        Recursively merge update dict into base dict with intelligent array handling.
        
        Arrays are merged intelligently based on identifying keys:
        - operations.operation: merged by "name"
        - properties.property: merged by "id"
        - components.component: merged by "name"
        - type_definitions.type_def: merged by "name"
        - manifestations.manifestation: merged by "name"
        - Other arrays: replaced entirely
        
        REPLACE MODE: If update dict contains {"__replace__": true}, the value
        completely replaces the base (no merging).
        
        Args:
            base: Base dictionary
            update: Updates to apply
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in update.items():
            # Skip the replace marker itself
            if key == "__replace__":
                continue
                
            # Check if this update has explicit replace mode
            if isinstance(value, dict) and value.get("__replace__") is True:
                # Remove the marker and use the rest as replacement
                clean_value = {k: v for k, v in value.items() if k != "__replace__"}
                result[key] = clean_value
            elif key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dicts
                result[key] = self._deep_merge(result[key], value)
            elif key in result and isinstance(result[key], list) and isinstance(value, list):
                # Intelligent array merging based on context
                result[key] = self._merge_arrays(key, result[key], value)
            else:
                # Overwrite with new value
                result[key] = value
        
        return result
    
    def _merge_arrays(self, key: str, base_array: list, update_array: list) -> list:
        """
        Merge arrays intelligently based on identifying keys.
        
        REPLACE MODE: If none of the update items match existing items (by merge key),
        the entire array is replaced. This allows for complete array replacement.
        
        MERGE MODE: If any update items match existing items, those items are merged
        and unmatched base items are preserved.
        
        Args:
            key: The field name (to determine merge strategy)
            base_array: Existing array
            update_array: Array with updates
            
        Returns:
            Merged or replaced array
        """
        # Define merge strategies for different array types
        merge_strategies = {
            'operation': 'name',      # operations.operation merged by name
            'property': 'id',         # properties.property merged by id
            'component': 'name',      # components.component merged by name
            'type-def': 'name',       # type-definitions.type-def merged by name
            'type_def': 'name',       # type_definitions.type_def merged by name (both formats)
            'manifestation': 'name',  # manifestations.manifestation merged by name
            'invariant': None,        # invariants - replace entire array
            'condition': None,        # conditions - replace entire array
            'effect': None,           # effects - replace entire array
            'domain': None,           # domains - replace entire array
            'pattern-ref': None,      # pattern refs - replace entire array
            'pattern_ref': None,      # pattern refs - replace entire array
        }
        
        merge_key = merge_strategies.get(key)
        
        if merge_key is None:
            # No intelligent merge - replace entire array
            return update_array
        
        # Build lookup dictionary from base array
        base_dict = {}
        non_mergeable_base_items = []
        
        for item in base_array:
            if isinstance(item, dict) and merge_key in item:
                identifier = item[merge_key]
                base_dict[identifier] = item
            else:
                # Item doesn't have the merge key
                non_mergeable_base_items.append(item)
        
        # Check if ANY update items match existing items
        update_identifiers = set()
        for item in update_array:
            if isinstance(item, dict) and merge_key in item:
                update_identifiers.add(item[merge_key])
        
        has_overlap = bool(update_identifiers & set(base_dict.keys()))
        
        # REPLACE MODE: No overlapping keys means complete replacement
        if not has_overlap and base_dict:
            return update_array
        
        # MERGE MODE: Has overlaps, merge intelligently
        result = []
        updated_keys = set()
        
        for item in update_array:
            if isinstance(item, dict) and merge_key in item:
                identifier = item[merge_key]
                updated_keys.add(identifier)
                
                if identifier in base_dict:
                    # Merge with existing item
                    merged_item = self._deep_merge(base_dict[identifier], item)
                    result.append(merged_item)
                else:
                    # New item - add it
                    result.append(item)
            else:
                # Item doesn't have merge key, just add it
                result.append(item)
        
        # Add base items that weren't updated (only in merge mode)
        for identifier, item in base_dict.items():
            if identifier not in updated_keys:
                result.append(item)
        
        # Add back non-mergeable items from base
        result.extend(non_mergeable_base_items)
        
        return result
    
    def delete(self, pattern_id: str) -> bool:
        """
        Delete a pattern by ID.
        
        Args:
            pattern_id: Pattern identifier
            
        Returns:
            True if deleted, False if not found
        """
        db_pattern = self.db.query(PatternDB).filter(PatternDB.id == pattern_id).first()
        if not db_pattern:
            return False
        
        self.db.delete(db_pattern)
        self.db.commit()
        return True
    
    def count(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> int:
        """
        Count patterns with optional filtering.
        
        Args:
            category: Filter by category
            status: Filter by status
            
        Returns:
            Number of patterns matching filters
        """
        query = self.db.query(PatternDB)
        
        if category:
            query = query.filter(PatternDB.category == category)
        if status:
            query = query.filter(PatternDB.status == status)
        
        return query.count()
    
    def get_statistics(self) -> dict:
        """
        Get statistics about the pattern collection.
        
        Returns:
            Dictionary with counts by category, status, and complexity
        """
        total = self.db.query(PatternDB).count()
        
        # Count by category
        by_category = {}
        for category in ["concept", "pattern", "flow"]:
            count = self.db.query(PatternDB).filter(PatternDB.category == category).count()
            if count > 0:
                by_category[category] = count
        
        # Count by status
        by_status = {}
        for status in ["draft", "stable", "deprecated"]:
            count = self.db.query(PatternDB).filter(PatternDB.status == status).count()
            if count > 0:
                by_status[status] = count
        
        # Count by complexity
        by_complexity = {}
        for complexity in ["low", "medium", "high"]:
            count = self.db.query(PatternDB).filter(PatternDB.complexity == complexity).count()
            if count > 0:
                by_complexity[complexity] = count
        
        return {
            "total_patterns": total,
            "by_category": by_category,
            "by_status": by_status,
            "by_complexity": by_complexity
        }


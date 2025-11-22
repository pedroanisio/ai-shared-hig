"""
Comprehensive tests for the Universal Corpus Pattern API.

Following TDD principles, these tests validate:
1. Model validation (Pydantic models match XSD constraints)
2. API endpoints (CRUD operations)
3. XML conversion
4. Edge cases and error handling
"""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
import xml.etree.ElementTree as ET
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api import app
from models import (
    Pattern, Metadata, Definition, MathExpression, Components, Component,
    Properties, Property, Operations, Operation, Manifestations, Manifestation,
    Dependencies, PatternRefs, TypeDefinitions, TypeDef
)
from database import Base, get_db


# Create test database engine
TEST_DATABASE_URL = "sqlite:///./test_patterns.db"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override database dependency for testing."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create fresh database for each test."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def valid_pattern_data():
    """Valid pattern data for testing."""
    return {
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
                        "name": "N",
                        "type": "Set",
                        "notation": "N",
                        "description": "Set of nodes"
                    },
                    {
                        "name": "E",
                        "type": "Set",
                        "description": "Set of edges"
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
                        "content": "traverse(n: N, depth: ℕ) = {n' ∈ N : distance(n, n') ≤ depth}",
                        "format": "latex"
                    }
                }
            ]
        }
    }


@pytest.fixture
def valid_pattern(valid_pattern_data):
    """Create a valid Pattern instance."""
    return Pattern(**valid_pattern_data)


# ==================== Model Validation Tests ====================

class TestPatternIdValidation:
    """Test Pattern ID validation matching XSD pattern [CPF][0-9]+(.[0-9]+)?"""
    
    def test_valid_concept_id(self, valid_pattern_data):
        """Test valid concept ID (C followed by numbers)."""
        valid_pattern_data["id"] = "C123"
        pattern = Pattern(**valid_pattern_data)
        assert pattern.id == "C123"
    
    def test_valid_pattern_id(self, valid_pattern_data):
        """Test valid pattern ID (P followed by numbers)."""
        valid_pattern_data["id"] = "P42"
        pattern = Pattern(**valid_pattern_data)
        assert pattern.id == "P42"
    
    def test_valid_flow_id(self, valid_pattern_data):
        """Test valid flow ID (F followed by numbers)."""
        valid_pattern_data["id"] = "F7"
        pattern = Pattern(**valid_pattern_data)
        assert pattern.id == "F7"
    
    def test_valid_id_with_decimal(self, valid_pattern_data):
        """Test valid ID with decimal notation."""
        valid_pattern_data["id"] = "C1.5"
        pattern = Pattern(**valid_pattern_data)
        assert pattern.id == "C1.5"
    
    def test_invalid_id_wrong_prefix(self, valid_pattern_data):
        """Test that invalid prefix raises ValidationError."""
        valid_pattern_data["id"] = "X123"
        with pytest.raises(ValidationError) as exc_info:
            Pattern(**valid_pattern_data)
        assert "Pattern ID must match pattern" in str(exc_info.value)
    
    def test_invalid_id_no_number(self, valid_pattern_data):
        """Test that ID without number raises ValidationError."""
        valid_pattern_data["id"] = "C"
        with pytest.raises(ValidationError) as exc_info:
            Pattern(**valid_pattern_data)
        assert "Pattern ID must match pattern" in str(exc_info.value)
    
    def test_invalid_id_letters_after_number(self, valid_pattern_data):
        """Test that ID with letters after number raises ValidationError."""
        valid_pattern_data["id"] = "C1ABC"
        with pytest.raises(ValidationError) as exc_info:
            Pattern(**valid_pattern_data)
        assert "Pattern ID must match pattern" in str(exc_info.value)


class TestCategoryValidation:
    """Test category enumeration validation."""
    
    def test_valid_concept_category(self, valid_pattern_data):
        """Test valid 'concept' category."""
        valid_pattern_data["metadata"]["category"] = "concept"
        pattern = Pattern(**valid_pattern_data)
        assert pattern.metadata.category == "concept"
    
    def test_valid_pattern_category(self, valid_pattern_data):
        """Test valid 'pattern' category."""
        valid_pattern_data["metadata"]["category"] = "pattern"
        pattern = Pattern(**valid_pattern_data)
        assert pattern.metadata.category == "pattern"
    
    def test_valid_flow_category(self, valid_pattern_data):
        """Test valid 'flow' category."""
        valid_pattern_data["metadata"]["category"] = "flow"
        pattern = Pattern(**valid_pattern_data)
        assert pattern.metadata.category == "flow"
    
    def test_invalid_category(self, valid_pattern_data):
        """Test that invalid category raises ValidationError."""
        valid_pattern_data["metadata"]["category"] = "invalid"
        with pytest.raises(ValidationError):
            Pattern(**valid_pattern_data)


class TestStatusValidation:
    """Test status enumeration validation."""
    
    @pytest.mark.parametrize("status", ["draft", "stable", "deprecated"])
    def test_valid_statuses(self, valid_pattern_data, status):
        """Test all valid status values."""
        valid_pattern_data["metadata"]["status"] = status
        pattern = Pattern(**valid_pattern_data)
        assert pattern.metadata.status == status
    
    def test_invalid_status(self, valid_pattern_data):
        """Test that invalid status raises ValidationError."""
        valid_pattern_data["metadata"]["status"] = "invalid"
        with pytest.raises(ValidationError):
            Pattern(**valid_pattern_data)


class TestComplexityValidation:
    """Test complexity enumeration validation."""
    
    @pytest.mark.parametrize("complexity", ["low", "medium", "high"])
    def test_valid_complexity(self, valid_pattern_data, complexity):
        """Test all valid complexity values."""
        valid_pattern_data["metadata"]["complexity"] = complexity
        pattern = Pattern(**valid_pattern_data)
        assert pattern.metadata.complexity == complexity
    
    def test_optional_complexity(self, valid_pattern_data):
        """Test that complexity is optional."""
        del valid_pattern_data["metadata"]["complexity"]
        pattern = Pattern(**valid_pattern_data)
        assert pattern.metadata.complexity is None
    
    def test_invalid_complexity(self, valid_pattern_data):
        """Test that invalid complexity raises ValidationError."""
        valid_pattern_data["metadata"]["complexity"] = "extreme"
        with pytest.raises(ValidationError):
            Pattern(**valid_pattern_data)


class TestDateValidation:
    """Test date format validation."""
    
    def test_valid_date_format(self, valid_pattern_data):
        """Test valid ISO date format."""
        valid_pattern_data["metadata"]["last_updated"] = "2025-11-22"
        pattern = Pattern(**valid_pattern_data)
        assert pattern.metadata.last_updated == "2025-11-22"
    
    def test_invalid_date_format(self, valid_pattern_data):
        """Test that invalid date format raises ValidationError."""
        valid_pattern_data["metadata"]["last-updated"] = "22-11-2025"
        with pytest.raises(ValidationError) as exc_info:
            Pattern(**valid_pattern_data)
        assert "ISO date format" in str(exc_info.value)
    
    def test_optional_date(self, valid_pattern_data):
        """Test that date is optional."""
        pattern = Pattern(**valid_pattern_data)
        assert pattern.metadata.last_updated is None


class TestPatternRefsValidation:
    """Test pattern reference ID validation."""
    
    def test_valid_pattern_refs(self, valid_pattern_data):
        """Test valid pattern references."""
        valid_pattern_data["dependencies"] = {
            "requires": {
                "pattern-ref": ["C1", "P2.3", "F15"]
            }
        }
        pattern = Pattern(**valid_pattern_data)
        assert len(pattern.dependencies.requires.pattern_ref) == 3
    
    def test_invalid_pattern_ref(self, valid_pattern_data):
        """Test that invalid pattern reference raises ValidationError."""
        valid_pattern_data["dependencies"] = {
            "requires": {
                "pattern-ref": ["INVALID123"]
            }
        }
        with pytest.raises(ValidationError) as exc_info:
            Pattern(**valid_pattern_data)
        assert "must match pattern" in str(exc_info.value)


class TestRequiredFields:
    """Test that required fields are enforced."""
    
    def test_missing_metadata(self, valid_pattern_data):
        """Test that missing metadata raises ValidationError."""
        del valid_pattern_data["metadata"]
        with pytest.raises(ValidationError):
            Pattern(**valid_pattern_data)
    
    def test_missing_definition(self, valid_pattern_data):
        """Test that missing definition raises ValidationError."""
        del valid_pattern_data["definition"]
        with pytest.raises(ValidationError):
            Pattern(**valid_pattern_data)
    
    def test_missing_properties(self, valid_pattern_data):
        """Test that missing properties raises ValidationError."""
        del valid_pattern_data["properties"]
        with pytest.raises(ValidationError):
            Pattern(**valid_pattern_data)
    
    def test_missing_operations(self, valid_pattern_data):
        """Test that missing operations raises ValidationError."""
        del valid_pattern_data["operations"]
        with pytest.raises(ValidationError):
            Pattern(**valid_pattern_data)
    
    def test_empty_components_list(self, valid_pattern_data):
        """Test that empty components list raises ValidationError."""
        valid_pattern_data["definition"]["components"]["component"] = []
        with pytest.raises(ValidationError):
            Pattern(**valid_pattern_data)
    
    def test_empty_properties_list(self, valid_pattern_data):
        """Test that empty properties list raises ValidationError."""
        valid_pattern_data["properties"]["property"] = []
        with pytest.raises(ValidationError):
            Pattern(**valid_pattern_data)
    
    def test_empty_operations_list(self, valid_pattern_data):
        """Test that empty operations list raises ValidationError."""
        valid_pattern_data["operations"]["operation"] = []
        with pytest.raises(ValidationError):
            Pattern(**valid_pattern_data)


# ==================== API Endpoint Tests ====================

class TestRootEndpoint:
    """Test root and health endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["api"] == "Universal Corpus Pattern API"
        assert "endpoints" in data
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "patterns_count" in data


class TestCreatePattern:
    """Test pattern creation endpoint."""
    
    def test_create_valid_pattern(self, client, valid_pattern_data):
        """Test creating a valid pattern."""
        response = client.post("/patterns", json=valid_pattern_data)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == valid_pattern_data["id"]
        assert data["metadata"]["name"] == valid_pattern_data["metadata"]["name"]
    
    def test_create_duplicate_pattern(self, client, valid_pattern_data):
        """Test that creating duplicate pattern returns 409."""
        client.post("/patterns", json=valid_pattern_data)
        response = client.post("/patterns", json=valid_pattern_data)
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]
    
    def test_create_invalid_pattern(self, client, valid_pattern_data):
        """Test that creating invalid pattern returns 422."""
        valid_pattern_data["id"] = "INVALID"
        response = client.post("/patterns", json=valid_pattern_data)
        assert response.status_code == 422


class TestListPatterns:
    """Test pattern listing endpoint."""
    
    def test_list_empty_patterns(self, client):
        """Test listing patterns when none exist."""
        response = client.get("/patterns")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_patterns(self, client, valid_pattern_data):
        """Test listing patterns."""
        client.post("/patterns", json=valid_pattern_data)
        response = client.get("/patterns")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == valid_pattern_data["id"]
    
    def test_filter_by_category(self, client, valid_pattern_data):
        """Test filtering patterns by category."""
        client.post("/patterns", json=valid_pattern_data)
        
        # Should find the pattern
        response = client.get("/patterns?category=concept")
        assert response.status_code == 200
        assert len(response.json()) == 1
        
        # Should not find the pattern
        response = client.get("/patterns?category=flow")
        assert response.status_code == 200
        assert len(response.json()) == 0
    
    def test_filter_by_status(self, client, valid_pattern_data):
        """Test filtering patterns by status."""
        client.post("/patterns", json=valid_pattern_data)
        
        response = client.get("/patterns?status=stable")
        assert response.status_code == 200
        assert len(response.json()) == 1
        
        response = client.get("/patterns?status=draft")
        assert response.status_code == 200
        assert len(response.json()) == 0
    
    def test_pagination(self, client, valid_pattern_data):
        """Test pagination of pattern list."""
        # Create multiple patterns
        for i in range(5):
            data = valid_pattern_data.copy()
            data["id"] = f"C{i}"
            client.post("/patterns", json=data)
        
        # Test limit
        response = client.get("/patterns?limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2
        
        # Test offset
        response = client.get("/patterns?limit=2&offset=2")
        assert response.status_code == 200
        assert len(response.json()) == 2


class TestGetPattern:
    """Test pattern retrieval endpoint."""
    
    def test_get_existing_pattern(self, client, valid_pattern_data):
        """Test getting an existing pattern."""
        client.post("/patterns", json=valid_pattern_data)
        response = client.get(f"/patterns/{valid_pattern_data['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == valid_pattern_data["id"]
    
    def test_get_nonexistent_pattern(self, client):
        """Test getting a non-existent pattern returns 404."""
        response = client.get("/patterns/NONEXISTENT")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestGetPatternXML:
    """Test XML export endpoint."""
    
    def test_get_pattern_as_xml(self, client, valid_pattern_data):
        """Test getting pattern as XML."""
        client.post("/patterns", json=valid_pattern_data)
        response = client.get(f"/patterns/{valid_pattern_data['id']}/xml")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/xml; charset=utf-8"
        
        # Verify it's valid XML
        root = ET.fromstring(response.content)
        assert root.tag == "pattern"
        assert root.get("id") == valid_pattern_data["id"]
    
    def test_xml_contains_all_elements(self, client, valid_pattern_data):
        """Test that XML export contains all required elements."""
        client.post("/patterns", json=valid_pattern_data)
        response = client.get(f"/patterns/{valid_pattern_data['id']}/xml")
        root = ET.fromstring(response.content)
        
        # Check main sections exist
        assert root.find(".//{http://universal-corpus.org/schema/v1}metadata") is not None
        assert root.find(".//{http://universal-corpus.org/schema/v1}definition") is not None
        assert root.find(".//{http://universal-corpus.org/schema/v1}properties") is not None
        assert root.find(".//{http://universal-corpus.org/schema/v1}operations") is not None


class TestUpdatePattern:
    """Test pattern update endpoint."""
    
    def test_update_existing_pattern(self, client, valid_pattern_data):
        """Test updating an existing pattern."""
        client.post("/patterns", json=valid_pattern_data)
        
        # Update the pattern
        valid_pattern_data["metadata"]["name"] = "Updated Name"
        response = client.put(f"/patterns/{valid_pattern_data['id']}", json=valid_pattern_data)
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["name"] == "Updated Name"
    
    def test_update_nonexistent_pattern(self, client, valid_pattern_data):
        """Test updating non-existent pattern returns 404."""
        response = client.put("/patterns/NONEXISTENT", json=valid_pattern_data)
        assert response.status_code == 404
    
    def test_update_id_mismatch(self, client, valid_pattern_data):
        """Test that ID mismatch returns 400."""
        client.post("/patterns", json=valid_pattern_data)
        valid_pattern_data["id"] = "C999"
        response = client.put("/patterns/C1", json=valid_pattern_data)
        assert response.status_code == 400
        assert "does not match" in response.json()["detail"]


class TestDeletePattern:
    """Test pattern deletion endpoint."""
    
    def test_delete_existing_pattern(self, client, valid_pattern_data):
        """Test deleting an existing pattern."""
        client.post("/patterns", json=valid_pattern_data)
        response = client.delete(f"/patterns/{valid_pattern_data['id']}")
        assert response.status_code == 204
        
        # Verify it's deleted
        response = client.get(f"/patterns/{valid_pattern_data['id']}")
        assert response.status_code == 404
    
    def test_delete_nonexistent_pattern(self, client):
        """Test deleting non-existent pattern returns 404."""
        response = client.delete("/patterns/NONEXISTENT")
        assert response.status_code == 404


class TestDependenciesEndpoint:
    """Test dependencies endpoint."""
    
    def test_get_dependencies_with_deps(self, client, valid_pattern_data):
        """Test getting dependencies for pattern with dependencies."""
        valid_pattern_data["dependencies"] = {
            "requires": {"pattern-ref": ["C2", "C3"]}
        }
        client.post("/patterns", json=valid_pattern_data)
        
        response = client.get(f"/patterns/{valid_pattern_data['id']}/dependencies")
        assert response.status_code == 200
        data = response.json()
        assert "requires" in data
        assert len(data["requires"]["pattern-ref"]) == 2
    
    def test_get_dependencies_without_deps(self, client, valid_pattern_data):
        """Test getting dependencies for pattern without dependencies."""
        client.post("/patterns", json=valid_pattern_data)
        
        response = client.get(f"/patterns/{valid_pattern_data['id']}/dependencies")
        assert response.status_code == 200
        assert response.json() == {}


class TestStatisticsEndpoint:
    """Test statistics endpoint."""
    
    def test_statistics_empty(self, client):
        """Test statistics with no patterns."""
        response = client.get("/statistics")
        assert response.status_code == 200
        data = response.json()
        assert data["total_patterns"] == 0
    
    def test_statistics_with_patterns(self, client, valid_pattern_data):
        """Test statistics with patterns."""
        # Create multiple patterns
        for i in range(3):
            data = valid_pattern_data.copy()
            data["id"] = f"C{i}"
            if i == 0:
                data["metadata"]["category"] = "concept"
            elif i == 1:
                data["metadata"]["category"] = "pattern"
            else:
                data["metadata"]["category"] = "flow"
            client.post("/patterns", json=data)
        
        response = client.get("/statistics")
        assert response.status_code == 200
        data = response.json()
        assert data["total_patterns"] == 3
        assert data["by_category"]["concept"] == 1
        assert data["by_category"]["pattern"] == 1
        assert data["by_category"]["flow"] == 1


# ==================== Integration Tests ====================

class TestCompleteWorkflow:
    """Test complete workflow of creating, retrieving, and managing patterns."""
    
    def test_full_crud_workflow(self, client, valid_pattern_data):
        """Test complete CRUD workflow."""
        # Create
        response = client.post("/patterns", json=valid_pattern_data)
        assert response.status_code == 201
        pattern_id = response.json()["id"]
        
        # Read
        response = client.get(f"/patterns/{pattern_id}")
        assert response.status_code == 200
        assert response.json()["id"] == pattern_id
        
        # Update
        valid_pattern_data["version"] = "1.2"
        response = client.put(f"/patterns/{pattern_id}", json=valid_pattern_data)
        assert response.status_code == 200
        assert response.json()["version"] == "1.2"
        
        # Delete
        response = client.delete(f"/patterns/{pattern_id}")
        assert response.status_code == 204
        
        # Verify deletion
        response = client.get(f"/patterns/{pattern_id}")
        assert response.status_code == 404



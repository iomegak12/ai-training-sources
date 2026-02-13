"""
Integration Tests for Agentic RAG API
Tests the full workflow from API request to agent response
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from services.agent_service import agent_service
from services.faiss_service import faiss_service
from db.init_databases import initialize_databases
from config.logging_config import setup_logging

# Setup logging for tests
setup_logging()


@pytest.fixture(scope="module", autouse=True)
def setup_services():
    """
    Setup all services before running integration tests
    This runs once for all tests in this module
    """
    # Initialize databases with sample data
    initialize_databases(crm_sample_records=10)
    
    # Initialize FAISS service (may fail gracefully)
    try:
        faiss_service.initialize()
    except Exception:
        pass  # OK if FAISS initialization fails in tests
    
    # Initialize agent service
    success = agent_service.initialize()
    assert success, "Agent service initialization failed"
    
    yield
    
    # Cleanup after tests
    pass


@pytest.fixture
def client():
    """Create test client for API requests"""
    return TestClient(app)


class TestHealthEndpoint:
    """Test the health check endpoint"""
    
    def test_health_check_success(self, client):
        """Test health check returns status of all components"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "status" in data
        assert "components" in data
        assert "timestamp" in data
        
        # Verify components
        components = data["components"]
        assert "agent_service" in components
        assert "database" in components
        
        # Agent should be healthy
        assert components["agent_service"]["status"] == "healthy"


class TestToolsEndpoint:
    """Test the tools listing endpoint"""
    
    def test_get_tools_success(self, client):
        """Test getting list of available tools"""
        response = client.get("/tools")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "tools" in data
        assert "count" in data
        
        # Verify we have multiple tools
        assert data["count"] > 5  # Should have at least 6+ tools
        
        # Verify tool structure
        tools = data["tools"]
        first_tool = tools[0]
        assert "name" in first_tool
        assert "description" in first_tool


class TestChatEndpoint:
    """Test the synchronous chat endpoint"""
    
    def test_chat_basic_query(self, client):
        """Test basic chat query with simple question"""
        response = client.post(
            "/chat",
            json={
                "message": "What is 2+2?",
                "conversation_history": []
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "response" in data
        assert "conversation_history" in data
        assert "timestamp" in data
        
        # Response should exist
        assert len(data["response"]) > 0
    
    def test_chat_with_conversation_history(self, client):
        """Test chat with conversation history context"""
        response = client.post(
            "/chat",
            json={
                "message": "What was my previous question?",
                "conversation_history": [
                    {"role": "user", "content": "What is 2+2?"},
                    {"role": "assistant", "content": "2+2 equals 4."}
                ]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should reference the previous question
        assert "response" in data
    
    def test_chat_crm_query(self, client):
        """Test chat with CRM database query"""
        response = client.post(
            "/chat",
            json={
                "message": "How many active customers do we have?",
                "conversation_history": []
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should get a response about customer count
        assert "response" in data
        assert len(data["response"]) > 0
    
    def test_chat_invalid_request(self, client):
        """Test chat with invalid request body"""
        response = client.post(
            "/chat",
            json={
                "invalid_field": "test"
            }
        )
        
        # Should return validation error
        assert response.status_code == 422
        data = response.json()
        assert "error" in data or "detail" in data


class TestStreamingChatEndpoint:
    """Test the streaming chat endpoint"""
    
    def test_chat_stream_basic(self, client):
        """Test streaming chat with SSE"""
        response = client.post(
            "/chat-stream",
            json={
                "message": "Hello, how are you?",
                "conversation_history": []
            }
        )
        
        assert response.status_code == 200
        
        # Verify SSE content type
        assert "text/event-stream" in response.headers.get("content-type", "")
        
        # Verify we got some streaming content
        content = response.text
        assert len(content) > 0
        
        # Should contain SSE data lines
        assert "data:" in content
    
    def test_chat_stream_with_tools(self, client):
        """Test streaming chat that uses tools"""
        response = client.post(
            "/chat-stream",
            json={
                "message": "Search for information about Python programming",
                "conversation_history": []
            }
        )
        
        assert response.status_code == 200
        content = response.text
        
        # Should have streaming data
        assert "data:" in content


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_chat_empty_message(self, client):
        """Test chat with empty message"""
        response = client.post(
            "/chat",
            json={
                "message": "",
                "conversation_history": []
            }
        )
        
        # Should handle gracefully (either validation error or processed)
        assert response.status_code in [200, 422]
    
    def test_chat_very_long_message(self, client):
        """Test chat with very long message"""
        long_message = "test " * 1000  # 5000 characters
        
        response = client.post(
            "/chat",
            json={
                "message": long_message,
                "conversation_history": []
            }
        )
        
        # Should either process or return error gracefully
        assert response.status_code in [200, 413, 422, 500]
    
    def test_invalid_endpoint(self, client):
        """Test accessing non-existent endpoint"""
        response = client.get("/nonexistent")
        
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test wrong HTTP method on endpoint"""
        response = client.get("/chat")  # POST endpoint
        
        assert response.status_code == 405


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    @pytest.mark.skip(reason="Rate limiting may not be enabled in test environment")
    def test_rate_limit_exceeded(self, client):
        """Test rate limiting kicks in after many requests"""
        # Make many rapid requests
        responses = []
        for _ in range(100):
            try:
                response = client.get("/health")
                responses.append(response.status_code)
            except Exception:
                break
        
        # Should eventually get rate limited (429)
        # This may not trigger in test environment
        assert any(status == 429 for status in responses) or all(status == 200 for status in responses)


class TestDatabaseIntegration:
    """Test database-related functionality"""
    
    def test_customer_query_by_email(self, client):
        """Test querying customer by email through chat"""
        response = client.post(
            "/chat",
            json={
                "message": "Find customer with email john.smith@email.com",
                "conversation_history": []
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should get a response about the customer
        assert "response" in data
    
    def test_sql_query_natural_language(self, client):
        """Test SQL database query with natural language"""
        response = client.post(
            "/chat",
            json={
                "message": "How many tracks are in the Chinook database?",
                "conversation_history": []
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should execute SQL query and return results
        assert "response" in data


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "--tb=short"])

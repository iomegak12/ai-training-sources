"""
API Endpoint Tests with Mocking
Tests each API endpoint with mocked services
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from fastapi import status
from main import app
from api.models import ChatRequest, ChatResponse
from langchain_core.messages import HumanMessage, AIMessage


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_agent_service():
    """Mock agent service for testing"""
    with patch('api.routes.AgentServiceDep') as mock:
        service = Mock()
        service.invoke.return_value = [
            HumanMessage(content="Test question"),
            AIMessage(content="Test answer")
        ]
        service.stream = AsyncMock(return_value=None)
        service.get_tools_info.return_value = [
            {"name": "test_tool", "description": "Test tool"}
        ]
        mock.return_value = service
        yield service


@pytest.fixture
def mock_faiss_service():
    """Mock FAISS service for testing"""
    with patch('api.routes.FAISSServiceDep') as mock:
        service = Mock()
        service.is_initialized.return_value = True
        mock.return_value = service
        yield service


@pytest.fixture
def mock_customer_manager():
    """Mock customer manager for testing"""
    with patch('api.routes.CustomerManagerDep') as mock:
        manager = Mock()
        manager.session = Mock()
        manager.session.is_active = True
        mock.return_value = manager
        yield manager


class TestChatEndpointMocked:
    """Test /chat endpoint with mocked services"""
    
    def test_chat_success(self, client, mock_agent_service):
        """Test successful chat request"""
        request_data = {
            "message": "Hello AI",
            "conversation_history": []
        }
        
        response = client.post("/chat", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "response" in data
        assert "conversation_history" in data
        assert "timestamp" in data
        
        # Verify agent was called
        mock_agent_service.invoke.assert_called_once()
    
    def test_chat_with_history(self, client, mock_agent_service):
        """Test chat with conversation history"""
        request_data = {
            "message": "Follow-up question",
            "conversation_history": [
                {"role": "user", "content": "First question"},
                {"role": "assistant", "content": "First answer"}
            ]
        }
        
        response = client.post("/chat", json=request_data)
        
        assert response.status_code == 200
        mock_agent_service.invoke.assert_called_once()
    
    def test_chat_missing_message(self, client):
        """Test chat with missing message field"""
        request_data = {
            "conversation_history": []
        }
        
        response = client.post("/chat", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data or "detail" in data
    
    def test_chat_invalid_history_format(self, client):
        """Test chat with invalid conversation history format"""
        request_data = {
            "message": "Test",
            "conversation_history": "invalid"  # Should be list
        }
        
        response = client.post("/chat", json=request_data)
        
        assert response.status_code == 422
    
    def test_chat_agent_error(self, client, mock_agent_service):
        """Test chat when agent service fails"""
        mock_agent_service.invoke.side_effect = Exception("Agent failed")
        
        request_data = {
            "message": "Test",
            "conversation_history": []
        }
        
        response = client.post("/chat", json=request_data)
        
        # Should return 500 error
        assert response.status_code == 500
        data = response.json()
        assert "error" in data


class TestStreamingChatMocked:
    """Test /chat-stream endpoint with mocked services"""
    
    @pytest.mark.asyncio
    async def test_stream_success(self, client, mock_agent_service):
        """Test successful streaming chat"""
        # Mock streaming generator
        async def mock_stream(*args, **kwargs):
            yield {"agent": {"messages": [{"type": "ai", "content": "chunk1"}]}}
            yield {"agent": {"messages": [{"type": "ai", "content": "chunk2"}]}}
        
        mock_agent_service.stream = mock_stream
        
        request_data = {
            "message": "Stream test",
            "conversation_history": []
        }
        
        response = client.post("/chat-stream", json=request_data)
        
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")
    
    def test_stream_missing_message(self, client):
        """Test streaming with missing message"""
        request_data = {
            "conversation_history": []
        }
        
        response = client.post("/chat-stream", json=request_data)
        
        assert response.status_code == 422


class TestHealthEndpointMocked:
    """Test /health endpoint with mocked services"""
    
    def test_health_all_healthy(self, client, mock_agent_service, mock_faiss_service, mock_customer_manager):
        """Test health check when all services are healthy"""
        mock_agent_service.is_initialized.return_value = True
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "components" in data
        assert "timestamp" in data
    
    def test_health_agent_unhealthy(self, client, mock_agent_service, mock_customer_manager):
        """Test health check when agent service is down"""
        mock_agent_service.is_initialized.return_value = False
        
        response = client.get("/health")
        
        assert response.status_code == 503  # Service Unavailable
        data = response.json()
        
        assert data["status"] == "unhealthy"
        assert data["components"]["agent_service"]["status"] == "unhealthy"
    
    def test_health_database_error(self, client, mock_agent_service, mock_customer_manager):
        """Test health check when database has issues"""
        mock_agent_service.is_initialized.return_value = True
        mock_customer_manager.session.is_active = False
        
        response = client.get("/health")
        
        # Should still return but indicate database issue
        assert response.status_code in [200, 503]


class TestToolsEndpointMocked:
    """Test /tools endpoint with mocked services"""
    
    def test_get_tools_success(self, client, mock_agent_service):
        """Test getting tools list"""
        mock_tools = [
            {"name": "tool1", "description": "Tool 1"},
            {"name": "tool2", "description": "Tool 2"},
            {"name": "tool3", "description": "Tool 3"}
        ]
        mock_agent_service.get_tools_info.return_value = mock_tools
        
        response = client.get("/tools")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "tools" in data
        assert "count" in data
        assert data["count"] == 3
        assert len(data["tools"]) == 3
    
    def test_get_tools_agent_not_initialized(self, client, mock_agent_service):
        """Test getting tools when agent is not initialized"""
        mock_agent_service.is_initialized.return_value = False
        
        response = client.get("/tools")
        
        # Should return error or empty list
        assert response.status_code in [200, 503]


class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API information"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data


class TestErrorHandlers:
    """Test custom error handlers"""
    
    def test_404_handler(self, client):
        """Test 404 error handler"""
        response = client.get("/nonexistent-endpoint")
        
        assert response.status_code == 404
        data = response.json()
        
        # Should use custom error format
        assert "error" in data or "detail" in data
    
    def test_405_method_not_allowed(self, client):
        """Test 405 error for wrong HTTP method"""
        response = client.put("/health")  # Health only supports GET
        
        assert response.status_code == 405
    
    def test_validation_error_format(self, client):
        """Test validation error returns proper format"""
        # Send invalid JSON
        response = client.post(
            "/chat",
            json={"invalid_field": 123}
        )
        
        assert response.status_code == 422
        data = response.json()
        
        # Should have custom validation error format
        assert "error" in data or "detail" in data
        assert "ValidationError" in str(data.get("error", ""))


class TestRequestValidation:
    """Test request validation"""
    
    def test_empty_json_body(self, client):
        """Test endpoint with empty JSON body"""
        response = client.post("/chat", json={})
        
        assert response.status_code == 422
    
    def test_malformed_json(self, client):
        """Test endpoint with malformed JSON"""
        response = client.post(
            "/chat",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_content_type(self, client):
        """Test POST without content-type"""
        response = client.post("/chat", data='{"message": "test"}')
        
        # Should either work or return validation error
        assert response.status_code in [200, 422]


class TestUtilityFunctions:
    """Test utility functions used in routes"""
    
    def test_timestamp_format(self):
        """Test timestamp formatting in responses"""
        from utils.helpers import format_timestamp
        
        timestamp = format_timestamp()
        
        # Should be ISO format
        assert "T" in timestamp
        assert "Z" in timestamp or "+" in timestamp
    
    def test_message_sanitization(self):
        """Test message sanitization"""
        from utils.helpers import sanitize_message
        
        # Test normal message
        result = sanitize_message("Hello world")
        assert result == "Hello world"
        
        # Test message with newlines
        result = sanitize_message("Line 1\nLine 2")
        assert "Line 1" in result
        assert "Line 2" in result
    
    def test_conversation_history_validation(self):
        """Test conversation history validation"""
        from utils.helpers import validate_conversation_history
        
        # Valid history
        valid_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"}
        ]
        
        is_valid, error = validate_conversation_history(valid_history)
        assert is_valid is True
        assert error is None
        
        # Invalid history - missing role
        invalid_history = [
            {"content": "Hello"}
        ]
        
        is_valid, error = validate_conversation_history(invalid_history)
        assert is_valid is False
        assert error is not None


if __name__ == "__main__":
    # Run endpoint tests
    pytest.main([__file__, "-v", "--tb=short"])

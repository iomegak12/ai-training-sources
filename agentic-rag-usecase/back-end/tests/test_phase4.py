"""
Phase 4 Validation Tests
Validates error handling, middleware, and utility functions
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch
import json

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import Request, status
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

# Import components to test
from api.middleware import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    RequestLoggingMiddleware
)
from utils.helpers import (
    format_timestamp,
    sanitize_message,
    extract_last_ai_message,
    build_conversation_history,
    validate_conversation_history,
    truncate_string,
    count_tokens_estimate,
    is_valid_url,
    safe_json_dumps,
    format_error_response
)
from main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestUtilityFunctions:
    """Test all utility helper functions"""
    
    def test_format_timestamp(self):
        """Test timestamp formatting"""
        timestamp = format_timestamp()
        
        # Should be valid ISO format
        assert isinstance(timestamp, str)
        assert "T" in timestamp
        # Should be parseable
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    
    def test_sanitize_message_normal(self):
        """Test sanitizing normal message"""
        message = "Hello, world!"
        result = sanitize_message(message)
        
        assert result == message
    
    def test_sanitize_message_with_whitespace(self):
        """Test sanitizing message with extra whitespace"""
        message = "  Hello  \n  World  "
        result = sanitize_message(message)
        
        # Should strip and normalize whitespace
        assert result.strip() == result
        assert len(result) > 0
    
    def test_sanitize_message_max_length(self):
        """Test message truncation at max length"""
        long_message = "a" * 20000
        result = sanitize_message(long_message, max_length=1000)
        
        assert len(result) <= 1000
    
    def test_extract_last_ai_message_valid(self):
        """Test extracting AI message from valid response"""
        from langchain_core.messages import HumanMessage, AIMessage
        
        messages = [
            HumanMessage(content="Question"),
            AIMessage(content="Answer")
        ]
        
        result = extract_last_ai_message(messages)
        assert result == "Answer"
    
    def test_extract_last_ai_message_empty(self):
        """Test extracting from empty messages"""
        result = extract_last_ai_message([])
        assert result == ""
    
    def test_build_conversation_history_valid(self):
        """Test building conversation from API format"""
        api_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]
        
        result = build_conversation_history(api_history)
        
        assert len(result) == 2
        assert result[0].content == "Hello"
        assert result[1].content == "Hi there"
    
    def test_build_conversation_history_empty(self):
        """Test building from empty history"""
        result = build_conversation_history([])
        assert result == []
    
    def test_validate_conversation_history_valid(self):
        """Test validating valid conversation history"""
        history = [
            {"role": "user", "content": "Test"},
            {"role": "assistant", "content": "Response"}
        ]
        
        is_valid, error = validate_conversation_history(history)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_conversation_history_invalid_missing_role(self):
        """Test validating history with missing role"""
        history = [
            {"content": "Test"}
        ]
        
        is_valid, error = validate_conversation_history(history)
        
        assert is_valid is False
        assert error is not None
        assert "role" in error.lower()
    
    def test_validate_conversation_history_invalid_missing_content(self):
        """Test validating history with missing content"""
        history = [
            {"role": "user"}
        ]
        
        is_valid, error = validate_conversation_history(history)
        
        assert is_valid is False
        assert error is not None
        assert "content" in error.lower()
    
    def test_validate_conversation_history_invalid_role(self):
        """Test validating history with invalid role"""
        history = [
            {"role": "invalid_role", "content": "Test"}
        ]
        
        is_valid, error = validate_conversation_history(history)
        
        assert is_valid is False
        assert error is not None
    
    def test_truncate_string_short(self):
        """Test truncating string shorter than max length"""
        text = "Short text"
        result = truncate_string(text, max_length=100)
        
        assert result == text
    
    def test_truncate_string_long(self):
        """Test truncating long string"""
        text = "a" * 200
        result = truncate_string(text, max_length=100)
        
        assert len(result) <= 103  # 100 + "..."
        assert result.endswith("...")
    
    def test_count_tokens_estimate(self):
        """Test token estimation"""
        text = "This is a test message"
        count = count_tokens_estimate(text)
        
        assert isinstance(count, int)
        assert count > 0
        assert count < len(text)  # Should be less than character count
    
    def test_is_valid_url_valid(self):
        """Test URL validation with valid URLs"""
        assert is_valid_url("https://example.com") is True
        assert is_valid_url("http://test.org/path") is True
        assert is_valid_url("https://sub.domain.com:8080") is True
    
    def test_is_valid_url_invalid(self):
        """Test URL validation with invalid URLs"""
        assert is_valid_url("not a url") is False
        assert is_valid_url("ftp://example.com") is True  # FTP is valid
        assert is_valid_url("") is False
        assert is_valid_url("javascript:alert(1)") is False
    
    def test_safe_json_dumps_normal(self):
        """Test JSON serialization with normal data"""
        data = {"key": "value", "number": 123}
        result = safe_json_dumps(data)
        
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed == data
    
    def test_safe_json_dumps_with_datetime(self):
        """Test JSON serialization with datetime"""
        data = {"timestamp": datetime.now()}
        result = safe_json_dumps(data)
        
        # Should convert datetime to string
        assert isinstance(result, str)
        assert "timestamp" in result
    
    def test_format_error_response(self):
        """Test error response formatting"""
        error = format_error_response(
            error_type="TestError",
            message="Test error message",
            status_code=400
        )
        
        assert error["error"] == "TestError"
        assert error["detail"] == "Test error message"
        assert error["status_code"] == 400
        assert "timestamp" in error


class TestExceptionHandlers:
    """Test custom exception handlers"""
    
    @pytest.mark.asyncio
    async def test_http_exception_handler(self):
        """Test HTTP exception handler"""
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.method = "GET"
        
        exc = StarletteHTTPException(status_code=404, detail="Not found")
        
        response = await http_exception_handler(request, exc)
        
        assert response.status_code == 404
        body = json.loads(response.body)
        assert "error" in body
        assert "detail" in body
        assert body["detail"] == "Not found"
    
    @pytest.mark.asyncio
    async def test_validation_exception_handler(self):
        """Test validation exception handler"""
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.method = "POST"
        
        # Create mock validation error
        from pydantic import BaseModel, ValidationError
        
        class TestModel(BaseModel):
            required_field: str
        
        try:
            TestModel()  # Will raise ValidationError
        except ValidationError as e:
            exc = RequestValidationError(errors=e.errors())
        
        response = await validation_exception_handler(request, exc)
        
        assert response.status_code == 422
        body = json.loads(response.body)
        assert "error" in body
        assert body["error"] == "ValidationError"
    
    @pytest.mark.asyncio
    async def test_general_exception_handler(self):
        """Test general exception handler"""
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.method = "GET"
        
        exc = Exception("Unexpected error")
        
        response = await general_exception_handler(request, exc)
        
        assert response.status_code == 500
        body = json.loads(response.body)
        assert "error" in body
        assert body["status_code"] == 500


class TestErrorHandlingIntegration:
    """Test error handling in real API requests"""
    
    def test_validation_error_real_request(self, client):
        """Test validation error with real request"""
        response = client.post("/chat", json={"invalid": "data"})
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data or "detail" in data
    
    def test_not_found_error(self, client):
        """Test 404 error handling"""
        response = client.get("/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data or "detail" in data
    
    def test_method_not_allowed_error(self, client):
        """Test 405 error handling"""
        response = client.delete("/health")  # Only GET allowed
        
        assert response.status_code == 405


class TestMiddleware:
    """Test custom middleware"""
    
    def test_request_logging_middleware(self, client):
        """Test that request logging middleware logs requests"""
        # Make a request
        response = client.get("/health")
        
        # Request should be processed normally
        assert response.status_code == 200
        
        # Middleware should not interfere with response
        data = response.json()
        assert "status" in data


class TestPhase4FilesExist:
    """Verify all Phase 4 files exist"""
    
    def test_helpers_file_exists(self):
        """Test utils/helpers.py exists"""
        helpers_path = project_root / "utils" / "helpers.py"
        assert helpers_path.exists(), "utils/helpers.py does not exist"
    
    def test_middleware_file_exists(self):
        """Test api/middleware.py exists"""
        middleware_path = project_root / "api" / "middleware.py"
        assert middleware_path.exists(), "api/middleware.py does not exist"
    
    def test_integration_tests_exist(self):
        """Test integration tests file exists"""
        tests_path = project_root / "tests" / "test_integration.py"
        assert tests_path.exists(), "tests/test_integration.py does not exist"
    
    def test_api_tests_exist(self):
        """Test API tests file exists"""
        tests_path = project_root / "tests" / "test_api.py"
        assert tests_path.exists(), "tests/test_api.py does not exist"


class TestPhase4Functionality:
    """Test that Phase 4 functionality is integrated"""
    
    def test_exception_handlers_registered(self):
        """Test that exception handlers are registered"""
        from main import app
        
        # App should have exception handlers
        assert len(app.exception_handlers) > 0
    
    def test_middleware_registered(self):
        """Test that middleware is registered"""
        from main import app
        
        # App should have middleware
        assert len(app.user_middleware) > 0
    
    def test_error_response_format_consistent(self, client):
        """Test that error responses use consistent format"""
        # Test multiple error types
        errors = []
        
        # Validation error
        response = client.post("/chat", json={})
        errors.append(response.json())
        
        # 404 error
        response = client.get("/nonexistent")
        errors.append(response.json())
        
        # All should have consistent structure
        for error in errors:
            assert "error" in error or "detail" in error


if __name__ == "__main__":
    # Run Phase 4 validation tests
    pytest.main([__file__, "-v", "--tb=short"])

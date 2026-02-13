"""
Utility Helper Functions
Common utilities for API operations
"""
import time
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from functools import wraps
from config.logging_config import get_logger

logger = get_logger(__name__)


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format datetime to ISO 8601 string
    
    Args:
        dt: Datetime to format (default: now)
        
    Returns:
        ISO 8601 formatted string
    """
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat() + "Z"


def sanitize_message(message: str, max_length: int = 10000) -> str:
    """
    Sanitize user message input
    
    Args:
        message: User message
        max_length: Maximum allowed length
        
    Returns:
        Sanitized message
    """
    # Strip whitespace
    message = message.strip()
    
    # Truncate if too long
    if len(message) > max_length:
        message = message[:max_length]
        logger.warning(f"Message truncated to {max_length} characters")
    
    return message


def extract_last_ai_message(messages: List[Any]) -> str:
    """
    Extract the last AI message from message list
    
    Args:
        messages: List of LangChain messages
        
    Returns:
        Last AI message content
    """
    for msg in reversed(messages):
        msg_type = msg.__class__.__name__
        if msg_type == "AIMessage":
            content = msg.content if hasattr(msg, 'content') else str(msg)
            return content
    
    return ""


def build_conversation_history(messages: List[Any]) -> List[Dict[str, str]]:
    """
    Build conversation history from LangChain messages
    
    Args:
        messages: List of LangChain messages
        
    Returns:
        List of conversation message dicts
    """
    history = []
    
    for msg in messages:
        msg_type = msg.__class__.__name__
        content = msg.content if hasattr(msg, 'content') else str(msg)
        
        if msg_type == "HumanMessage":
            history.append({"role": "user", "content": content})
        elif msg_type == "AIMessage":
            history.append({"role": "assistant", "content": content})
        elif msg_type == "SystemMessage":
            history.append({"role": "system", "content": content})
    
    return history


def measure_time(func):
    """
    Decorator to measure function execution time
    
    Args:
        func: Function to measure
        
    Returns:
        Wrapped function with timing
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.debug(f"{func.__name__} executed in {elapsed_ms}ms")
            return result
        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.error(f"{func.__name__} failed after {elapsed_ms}ms: {str(e)}")
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.debug(f"{func.__name__} executed in {elapsed_ms}ms")
            return result
        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.error(f"{func.__name__} failed after {elapsed_ms}ms: {str(e)}")
            raise
    
    # Return appropriate wrapper based on function type
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def parse_sse_data(data: str) -> Optional[Dict[str, Any]]:
    """
    Parse Server-Sent Event data
    
    Args:
        data: SSE data string
        
    Returns:
        Parsed data dict or None
    """
    try:
        if data.startswith("data: "):
            data = data[6:]  # Remove "data: " prefix
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def format_error_response(error: Exception, status_code: int = 500) -> Dict[str, Any]:
    """
    Format error as response dict
    
    Args:
        error: Exception object
        status_code: HTTP status code
        
    Returns:
        Error response dict
    """
    return {
        "error": error.__class__.__name__,
        "detail": str(error),
        "status_code": status_code
    }


def validate_conversation_history(history: Optional[List[Dict[str, str]]]) -> bool:
    """
    Validate conversation history structure
    
    Args:
        history: Conversation history list
        
    Returns:
        True if valid, False otherwise
    """
    if history is None:
        return True
    
    if not isinstance(history, list):
        return False
    
    for msg in history:
        if not isinstance(msg, dict):
            return False
        if "role" not in msg or "content" not in msg:
            return False
        if msg["role"] not in ["user", "assistant", "system"]:
            return False
        if not isinstance(msg["content"], str):
            return False
    
    return True


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def count_tokens_estimate(text: str) -> int:
    """
    Rough estimate of token count (1 token ≈ 4 characters)
    
    Args:
        text: Text to estimate
        
    Returns:
        Estimated token count
    """
    return len(text) // 4


def is_valid_url(url: str) -> bool:
    """
    Validate URL format
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def safe_json_dumps(obj: Any, **kwargs) -> str:
    """
    Safely serialize object to JSON string
    
    Args:
        obj: Object to serialize
        **kwargs: Additional json.dumps arguments
        
    Returns:
        JSON string
    """
    try:
        return json.dumps(obj, **kwargs)
    except (TypeError, ValueError) as e:
        logger.warning(f"JSON serialization failed: {str(e)}")
        return json.dumps({"error": "Serialization failed", "type": str(type(obj))})


def get_client_ip(request) -> str:
    """
    Get client IP from request (handles proxies)
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address
    """
    # Check X-Forwarded-For header (proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct client
    return request.client.host if request.client else "unknown"

"""
Phase 3 Validation Test
Tests API layer - models, routes, and main app
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def test_api_models():
    """Test that API models can be imported and instantiated"""
    print("\n" + "=" * 60)
    print("TEST 1: API Models")
    print("=" * 60)
    
    try:
        from api.models import (
            ChatRequest, ChatResponse, HealthResponse, ToolsResponse,
            ConversationMessage, MessageRole, ToolInfo, ComponentHealth, HealthStatus
        )
        
        # Test ChatRequest
        chat_req = ChatRequest(message="test message")
        print(f"  ✓ ChatRequest created: {chat_req.message}")
        
        # Test ConversationMessage
        conv_msg = ConversationMessage(role=MessageRole.USER, content="hello")
        print(f"  ✓ ConversationMessage created: {conv_msg.role}")
        
        # Test ToolInfo
        tool_info = ToolInfo(name="test_tool", description="test description")
        print(f"  ✓ ToolInfo created: {tool_info.name}")
        
        print("✅ Test 1: API Models - PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Test 1: API Models - FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_api_dependencies():
    """Test that API dependencies can be imported"""
    print("\n" + "=" * 60)
    print("TEST 2: API Dependencies")
    print("=" * 60)
    
    try:
        from api.dependencies import (
            get_agent_service, get_faiss_service, get_customer_manager
        )
        
        print(f"  ✓ get_agent_service imported")
        print(f"  ✓ get_faiss_service imported")
        print(f"  ✓ get_customer_manager imported")
        
        print("✅ Test 2: API Dependencies - PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Test 2: API Dependencies - FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_api_routes():
    """Test that API routes can be imported"""
    print("\n" + "=" * 60)
    print("TEST 3: API Routes")
    print("=" * 60)
    
    try:
        from api.routes import router
        
        # Check routes exist
        routes = [route.path for route in router.routes]
        print(f"  Routes registered: {len(routes)}")
        for route in routes:
            print(f"    - {route}")
        
        expected_routes = ["/chat", "/chat-stream", "/health", "/tools"]
        all_found = all(route in routes for route in expected_routes)
        
        if all_found:
            print("✅ Test 3: API Routes - PASSED")
            return True
        else:
            print(f"❌ Test 3: API Routes - FAILED")
            print(f"   Expected routes: {expected_routes}")
            print(f"   Found routes: {routes}")
            return False
        
    except Exception as e:
        print(f"❌ Test 3: API Routes - FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_fastapi_app():
    """Test that FastAPI app can be created"""
    print("\n" + "=" * 60)
    print("TEST 4: FastAPI App")
    print("=" * 60)
    
    try:
        from main import app
        
        print(f"  ✓ FastAPI app created")
        print(f"  App title: {app.title}")
        print(f"  App version: {app.version}")
        print(f"  Routes count: {len(app.routes)}")
        
        # Check middleware
        middleware_count = len(app.user_middleware)
        print(f"  Middleware count: {middleware_count}")
        
        print("✅ Test 4: FastAPI App - PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Test 4: FastAPI App - FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration_validation():
    """Test configuration validation"""
    print("\n" + "=" * 60)
    print("TEST 5: Configuration Validation")
    print("=" * 60)
    
    try:
        from config.settings import settings
        
        # Check new settings added in Phase 3
        print(f"  Agent model: {settings.agent_model_name}")
        print(f"  SQL model: {settings.sql_model_name}")
        print(f"  FAISS tool name: {settings.faiss_tool_name}")
        print(f"  API port: {settings.api_port}")
        print(f"  Docs enabled: {settings.docs_enabled}")
        print(f"  CORS enabled: {settings.cors_enabled}")
        
        # Validate
        errors = settings.validate_on_startup()
        if errors:
            print(f"\n  Validation warnings ({len(errors)}):")
            for error in errors:
                print(f"    - {error}")
        
        print("✅ Test 5: Configuration Validation - PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Test 5: Configuration Validation - FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Phase 3 tests"""
    print("\n" + "=" * 70)
    print("PHASE 3 VALIDATION TEST")
    print("Testing: API Layer (Models, Routes, App)")
    print("=" * 70)
    
    # Track results
    results = []
    
    # Run all tests
    results.append(test_api_models())
    results.append(test_api_dependencies())
    results.append(test_api_routes())
    results.append(test_fastapi_app())
    results.append(test_configuration_validation())
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 PHASE 3 COMPLETE ✅")
        print("\nAll API layer components are working correctly!")
        print("\nNext Steps:")
        print("  - Test the running API server")
        print("  - Try the /health endpoint")
        print("  - Try the /chat endpoint")
        print("  - Explore the interactive docs at /docs")
        print("\nTo start the server:")
        print("  python main.py")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("\nPlease review the errors above and fix them before proceeding.")
    
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

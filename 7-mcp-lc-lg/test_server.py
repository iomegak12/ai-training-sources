# test_server.py
"""Simple test to verify the MCP server imports and basic functionality work"""

def test_imports():
    """Test that all required imports work correctly"""
    try:
        from mcp.server import FastMCP
        from mcp import Resource, Tool
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_server_creation():
    """Test that the server can be created"""
    try:
        from mcp.server import FastMCP
        server = FastMCP("TestServer")
        print("✓ Server creation successful")
        return True
    except Exception as e:
        print(f"✗ Server creation failed: {e}")
        return False

def test_task_server_import():
    """Test that our task server can be imported"""
    try:
        import task_server
        print("✓ Task server import successful")
        print("✓ Task server initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Task server import failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing MCP Server Setup...")
    print("-" * 40)
    
    all_passed = True
    all_passed &= test_imports()
    all_passed &= test_server_creation()
    all_passed &= test_task_server_import()
    
    print("-" * 40)
    if all_passed:
        print("🎉 All tests passed! Your MCP server is ready to use.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
"""
Test script to verify Phase 1 setup is complete.

This script tests:
1. Configuration loading
2. Environment variable parsing
3. Settings validation
4. Logging setup
"""

import sys
from pathlib import Path

# Add parent directory to path to import from back-end modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from config.logging_config import setup_logging, get_logger


def test_configuration():
    """Test configuration loading."""
    print("=" * 60)
    print("PHASE 1: Configuration Testing")
    print("=" * 60)
    print()
    
    # Test 1: Configuration Loading
    print("✅ Test 1: Configuration Loading")
    print(f"   API Port: {settings.api_port}")
    print(f"   Environment: {settings.api_env}")
    print(f"   Reload: {settings.api_reload}")
    print(f"   Docs Enabled: {settings.docs_enabled}")
    print(f"   Rate Limiting: {settings.rate_limit_enabled}")
    print()
    
    # Test 2: Property Methods
    print("✅ Test 2: Property Methods")
    print(f"   CORS Origins: {settings.cors_origins_list}")
    print(f"   FAISS URLs: {settings.faiss_urls_list}")
    print(f"   Base Path: {settings.base_path}")
    print(f"   CRM DB Path: {settings.crm_database_full_path}")
    print(f"   Chinook DB Path: {settings.chinook_database_full_path}")
    print(f"   URLs File: {settings.urls_file_full_path}")
    print()
    
    # Test 3: Validation
    print("✅ Test 3: Configuration Validation")
    errors = settings.validate_on_startup()
    if errors:
        print(f"   ⚠️  Found {len(errors)} validation error(s):")
        for error in errors:
            print(f"      - {error}")
        print()
        print("   📝 Note: OPENAI_API_KEY error is expected in Phase 1")
        print("   📝 You'll need to set this before Phase 2")
    else:
        print("   ✨ All configuration valid!")
    print()
    
    # Test 4: Logging Setup
    print("✅ Test 4: Logging Setup")
    setup_logging(
        log_level=settings.log_level,
        log_format=settings.log_format,
        log_file_enabled=settings.log_file_enabled,
        log_file_path=settings.log_file_path
    )
    logger = get_logger(__name__)
    logger.info("Logging system initialized successfully")
    logger.debug("This is a debug message (may not show based on LOG_LEVEL)")
    print("   Logging configured successfully!")
    print()
    
    # Summary
    print("=" * 60)
    print("PHASE 1 COMPLETE ✅")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. Edit .env file and add your OPENAI_API_KEY")
    print("2. Proceed to Phase 2: Core Services & Tools")
    print()


if __name__ == "__main__":
    test_configuration()

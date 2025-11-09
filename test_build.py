"""Test script to verify the SDK package works correctly."""

import sys
from pathlib import Path

def test_imports():
    """Test that all SDK components can be imported."""
    print("Testing imports...")
    
    try:
        from pesapal import (
            PesapalClient,
            PaymentRequest,
            PaymentResponse,
            PaymentStatus,
            IPNRegistration,
            PesapalError,
            PesapalAPIError,
            PesapalAuthenticationError,
            PesapalValidationError,
            PesapalNetworkError,
        )
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_version():
    """Test that version is accessible."""
    print("\nTesting version...")
    
    try:
        from pesapal import __version__
        print(f"✅ Version: {__version__}")
        return True
    except AttributeError:
        print("❌ Version not found")
        return False

def test_client_initialization():
    """Test client can be initialized."""
    print("\nTesting client initialization...")
    
    try:
        from pesapal import PesapalClient
        
        # Test with dummy credentials
        client = PesapalClient(
            consumer_key="test_key",
            consumer_secret="test_secret",
            sandbox=True
        )
        print("✅ Client initialized successfully")
        print(f"   - Sandbox mode: {client.sandbox}")
        print(f"   - Base URL: {client.base_url}")
        return True
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return False

def test_models():
    """Test that models can be instantiated."""
    print("\nTesting models...")
    
    try:
        from pesapal import PaymentRequest
        from decimal import Decimal
        
        # Test PaymentRequest model
        request = PaymentRequest(
            id="TEST-123",
            amount=Decimal("100.00"),
            currency="KES",
            description="Test payment",
            callback_url="https://example.com/callback",
            notification_id="test-ipn-id"
        )
        print("✅ PaymentRequest model works")
        print(f"   - Order ID: {request.id}")
        print(f"   - Amount: {request.amount}")
        print(f"   - Currency: {request.currency}")
        return True
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_exceptions():
    """Test that exceptions can be raised."""
    print("\nTesting exceptions...")
    
    try:
        from pesapal import (
            PesapalError,
            PesapalAPIError,
            PesapalAuthenticationError,
            PesapalValidationError,
            PesapalNetworkError,
        )
        
        # Test exception hierarchy
        assert issubclass(PesapalAPIError, PesapalError)
        assert issubclass(PesapalAuthenticationError, PesapalAPIError)
        assert issubclass(PesapalValidationError, PesapalError)
        assert issubclass(PesapalNetworkError, PesapalError)
        
        print("✅ Exception hierarchy correct")
        return True
    except Exception as e:
        print(f"❌ Exception test failed: {e}")
        return False

def test_utils():
    """Test utility functions."""
    print("\nTesting utilities...")
    
    try:
        from pesapal.utils import generate_signature, verify_webhook_signature
        
        # Test signature generation
        data = {"key1": "value1", "key2": "value2"}
        secret = "test_secret"
        signature = generate_signature(data, secret)
        
        assert isinstance(signature, str)
        assert len(signature) > 0
        
        # Test signature verification
        is_valid = verify_webhook_signature(data, signature, secret)
        assert is_valid == True
        
        print("✅ Utility functions work")
        return True
    except Exception as e:
        print(f"❌ Utility test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Pesapal Python SDK - Build Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_version,
        test_client_initialization,
        test_models,
        test_exceptions,
        test_utils,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! Package is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please fix issues before publishing.")
        return 1

if __name__ == "__main__":
    sys.exit(main())


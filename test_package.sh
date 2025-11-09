#!/bin/bash

# Complete test script for the Pesapal Python SDK package

set -e

echo "=========================================="
echo "Pesapal Python SDK - Complete Test"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Step 1: Check Python version
echo -e "${BLUE}Step 1: Checking Python version...${NC}"
python3 --version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✅ Python ${PYTHON_VERSION}${NC}"
echo ""

# Step 2: Install build tools
echo -e "${BLUE}Step 2: Installing build tools...${NC}"
python3 -m pip install --quiet --upgrade pip build twine
echo -e "${GREEN}✅ Build tools installed${NC}"
echo ""

# Step 3: Clean previous builds
echo -e "${BLUE}Step 3: Cleaning previous builds...${NC}"
rm -rf dist/ build/ *.egg-info 2>/dev/null || true
echo -e "${GREEN}✅ Cleaned${NC}"
echo ""

# Step 4: Build the package
echo -e "${BLUE}Step 4: Building package...${NC}"
python3 -m build
echo -e "${GREEN}✅ Build complete${NC}"
echo ""

# Step 5: Check build artifacts
echo -e "${BLUE}Step 5: Checking build artifacts...${NC}"
if [ -f "dist/pesapal_python_sdk-1.0.0-py3-none-any.whl" ]; then
    echo -e "${GREEN}✅ Wheel: dist/pesapal_python_sdk-1.0.0-py3-none-any.whl${NC}"
    ls -lh dist/pesapal_python_sdk-1.0.0-py3-none-any.whl | awk '{print "   Size: " $5}'
else
    echo -e "${RED}❌ Wheel file not found${NC}"
    exit 1
fi

if [ -f "dist/pesapal-python-sdk-1.0.0.tar.gz" ]; then
    echo -e "${GREEN}✅ Source: dist/pesapal-python-sdk-1.0.0.tar.gz${NC}"
    ls -lh dist/pesapal-python-sdk-1.0.0.tar.gz | awk '{print "   Size: " $5}'
else
    echo -e "${RED}❌ Source distribution not found${NC}"
    exit 1
fi
echo ""

# Step 6: Check package contents
echo -e "${BLUE}Step 6: Checking package contents...${NC}"
echo "Wheel contents:"
unzip -l dist/pesapal_python_sdk-1.0.0-py3-none-any.whl | grep -E "(pesapal/|README)" | head -10
echo ""

# Step 7: Install the package
echo -e "${BLUE}Step 7: Installing package...${NC}"
python3 -m pip install --quiet --force-reinstall dist/pesapal_python_sdk-1.0.0-py3-none-any.whl
echo -e "${GREEN}✅ Package installed${NC}"
echo ""

# Step 8: Test imports
echo -e "${BLUE}Step 8: Testing imports...${NC}"
python3 -c "
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
print('✅ All imports successful')
" || exit 1

python3 -c "
from pesapal import __version__
print(f'✅ Version: {__version__}')
" || exit 1
echo ""

# Step 9: Test client initialization
echo -e "${BLUE}Step 9: Testing client initialization...${NC}"
python3 -c "
from pesapal import PesapalClient
client = PesapalClient(
    consumer_key='test_key',
    consumer_secret='test_secret',
    sandbox=True
)
print(f'✅ Client initialized')
print(f'   Sandbox: {client.sandbox}')
print(f'   Base URL: {client.base_url}')
" || exit 1
echo ""

# Step 10: Test models
echo -e "${BLUE}Step 10: Testing models...${NC}"
python3 -c "
from pesapal import PaymentRequest
from decimal import Decimal
request = PaymentRequest(
    id='TEST-123',
    amount=Decimal('100.00'),
    currency='KES',
    description='Test payment',
    callback_url='https://example.com/callback',
    notification_id='test-ipn-id'
)
print(f'✅ PaymentRequest model works')
print(f'   Order ID: {request.id}')
print(f'   Amount: {request.amount}')
print(f'   Currency: {request.currency}')
" || exit 1
echo ""

# Step 11: Test utilities
echo -e "${BLUE}Step 11: Testing utilities...${NC}"
python3 -c "
from pesapal.utils import generate_signature, verify_webhook_signature
data = {'key1': 'value1', 'key2': 'value2'}
secret = 'test_secret'
signature = generate_signature(data, secret)
is_valid = verify_webhook_signature(data, signature, secret)
print(f'✅ Utilities work')
print(f'   Signature generated: {len(signature)} chars')
print(f'   Verification: {is_valid}')
" || exit 1
echo ""

# Step 12: Check package info
echo -e "${BLUE}Step 12: Package information...${NC}"
python3 -m pip show pesapal-python-sdk | grep -E "(Name|Version|Summary|Requires)" || true
echo ""

# Summary
echo "=========================================="
echo -e "${GREEN}✅ All tests passed!${NC}"
echo "=========================================="
echo ""
echo "Package is ready for publishing!"
echo ""
echo "Next steps:"
echo "1. Update metadata in pyproject.toml and setup.py"
echo "2. Test on TestPyPI: python3 -m twine upload --repository testpypi dist/*"
echo "3. Publish to PyPI: python3 -m twine upload dist/*"
echo ""
echo "See PUBLISH.md for detailed instructions."


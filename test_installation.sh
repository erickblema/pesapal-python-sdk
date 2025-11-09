#!/bin/bash

# Test script for building and installing the Pesapal Python SDK

set -e  # Exit on error

echo "=========================================="
echo "Pesapal Python SDK - Installation Test"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Clean previous builds
echo -e "${YELLOW}Step 1: Cleaning previous builds...${NC}"
rm -rf dist/ build/ *.egg-info
echo -e "${GREEN}✅ Cleaned${NC}"
echo ""

# Step 2: Check if build tools are installed
echo -e "${YELLOW}Step 2: Checking build tools...${NC}"
if ! python -m pip show build twine > /dev/null 2>&1; then
    echo "Installing build tools..."
    python -m pip install build twine
fi
echo -e "${GREEN}✅ Build tools ready${NC}"
echo ""

# Step 3: Build the package
echo -e "${YELLOW}Step 3: Building package...${NC}"
python -m build
echo -e "${GREEN}✅ Build complete${NC}"
echo ""

# Step 4: Check build artifacts
echo -e "${YELLOW}Step 4: Checking build artifacts...${NC}"
if [ -f "dist/pesapal_python_sdk-1.0.0-py3-none-any.whl" ]; then
    echo -e "${GREEN}✅ Wheel file created${NC}"
    ls -lh dist/pesapal_python_sdk-1.0.0-py3-none-any.whl
else
    echo -e "${RED}❌ Wheel file not found${NC}"
    exit 1
fi

if [ -f "dist/pesapal-python-sdk-1.0.0.tar.gz" ]; then
    echo -e "${GREEN}✅ Source distribution created${NC}"
    ls -lh dist/pesapal-python-sdk-1.0.0.tar.gz
else
    echo -e "${RED}❌ Source distribution not found${NC}"
    exit 1
fi
echo ""

# Step 5: Install the package
echo -e "${YELLOW}Step 5: Installing package from wheel...${NC}"
python -m pip install --force-reinstall dist/pesapal_python_sdk-1.0.0-py3-none-any.whl
echo -e "${GREEN}✅ Package installed${NC}"
echo ""

# Step 6: Test imports
echo -e "${YELLOW}Step 6: Testing imports...${NC}"
python -c "
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
print(f'✅ Version: {__import__(\"pesapal\").__version__}')
"
echo ""

# Step 7: Run comprehensive tests
echo -e "${YELLOW}Step 7: Running comprehensive tests...${NC}"
python test_build.py
TEST_RESULT=$?
echo ""

# Step 8: Check package info
echo -e "${YELLOW}Step 8: Package information...${NC}"
python -m pip show pesapal-python-sdk
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review the package: pip show pesapal-python-sdk"
    echo "2. Test in a virtual environment:"
    echo "   python -m venv test_env"
    echo "   source test_env/bin/activate  # On Windows: test_env\\Scripts\\activate"
    echo "   pip install dist/pesapal_python_sdk-1.0.0-py3-none-any.whl"
    echo "3. Publish to TestPyPI: python -m twine upload --repository testpypi dist/*"
    echo "4. Publish to PyPI: python -m twine upload dist/*"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo "Please fix the issues before publishing."
    exit 1
fi


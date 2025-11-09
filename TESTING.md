# Testing Before Publishing

This guide helps you test the Pesapal Python SDK package before publishing to PyPI.

## Quick Test

Run the automated test script:

```bash
# On Unix/Mac
./test_installation.sh

# On Windows
bash test_installation.sh
```

Or run the Python test script:

```bash
python test_build.py
```

## Manual Testing Steps

### 1. Clean Previous Builds

```bash
rm -rf dist/ build/ *.egg-info
```

### 2. Install Build Tools

```bash
pip install build twine
```

### 3. Build the Package

```bash
python -m build
```

This creates:
- `dist/pesapal_python_sdk-1.0.0-py3-none-any.whl` (wheel)
- `dist/pesapal-python-sdk-1.0.0.tar.gz` (source distribution)

### 4. Install the Package Locally

```bash
pip install dist/pesapal_python_sdk-1.0.0-py3-none-any.whl
```

Or install from source:

```bash
pip install dist/pesapal-python-sdk-1.0.0.tar.gz
```

### 5. Test Imports

```python
# Test basic imports
from pesapal import PesapalClient
from pesapal import PaymentRequest, PaymentResponse, PaymentStatus
from pesapal import IPNRegistration
from pesapal import PesapalError, PesapalAPIError

# Test version
from pesapal import __version__
print(__version__)  # Should print: 1.0.0
```

### 6. Test Client Initialization

```python
from pesapal import PesapalClient

client = PesapalClient(
    consumer_key="test_key",
    consumer_secret="test_secret",
    sandbox=True
)

print(client.sandbox)  # Should print: True
print(client.base_url)  # Should print sandbox URL
```

### 7. Test Models

```python
from pesapal import PaymentRequest
from decimal import Decimal

request = PaymentRequest(
    id="TEST-123",
    amount=Decimal("100.00"),
    currency="KES",
    description="Test payment",
    callback_url="https://example.com/callback",
    notification_id="test-ipn-id"
)

print(request.id)  # Should print: TEST-123
print(request.amount)  # Should print: 100.00
```

### 8. Test Utilities

```python
from pesapal.utils import generate_signature, verify_webhook_signature

data = {"key1": "value1", "key2": "value2"}
secret = "test_secret"

# Generate signature
signature = generate_signature(data, secret)
print(signature)  # Should print a base64 string

# Verify signature
is_valid = verify_webhook_signature(data, signature, secret)
print(is_valid)  # Should print: True
```

## Test in Clean Environment

To ensure the package works in a fresh environment:

### Option 1: New Virtual Environment

```bash
# Create new virtual environment
python -m venv test_env

# Activate it
# On Unix/Mac:
source test_env/bin/activate
# On Windows:
test_env\Scripts\activate

# Install the package
pip install dist/pesapal_python_sdk-1.0.0-py3-none-any.whl

# Test
python -c "from pesapal import PesapalClient; print('OK')"

# Deactivate
deactivate
```

### Option 2: Test with pip install from local

```bash
# Install directly from wheel
pip install --force-reinstall dist/pesapal_python_sdk-1.0.0-py3-none-any.whl

# Verify installation
pip show pesapal-python-sdk

# Test import
python -c "from pesapal import PesapalClient; print('OK')"
```

## Check Package Contents

Verify what's included in the package:

```bash
# Extract and inspect wheel
unzip -l dist/pesapal_python_sdk-1.0.0-py3-none-any.whl

# Or extract source distribution
tar -tzf dist/pesapal-python-sdk-1.0.0.tar.gz
```

You should see:
- `pesapal/__init__.py`
- `pesapal/client.py`
- `pesapal/models.py`
- `pesapal/exceptions.py`
- `pesapal/constants.py`
- `pesapal/utils.py`
- `README_SDK.md` (as README.md in package)

You should NOT see:
- `app/` directory
- `main.py`
- `test_*.py` files

## Verify Dependencies

Check that only required dependencies are listed:

```bash
pip show pesapal-python-sdk
```

Should show:
- `httpx>=0.24.0`
- `pydantic>=2.0.0`

Should NOT show:
- `fastapi`
- `motor`
- `pymongo`
- `uvicorn`

## Test Package Metadata

```bash
# Check package info
pip show pesapal-python-sdk

# Should display:
# Name: pesapal-python-sdk
# Version: 1.0.0
# Summary: Python SDK for Pesapal Payment Gateway API 3.0
# Requires: httpx, pydantic
```

## Common Issues

### Issue: "No module named 'pesapal'"

**Solution:** Make sure you installed the package:
```bash
pip install dist/pesapal_python_sdk-1.0.0-py3-none-any.whl
```

### Issue: "Package includes app/ directory"

**Solution:** Check `MANIFEST.in` and `setup.py` to ensure `app/` is excluded.

### Issue: "Missing dependencies"

**Solution:** Verify `pyproject.toml` has correct dependencies listed.

### Issue: "Import errors"

**Solution:** Check `pesapal/__init__.py` exports all necessary classes.

## Next Steps

Once all tests pass:

1. ✅ Update metadata (name, email, URLs)
2. ✅ Test build locally
3. ✅ Test installation
4. ✅ Publish to TestPyPI
5. ✅ Test from TestPyPI
6. ✅ Publish to PyPI

See `PUBLISH.md` for publishing instructions.


# Publishing to PyPI

This guide explains how to publish the Pesapal Python SDK to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account at [pypi.org](https://pypi.org)
2. **API Token**: Generate an API token from your PyPI account settings
3. **Build Tools**: Install build tools:
   ```bash
   pip install build twine
   ```

## Step 1: Update Package Information

Before publishing, update the following files if needed:

1. **`pyproject.toml`**:
   - ✅ Author information is set (Erick Lema, ericklema360@gmail.com)
   - Update `project.urls` with your GitHub repository URLs (if you have a repository)

2. **`setup.py`**:
   - ✅ Author information is set
   - Update `url` with your repository URL (if you have a repository)

3. **`README_SDK.md`**:
   - Update GitHub repository URLs (if you have a repository)
   - Update support links (if needed)

## Step 2: Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m build
```

This creates:
- `dist/pesapal-python-sdk-1.0.0.tar.gz` (source distribution)
- `dist/pesapal_python_sdk-1.0.0-py3-none-any.whl` (wheel)

## Step 3: Test the Build

```bash
# Install the built package locally
pip install dist/pesapal_python_sdk-1.0.0-py3-none-any.whl

# Test import
python -c "from pesapal import PesapalClient; print('OK')"
```

## Step 4: Test on TestPyPI (Recommended)

First, test on TestPyPI to ensure everything works:

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Install from TestPyPI to verify
pip install --index-url https://test.pypi.org/simple/ pesapal-python-sdk
```

## Step 5: Publish to PyPI

Once tested, publish to the real PyPI:

```bash
# Upload to PyPI
python -m twine upload dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your PyPI API token

## Step 6: Verify Publication

1. Check PyPI: https://pypi.org/project/pesapal-python-sdk/
2. Install and test:
   ```bash
   pip install pesapal-python-sdk
   python -c "from pesapal import PesapalClient; print('Installed successfully!')"
   ```

## Updating the Package

For subsequent releases:

1. **Update version** in:
   - `pyproject.toml` (`version = "1.0.1"`)
   - `setup.py` (`version="1.0.1"`)
   - `pesapal/__init__.py` (`__version__ = "1.0.1"`)

2. **Update CHANGELOG** in `README_SDK.md`

3. **Build and publish**:
   ```bash
   python -m build
   python -m twine upload dist/*
   ```

## Package Name Considerations

The package name `pesapal-python-sdk` should be available. If not, consider:
- `pesapal-sdk-python`
- `pesapal-payment-sdk`
- `pesapal-api-python`

Check availability at: https://pypi.org/project/pesapal-python-sdk/

## Important Notes

- **Never publish test credentials** - Ensure no secrets in the package
- **Version numbers** - Follow semantic versioning (MAJOR.MINOR.PATCH)
- **README** - Make sure README_SDK.md is comprehensive
- **Dependencies** - Keep SDK dependencies minimal (only httpx and pydantic)
- **License** - Add a LICENSE file (MIT recommended)

## Troubleshooting

### "Package already exists"
- The package name is taken, choose a different name

### "Invalid credentials"
- Check your API token is correct
- Ensure you're using `__token__` as username

### "Missing required metadata"
- Ensure all fields in `pyproject.toml` are filled
- Check README file exists and is valid markdown


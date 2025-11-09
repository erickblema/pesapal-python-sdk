# Publishing Guide

## Quick Publish

### 1. Test on TestPyPI

```bash
# Build
python3 -m build

# Upload to TestPyPI
python3 -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ pesapal-python-sdk
```

### 2. Publish to PyPI

**Option A: Using GitHub Actions (Recommended)**

1. Update version in `pyproject.toml`, `setup.py`, `pesapal/__init__.py`
2. Commit and push
3. Create GitHub Release → Workflow publishes automatically

**Option B: Manual**

```bash
python3 -m build
python3 -m twine upload dist/*
```

## GitHub Secrets Required

- `PYPI_API_TOKEN` - For publishing to PyPI
- `TEST_PYPI_API_TOKEN` - For testing on TestPyPI (optional)

## Workflow

The `.github/workflows/workflow.yml` automatically:
- Builds package on release
- Publishes to PyPI
- Can be manually triggered for TestPyPI testing


# GitHub Actions Workflows

## Workflows

### 1. `publish.yml` - Publish to PyPI

Automatically publishes the package to PyPI when:
- A new release is published on GitHub
- Manually triggered via workflow_dispatch

**Setup:**
1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Add secrets:
   - `PYPI_API_TOKEN` - Your PyPI API token
   - `TEST_PYPI_API_TOKEN` - Your TestPyPI API token (optional)

**Usage:**
- **Automatic**: Create a GitHub release to trigger publishing
- **Manual**: Go to Actions → Publish to PyPI → Run workflow

### 2. `test.yml` - Test Package

Runs tests on multiple Python versions (3.8-3.12) on every push and pull request.

**Tests:**
- Package builds successfully
- Package installs correctly
- All imports work
- Client initializes correctly

## Publishing Process

### Option 1: Automatic (Recommended)

1. Update version in:
   - `pyproject.toml`
   - `setup.py`
   - `pesapal/__init__.py`

2. Commit and push:
   ```bash
   git add .
   git commit -m "Release v1.0.0"
   git push
   ```

3. Create GitHub Release:
   - Go to Releases → Create a new release
   - Tag: `v1.0.0`
   - Title: `v1.0.0`
   - Publish release

4. Workflow automatically publishes to PyPI

### Option 2: Manual

1. Go to Actions tab
2. Select "Publish to PyPI"
3. Click "Run workflow"
4. Workflow publishes to PyPI

## Secrets Setup

### Get PyPI API Token

1. Go to [pypi.org](https://pypi.org)
2. Account Settings → API tokens
3. Create new token
4. Copy token
5. Add to GitHub Secrets as `PYPI_API_TOKEN`

### Get TestPyPI API Token

1. Go to [test.pypi.org](https://test.pypi.org)
2. Same process as above
3. Add to GitHub Secrets as `TEST_PYPI_API_TOKEN`


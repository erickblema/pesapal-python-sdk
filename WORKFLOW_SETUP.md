# GitHub Actions Workflow Setup

## ✅ Workflow Created

**File:** `.github/workflows/workflow.yml`

This workflow automatically publishes your package to PyPI when you create a GitHub release.

## 🔧 Setup Instructions

### 1. Get PyPI API Token

1. Go to [pypi.org](https://pypi.org) and log in
2. Go to **Account Settings** → **API tokens**
3. Click **Add API token**
4. Token name: `pesapal-python-sdk`
5. Scope: **Entire account** (or project-specific)
6. Click **Add token**
7. **Copy the token** (you'll only see it once!)

### 2. Add Token to GitHub Secrets

1. Go to your GitHub repository: `https://github.com/erickblema/pesapal-python-sdk`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `PYPI_API_TOKEN`
5. Value: Paste your PyPI API token
6. Click **Add secret**

### 3. How to Publish

#### Option A: Automatic (Recommended)

1. **Update version** in:
   - `pyproject.toml`: `version = "1.0.0"`
   - `setup.py`: `version="1.0.0"`
   - `pesapal/__init__.py`: `__version__ = "1.0.0"`

2. **Commit and push:**
   ```bash
   git add .
   git commit -m "Release v1.0.0"
   git push
   ```

3. **Create GitHub Release:**
   - Go to repository → **Releases** → **Create a new release**
   - Tag: `v1.0.0` (must start with `v`)
   - Title: `v1.0.0`
   - Description: Release notes
   - Click **Publish release**

4. **Workflow runs automatically** and publishes to PyPI!

#### Option B: Manual Trigger

1. Go to **Actions** tab
2. Select **Publish to PyPI** workflow
3. Click **Run workflow**
4. Select branch (usually `main`)
5. Click **Run workflow**

## 📋 Workflow Details

**Triggers:**
- ✅ When a GitHub release is published
- ✅ Manual trigger via Actions tab

**Steps:**
1. Checkout code
2. Set up Python 3.9
3. Install build tools (build, twine)
4. Build package
5. Publish to PyPI
6. Verify publication

## 🔒 Security

- API token is stored in GitHub Secrets (encrypted)
- Token is never exposed in logs
- Only repository admins can access secrets

## ✅ Verification

After publishing, verify:
1. Check PyPI: https://pypi.org/project/pesapal-python-sdk/
2. Install: `pip install pesapal-python-sdk`
3. Test: `python -c "from pesapal import PesapalClient; print('OK')"`

## 🎉 Ready!

Once you add the `PYPI_API_TOKEN` secret, you're ready to publish automatically!


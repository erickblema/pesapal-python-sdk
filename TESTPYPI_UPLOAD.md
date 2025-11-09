# Upload to TestPyPI

## Step 1: Get TestPyPI API Token

1. Go to https://test.pypi.org/account/register/ (create account if needed)
2. Log in at https://test.pypi.org/manage/account/
3. Go to "API tokens" section
4. Create a new token with scope: "Entire account" or "Project: pesapal-python-sdk"
5. Copy the token (starts with `pypi-`)

## Step 2: Upload Package

Run this command (replace `YOUR_TOKEN` with your actual token):

```bash
python3 -m twine upload --repository testpypi dist/*
```

When prompted:
- Username: `__token__`
- Password: `YOUR_TOKEN` (the token you copied)

## Step 3: Test Installation

After upload, test the installation:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pesapal-python-sdk
```

## Alternative: Use Environment Variable

You can also set the token as an environment variable:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR_TOKEN_HERE
python3 -m twine upload --repository testpypi dist/*
```


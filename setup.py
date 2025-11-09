"""Setup configuration for Pesapal Python SDK."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README - prefer README_SDK.md, fallback to README.md
readme_sdk = Path(__file__).parent / "README_SDK.md"
readme_default = Path(__file__).parent / "README.md"

if readme_sdk.exists():
    long_description = readme_sdk.read_text(encoding="utf-8")
elif readme_default.exists():
    long_description = readme_default.read_text(encoding="utf-8")
else:
    long_description = ""

setup(
    name="pesapal-python-sdk",
    version="1.0.0",
    description="Python SDK for Pesapal Payment Gateway API 3.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Erick Lema",
    author_email="ericklema360@gmail.com",
    url="https://github.com/erickblema/pesapal-python-sdk",
    packages=find_packages(exclude=["tests", "app", "*.tests", "*.tests.*"]),
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.24.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
    ],
    keywords=["pesapal", "payment", "gateway", "sdk", "api", "fintech"],
    include_package_data=True,
    zip_safe=False,
)


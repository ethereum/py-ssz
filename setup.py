#!/usr/bin/env python
from setuptools import (
    find_packages,
    setup,
)

extras_require = {
    "dev": [
        "build>=0.9.0",
        "bump_my_version>=0.19.0",
        "ipython",
        "pre-commit>=3.4.0",
        "tox>=4.0.0",
        "twine",
        "wheel",
    ],
    "docs": [
        "sphinx>=6.0.0",
        "sphinx-autobuild>=2021.3.14",
        "sphinx_rtd_theme>=1.0.0",
        "towncrier>=24,<25",
    ],
    "test": [
        "hypothesis>=6.22.0,<6.108.7",
        "pytest>=7.0.0",
        "pytest-xdist>=2.4.0",
    ],
    "yaml": [
        "ruamel.yaml>=0.17.0",
    ],
}

extras_require["dev"] = (
    extras_require["dev"]
    + extras_require["docs"]
    + extras_require["test"]
    + extras_require["yaml"]
)

with open("./README.md") as readme:
    long_description = readme.read()


setup(
    name="ssz",
    # *IMPORTANT*: Don't manually change the version here. See Contributing docs for the release process.
    version="0.5.2",
    description="""ssz: Python implementation of the Simple Serialization encoding and decoding""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="The Ethereum Foundation",
    author_email="snakecharmers@ethereum.org",
    url="https://github.com/ethereum/py-ssz",
    include_package_data=True,
    install_requires=[
        "eth-utils>=2",
        "lru-dict>=1.1.6",
        "pyrsistent>=0.16.0",
    ],
    python_requires=">=3.8, <4",
    extras_require=extras_require,
    py_modules=["ssz"],
    license="MIT",
    zip_safe=False,
    keywords="ethereum",
    packages=find_packages(exclude=["scripts", "scripts.*", "tests", "tests.*"]),
    package_data={"ssz": ["py.typed"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)

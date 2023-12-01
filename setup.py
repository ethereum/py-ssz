#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import (
    find_packages,
    setup,
)

extras_require = {
    "dev": [
        "build>=0.9.0",
        "bumpversion>=0.5.3",
        "ipython",
        "pre-commit>=3.4.0",
        "tox>=4.0.0",
        "twine",
        "wheel",
    ],
    "docs": [
        "sphinx>=6.0.0",
        "sphinx_rtd_theme>=1.0.0",
        "towncrier>=21,<22",
    ],
    "test": [
        "hypothesis==4.54.0",
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
    # *IMPORTANT*: Don't manually change the version here. Use `make bump`, as described in readme
    version="0.3.1",
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
        # When updating to a newer version of pyrsistent, please check that the interface
        # `transform` expects has not changed (see https://github.com/tobgu/pyrsistent/issues/180)
        "pyrsistent>=0.16.0,<0.17",
    ],
    python_requires=">=3.8, <4",
    extras_require=extras_require,
    py_modules=["ssz"],
    license="MIT",
    zip_safe=False,
    keywords="ethereum",
    packages=find_packages(exclude=["tests", "tests.*"]),
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
    ],
)

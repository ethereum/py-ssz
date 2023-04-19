#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

extras_require = {
    "test": [
        "pytest>=7.0.0",
        "pytest-xdist>=2.4.0",
        "hypothesis==4.54.0",
        "mypy-extensions>=0.4.1",
    ],
    "lint": [
        "flake8==3.7.9",
        "isort>=5.10.1,<6",
        "pydocstyle>=6.0.0",
        "black>=23",
    ],
    "doc": [
        "sphinx>=5.0.0",
        "sphinx_rtd_theme>=1.0.0",
        "towncrier>=21,<22",
    ],
    "dev": [
        "bumpversion>=0.5.3",
        "pytest-watch>=4.1.0",
        "tox>=4.0.0",
        "build>=0.9.0",
        "wheel",
        "twine",
        "ipython",
    ],
    "yaml": [
        "ruamel.yaml>=0.17.0",
    ],
}

extras_require["dev"] = (
    extras_require["dev"]
    + extras_require["test"]
    + extras_require["lint"]
    + extras_require["doc"]
    + extras_require["yaml"]
)

with open("./README.md") as readme:
    long_description = readme.read()


setup(
    name="ssz",
    # *IMPORTANT*: Don't manually change the version here. Use `make bump`, as described in readme
    version="0.3.0",
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
    setup_requires=[],
    python_requires=">=3.7, <4",
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
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

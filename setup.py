#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

extras_require = {
    "test": [
        "pytest==4.4.0",
        "pytest-xdist==1.28.0",
        "pytest-watch>=4.1.0,<5",
        "tox>=2.9.1,<3",
        "hypothesis==3.69.5",
        "ruamel.yaml==0.15.87",
        "mypy-extensions>=0.4.1,<1.0.0",
    ],
    "lint": ["flake8==3.7.8", "isort==4.3.21", "black==19.3b"],
    "doc": ["Sphinx>=1.6.5,<2", "sphinx_rtd_theme>=0.1.9"],
    "dev": ["bumpversion>=0.5.3,<1", "wheel", "twine", "ipython", "pre-commit==1.18.3"],
}

extras_require["dev"] = (
    extras_require["dev"]
    + extras_require["test"]
    + extras_require["lint"]
    + extras_require["doc"]
)

setup(
    name="ssz",
    # *IMPORTANT*: Don't manually change the version here. Use `make bump`, as described in readme
    version="0.2.0",
    description="""ssz: Python implementation of the Simple Serialization encoding and decoding""",
    long_description_markdown_filename="README.md",
    author="Jason Carver",
    author_email="ethcalibur+pip@gmail.com",
    url="https://github.com/ethereum/py-ssz",
    include_package_data=True,
    install_requires=[
        "eth-utils>=1,<2",
        "lru-dict>=1.1.6",
        # When updating to a newer version of pyrsistent, please check that the interface
        # `transform` expects has not changed (see https://github.com/tobgu/pyrsistent/issues/180)
        "pyrsistent==0.15.6",
    ],
    setup_requires=["setuptools-markdown"],
    python_requires=">=3.6, <4",
    extras_require=extras_require,
    py_modules=["ssz"],
    license="MIT",
    zip_safe=False,
    keywords="ethereum",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)

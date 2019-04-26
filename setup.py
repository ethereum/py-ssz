#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import (
    setup,
    find_packages,
)

extras_require = {
    'test': [
        "pytest==4.4.0",
        "pytest-xdist==1.28.0",
        "pytest-watch>=4.1.0,<5",
        "tox>=2.9.1,<3",
        "hypothesis==3.69.5",
        "ruamel.yaml==0.15.87",
    ],
    'lint': [
        "flake8==3.4.1",
        "isort>=4.2.15,<5",
    ],
    'doc': [
        "Sphinx>=1.6.5,<2",
        "sphinx_rtd_theme>=0.1.9",
    ],
    'dev': [
        "bumpversion>=0.5.3,<1",
        "wheel",
        "twine",
        "ipython",
    ],
}

extras_require['dev'] = (
    extras_require['dev'] +
    extras_require['test'] +
    extras_require['lint'] +
    extras_require['doc']
)

setup(
    name='ssz',
    # *IMPORTANT*: Don't manually change the version here. Use `make bump`, as described in readme
    version='0.1.0-alpha.6',
    description="""ssz: Python implementation of the Simple Serialization encoding and decoding""",
    long_description_markdown_filename='README.md',
    author='Jason Carver',
    author_email='ethcalibur+pip@gmail.com',
    url='https://github.com/ethereum/py-ssz',
    include_package_data=True,
    install_requires=[
        "eth-utils>=1,<2",
        "eth-hash[pycryptodome]",
        "mypy-extensions>=0.4.1,<1.0.0",
    ],
    setup_requires=['setuptools-markdown'],
    python_requires='>=3.6, <4',
    extras_require=extras_require,
    py_modules=['ssz'],
    license="MIT",
    zip_safe=False,
    keywords='ethereum',
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)

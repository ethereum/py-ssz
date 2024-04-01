Release Notes
=============

.. towncrier release notes start

py-ssz v0.5.0 (2024-04-01)
--------------------------

Internal Changes - for py-ssz Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Add ``python 3.12`` support, add all doc type tests and night runs to CI, add blocklint to linting, turned off ``yaml`` tests in CI (`#136 <https://github.com/ethereum/py-ssz/issues/136>`__)


py-ssz v0.4.0 (2023-12-07)
--------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

- Drop support for python 3.7 (`#134 <https://github.com/ethereum/py-ssz/issues/134>`__)


Internal Changes - for py-ssz Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Add ``build.os`` config to readthedocs.yml (`#133 <https://github.com/ethereum/py-ssz/issues/133>`__)
- Merge changes from the template, including use ``pre-commit`` for linting and change the name of the ``master`` branch to ``main`` (`#134 <https://github.com/ethereum/py-ssz/issues/134>`__)


py-ssz v0.3.1 (2023-06-08)
--------------------------

Internal Changes - for py-ssz Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- pull in most project template updates (`#128 <https://github.com/ethereum/py-ssz/issues/128>`__)
- bump eth-utils requirement version to >=2 (`#132 <https://github.com/ethereum/py-ssz/issues/132>`__)


py-ssz v0.3.0 (2022-08-19)
--------------------------

Breaking changes
~~~~~~~~~~~~~~~~

- Dropping official support for Python 3.6 (although it still worked as of the last test run). (`#125 <https://github.com/ethereum/py-ssz/issues/125>`__)


Features
~~~~~~~~

- Add a :class:`~ssz.sedes.byte_list.ByteList` sedes that is more convenient and more performant. With
  ByteList, the caller can decode a :class:`bytes` object, rather than passing in a list of
  single-byte elements. (`#118 <https://github.com/ethereum/py-ssz/issues/118>`__)


Bugfixes
~~~~~~~~

- Reject empty bytes at the end of a bitlist as invalid (`#109 <https://github.com/ethereum/py-ssz/issues/109>`__)
- Reject vectors and bitvectors of length 0 as invalid, as defined in the spec. (`#111 <https://github.com/ethereum/py-ssz/issues/111>`__)
- Enforce that vector types must have a maximum length of 1 or more, and lists may have a 0 max length (`#116 <https://github.com/ethereum/py-ssz/issues/116>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Sort release notes with most recent on top (`#124 <https://github.com/ethereum/py-ssz/issues/124>`__)


Internal Changes - for py-ssz Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Upgrade black to a stable version, and pass newest style checks (`#120 <https://github.com/ethereum/py-ssz/issues/120>`__)
- Use the latest project template, which gives many developer-focused benefits: in making release
  notes, releasing new versions, etc. (`#121 <https://github.com/ethereum/py-ssz/issues/121>`__)
- Miscellaneous changes (`#124 <https://github.com/ethereum/py-ssz/issues/124>`__):

  - Run black autoformat, as part of ``make lint-roll``
  - Added some tests to check length validation of :class:`~ssz.sedes.byte_list.ByteList` and :class:`~ssz.sedes.byte_vector.ByteVector`
  - When generating website docs from docstrings, skip tests


v0.2.4
--------------

Released 2020-03-24

- Update `pyrsistent` dependency.


v0.1.0-alpha.8
--------------

Released 2018-05-05

- Less strict class relationship requirement for equality of serializables -
  `#71 <https://github.com/ethereum/py-ssz/pull/71>`_


v0.1.0-alpha.7
--------------

Released 2018-05-02

- Fix equality of serializable objects - `#64 <https://github.com/ethereum/py-ssz/pull/64>`_
- Add helpers to convert objects to and from a human readable representation -
  `#66 <https://github.com/ethereum/py-ssz/pull/66>`_
- Cache hash tree root of serializable objects - `#68 <https://github.com/ethereum/py-ssz/pull/68>`_


v0.1.0-alpha.6
--------------

Released 2018-04-23

No changes


v0.1.0-alpha.5
--------------

Released 2018-04-23

- Slight change in serializable inheritance rules -
  `#57 <https://github.com/ethereum/py-ssz/pull/57>`_
- Add root property to serializable - `#57 <https://github.com/ethereum/py-ssz/pull/57>`_
- Add SignedSerializable base class with signing-root property -
  `#57 <https://github.com/ethereum/py-ssz/pull/57>`_


v0.1.0-alpha.4
--------------

Released 2018-04-09

- Fix bug in serializable class - `#56 <https://github.com/ethereum/py-ssz/pull/56>`_


v0.1.0-alpha.3
--------------

Released 2018-04-04

- Implement spec version 0.5.0


v0.1.0-alpha.2
--------------

Released 2018-02-05

- Add zero padding to tree hash - `#35 <https://github.com/ethereum/py-ssz/pull/35>`_


v0.1.0-alpha.1
--------------

Released 2018-02-05

- Implements January pre-release spec


v0.1.0-alpha.0
--------------

- Launched repository, claimed names for pip, RTD, github, etc

from abc import ABC, ABCMeta
from typing import Any, Dict, NamedTuple, Optional, Tuple, Type, TypeVar, Union

from eth_typing import Hash32
from eth_utils import ValidationError
from eth_utils.toolz import assoc

from ssz.constants import FIELDS_META_ATTR
from ssz.hashable_structure import BaseHashableStructure, HashableStructureEvolver
from ssz.sedes.base import BaseSedes
from ssz.sedes.container import Container

TStructure = TypeVar("TStructure", bound="HashableContainer")
TElement = TypeVar("TElement")


class Meta(NamedTuple):
    fields: Optional[Tuple[Tuple[str, BaseSedes], ...]]
    field_names_to_element_indices: Optional[Dict[str, int]]
    container_sedes: Optional[Container]


class MetaHashableContainer(ABCMeta):
    _meta: Meta

    def __new__(mcls, name: str, bases: Tuple[Type, ...], namespace: Dict[str, Any]):
        declares_fields = FIELDS_META_ATTR in namespace

        if declares_fields:
            fields = namespace.pop(FIELDS_META_ATTR)
            field_sedes = tuple(sedes for field_name, sedes in fields)
            try:
                container_sedes = Container(field_sedes)
            except ValidationError as exception:
                # catch empty fields and reraise as a TypeError as this would be an invalid class
                # definition
                raise TypeError(str(exception)) from exception

        else:
            container_bases = tuple(
                base for base in bases if isinstance(base, MetaHashableContainer)
            )
            bases_with_fields = tuple(
                base for base in container_bases if base._meta.fields is not None
            )

            if len(bases_with_fields) == 0:
                fields = None
                container_sedes = None
            elif len(bases_with_fields) == 1:
                fields = bases_with_fields[0]._meta.fields
                container_sedes = bases_with_fields[0]._meta.container_sedes
            else:
                raise TypeError(
                    "Fields need to be declared explicitly as class has multiple "
                    "HashableContainer parents with fields themselves"
                )

        if fields is None:
            # create the class without any fields if neither the class itself nor any of its
            # ancestors have defined fields
            meta = Meta(
                fields=None, field_names_to_element_indices=None, container_sedes=None
            )
        else:
            field_names, _ = zip(*fields)
            field_names_to_element_indices = {
                field_name: index for index, field_name in enumerate(field_names)
            }
            meta = Meta(
                fields=fields,
                field_names_to_element_indices=field_names_to_element_indices,
                container_sedes=container_sedes,
            )

        return super().__new__(mcls, name, bases, assoc(namespace, "_meta", meta))


class HashableContainer(
    BaseHashableStructure[TElement], ABC, metaclass=MetaHashableContainer
):
    @classmethod
    def create(cls, **fields: Dict[str, Any]):
        if (
            cls._meta.fields is None
            or cls._meta.field_names_to_element_indices is None
            or cls._meta.container_sedes is None
        ):
            raise TypeError("HashableContainer does not define any fields")

        given_keys = set(fields.keys())
        expected_keys = set(cls._meta.field_names_to_element_indices.keys())
        missing_keys = expected_keys - given_keys
        unexpected_keys = given_keys - missing_keys

        if missing_keys:
            raise ValueError(
                f"The following keyword arguments are missing: {', '.join(sorted(missing_keys))}"
            )
        if unexpected_keys:
            raise ValueError(
                f"The following keyword arguments are unexpected: "
                f"{', '.join(sorted(unexpected_keys))}"
            )

        return cls.from_iterable_and_sedes(
            (fields[field_name] for field_name, _ in cls._meta.fields),
            sedes=cls._meta.container_sedes,
            max_length=None,
        )

    @property
    def root(self) -> Hash32:
        return self.raw_root

    def __getattr__(self, name: str) -> TElement:
        try:
            element_index = self._meta.field_names_to_element_indices[name]
        except KeyError:
            raise AttributeError("HashableContainer has no attribute {name}")
        return self[element_index]

    def __getitem__(self, index: Union[str, int]) -> TElement:
        if isinstance(index, str):
            element_index = self._meta.field_names_to_element_indices[index]
        else:
            element_index = index
        return super().__getitem__(element_index)

    def evolver(self: TStructure) -> "HashableContainerEvolver[TStructure, TElement]":
        return HashableContainerEvolver(self)


class HashableContainerEvolver(HashableStructureEvolver[TStructure, TElement]):
    def __setattr__(self, name: str, value: TElement) -> None:
        meta = self._original_structure._meta
        try:
            element_index = meta.field_names_to_element_indices[name]
        except KeyError:
            super().__setattr__(name, value)
        else:
            self[element_index] = value

    def __getattr__(self, name: str) -> TElement:
        meta = self._original_structure._meta
        try:
            element_index = meta.field_names_to_element_indices[name]
        except KeyError:
            raise AttributeError("HashableContainer has no attribute {name}")
        return self[element_index]

    def __getitem__(self, index: Union[str, int]) -> TElement:
        if isinstance(index, str):
            element_index = self._meta.field_names_to_element_indices[index]
        else:
            element_index = index
        return super().__getitem__(element_index)

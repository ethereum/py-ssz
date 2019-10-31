from abc import ABC, ABCMeta
from typing import Any, Dict, NamedTuple, Optional, Tuple, Type, TypeVar, Union

from eth_typing import Hash32
from eth_utils.toolz import merge

from ssz.constants import FIELDS_META_ATTR
from ssz.hashable_structure import BaseHashableStructure, HashableStructureEvolver
from ssz.sedes.base import BaseSedes
from ssz.sedes.container import Container

TStructure = TypeVar("TStructure", bound="HashableContainer")
TElement = TypeVar("TElement")


class Meta(NamedTuple):
    fields: Tuple[Tuple[str, BaseSedes], ...]
    field_names_to_element_indices: Dict[str, int]
    container_sedes: Container
    evolver_class: Type["HashableContainerEvolver"]


#
# Descriptors to translate from attribute access (`hashable_container.field_name`) to item access
# (`hashable_container["field_name"]`)
#
class FieldDescriptor:
    def __init__(self, name: str) -> None:
        self.name = name

    def __get__(
        self, instance: "HashableContainer", owner: Type["HashableContainer"] = None
    ) -> Any:
        return instance[self.name]


class SettableFieldDescriptor(FieldDescriptor):
    def __set__(self, instance: "HashableContainerEvolver", value: Any) -> None:
        instance[self.name] = value


#
# Metaclass which creates HashableContainers
#
class MetaHashableContainer(ABCMeta):
    def __new__(mcls, name: str, bases: Tuple[Type, ...], namespace: Dict[str, Any]):
        container_sedes: Optional[Container]

        declares_fields = FIELDS_META_ATTR in namespace

        if declares_fields:
            fields = namespace.pop(FIELDS_META_ATTR)
            field_sedes = tuple(sedes for field_name, sedes in fields)
            if not fields:
                raise TypeError(
                    "HashableContainer must refrain from defining fields at all or define at least "
                    "one, but not define zero"
                )
            container_sedes = Container(field_sedes)

        else:
            container_bases = tuple(
                base for base in bases if isinstance(base, MetaHashableContainer)
            )
            bases_with_fields = tuple(
                base for base in container_bases if base._meta is not None
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
            # create the class without specifying any fields as neither the class itself nor any of
            # its ancestors have defined fields
            field_descriptors: Dict[str, FieldDescriptor] = {}
            meta = None
        else:
            field_names, _ = zip(*fields)
            field_names_to_element_indices = {
                field_name: index for index, field_name in enumerate(field_names)
            }

            field_descriptors = {
                field_name: FieldDescriptor(field_name) for field_name in field_names
            }
            settable_field_descriptors = {
                field_name: SettableFieldDescriptor(field_name)
                for field_name in field_names
            }

            evolver_class = type(
                name + "Evolver",
                (HashableContainerEvolver,),
                settable_field_descriptors,
            )

            meta = Meta(
                fields=fields,
                field_names_to_element_indices=field_names_to_element_indices,
                container_sedes=container_sedes,
                evolver_class=evolver_class,
            )
            field_descriptors = {
                field_name: FieldDescriptor(field_name) for field_name in field_names
            }

        namespace_with_meta_and_fields = merge(
            namespace, {"_meta": meta}, field_descriptors
        )
        return super().__new__(mcls, name, bases, namespace_with_meta_and_fields)


#
# The base class for hashable containers
#
class HashableContainer(
    BaseHashableStructure[TElement], ABC, metaclass=MetaHashableContainer
):
    _meta: Meta  # set by MetaHashableContainer

    def __init__(self, *args, **kwargs):
        if self._meta is None:
            raise TypeError("HashableContainer does not define any fields")
        else:
            super().__init__(*args, **kwargs)

    @classmethod
    def create(cls, **fields: Dict[str, Any]):
        if cls._meta is None:
            raise TypeError("HashableContainer does not define any fields")

        given_keys = set(fields.keys())
        expected_keys = set(cls._meta.field_names_to_element_indices.keys())
        missing_keys = expected_keys - given_keys
        unexpected_keys = given_keys - expected_keys

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

    def normalize_item_index(self, index: Union[str, int]) -> int:
        if isinstance(index, str):
            return self._meta.field_names_to_element_indices[index]
        elif isinstance(index, int):
            return index
        else:
            raise TypeError("Index must be either int or str")

    def __getitem__(self, index: Union[str, int]) -> TElement:
        element_index = self.normalize_item_index(index)
        return super().__getitem__(element_index)

    def evolver(self: TStructure) -> "HashableContainerEvolver[TStructure, TElement]":
        return self._meta.evolver_class(self)


#
# Base class for evolvers for the hashable container (MetaHashableContainer subclasses this
# dynamically)
#
class HashableContainerEvolver(HashableStructureEvolver[TStructure, TElement]):
    def __setitem__(self, index: Union[str, int], value: TElement) -> None:
        element_index = self._original_structure.normalize_item_index(index)
        super().__setitem__(element_index, value)

    def __getitem__(self, index: Union[str, int]) -> TElement:
        element_index = self._original_structure.normalize_item_index(index)
        return super().__getitem__(element_index)

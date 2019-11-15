from abc import ABCMeta
import sys
from typing import (
    Any,
    Dict,
    Generator,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from eth_typing import Hash32
from eth_utils import to_tuple
from eth_utils.toolz import merge

from ssz.constants import FIELDS_META_ATTR, SIGNATURE_FIELD_NAME
from ssz.hashable_structure import BaseHashableStructure, HashableStructureEvolver
from ssz.sedes.base import BaseSedes
from ssz.sedes.container import Container

TStructure = TypeVar("TStructure", bound="HashableContainer")
TElement = TypeVar("TElement")


class FieldDescriptor:
    """Descriptor translating from __getattr__ to __getitem__ calls for a given attribute."""

    def __init__(self, name: str) -> None:
        self.name = name

    def __get__(
        self, instance: "HashableContainer", owner: Type["HashableContainer"] = None
    ) -> Any:
        return instance[self.name]


class SettableFieldDescriptor(FieldDescriptor):
    """Settable variant of FieldDescriptor for evolver."""

    def __set__(self, instance: "HashableContainerEvolver", value: Any) -> None:
        instance[self.name] = value


Field = Tuple[str, Union[BaseSedes, "HashableContainer"]]


class Meta(NamedTuple):
    fields: Tuple[Field, ...]
    field_names_to_element_indices: Dict[str, int]
    field_descriptors: Dict[str, FieldDescriptor]
    container_sedes: Container
    evolver_class: Type["HashableContainerEvolver"]

    @classmethod
    def from_fields(
        cls, fields: Tuple[Tuple[str, BaseSedes], ...], container: Container, name: str
    ) -> "Meta":
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

        # create subclass of HashableEvolver that has a settable descriptor for each field
        evolver_class = type(
            name + "Evolver", (HashableContainerEvolver,), settable_field_descriptors
        )

        return cls(
            fields=fields,
            field_names_to_element_indices=field_names_to_element_indices,
            field_descriptors=field_descriptors,
            container_sedes=container,
            evolver_class=evolver_class,
        )


class MetaSigned(NamedTuple):
    fields: Tuple[Field, ...]
    field_names_to_element_indices: Dict[str, int]
    field_descriptors: Dict[str, FieldDescriptor]
    container_sedes: Container
    signing_container_sedes: Container
    evolver_class: Type["HashableContainerEvolver"]

    @classmethod
    def from_meta(cls, meta: Meta, signing_container: Container) -> "MetaSigned":
        return cls(
            fields=meta.fields,
            field_names_to_element_indices=meta.field_names_to_element_indices,
            field_descriptors=meta.field_descriptors,
            container_sedes=meta.container_sedes,
            signing_container_sedes=signing_container,
            evolver_class=meta.evolver_class,
        )


def get_meta_from_bases(bases: Tuple[Type, ...]) -> Optional[Meta]:
    """Return the meta object defined by one of the given base classes.

    Returns None if no base defines a meta object. Raises a TypeError if more than one do.
    """
    container_bases = tuple(
        base for base in bases if isinstance(base, MetaHashableContainer)
    )
    bases_with_meta = tuple(base for base in container_bases if base._meta is not None)

    if len(bases_with_meta) == 0:
        return None
    elif len(bases_with_meta) == 1:
        return bases_with_meta[0]._meta
    else:
        raise TypeError(
            "Fields need to be declared explicitly as class has multiple "
            "HashableContainer parents with fields themselves"
        )


@to_tuple
def get_field_sedes_from_fields(
    fields: Sequence[Field]
) -> Generator[BaseSedes, None, None]:
    for _, field in fields:
        if isinstance(field, BaseSedes):
            yield field
        elif issubclass(field, HashableContainer):
            yield field._meta.container_sedes
        else:
            raise TypeError(
                f"Field must either be a sedes object or a hashable container, got {field}"
            )


class MetaHashableContainer(ABCMeta):
    """Metaclass which creates HashableContainers."""

    def __new__(mcls, name: str, bases: Tuple[Type, ...], namespace: Dict[str, Any]):
        container_sedes: Optional[Container]

        # get fields defined in the class or by one of its bases
        if FIELDS_META_ATTR in namespace:
            fields = namespace.pop(FIELDS_META_ATTR)
            field_sedes = get_field_sedes_from_fields(fields)
            if not fields:
                raise TypeError(
                    "HashableContainer must either define a non-zero number of fields or not "
                    "define any, but not an empty set."
                )
            container_sedes = Container(field_sedes)
        else:
            meta = get_meta_from_bases(bases)
            if meta is not None:
                fields = meta.fields
                field_sedes = get_field_sedes_from_fields(fields)
                container_sedes = Container(field_sedes)
            else:
                fields = None
                container_sedes = None

        if fields is not None:
            assert container_sedes is not None
            meta = Meta.from_fields(fields, container_sedes, name=name)
        else:
            meta = None

        namespace_with_meta_and_fields = merge(
            namespace, {"_meta": meta}, meta.field_descriptors if meta else {}
        )
        return super().__new__(mcls, name, bases, namespace_with_meta_and_fields)


class MetaSignedHashableContainer(MetaHashableContainer):
    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)

        # check that the signature conventions are abided by
        if cls._meta is not None:
            if len(cls._meta.field_names) < 2:
                raise TypeError(f"Signed containers need to have at least two fields")
            if cls._meta.field_names[-1] != SIGNATURE_FIELD_NAME:
                raise TypeError(
                    f"Last field of signed container must be {SIGNATURE_FIELD_NAME}, but is "
                    f"{cls._meta.field_names[-1]}"
                )

            signing_field_sedes = tuple(sedes for field_name, sedes in cls._meta.fields)
            signing_container = Container(signing_field_sedes)
            cls._meta = MetaSigned.from_meta(cls._meta, signing_container)

        return cls


# workaround for https://github.com/python/typing/issues/449 (fixed in python 3.7)
python_version_info = sys.version_info
if python_version_info[0] <= 3 and python_version_info[1] <= 6:
    from typing import GenericMeta

    class GenericMetaHashableContainer(GenericMeta, MetaHashableContainer):
        pass

    class GenericMetaSignedHashableContainer(GenericMeta, MetaSignedHashableContainer):
        pass


else:
    GenericMetaHashableContainer = MetaHashableContainer  # type: ignore
    GenericMetaSignedHashableContainer = MetaSignedHashableContainer  # type: ignore


class HashableContainer(
    BaseHashableStructure[TElement], metaclass=GenericMetaHashableContainer
):
    """Base class for hashable containers."""

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


class HashableContainerEvolver(HashableStructureEvolver[TStructure, TElement]):
    """Base class for evolvers for hashable containers.

    Subclasses (created dynamically by MetaHashableContainer when creating the corresponding
    HashableContainer) should add settable field descriptors for all fields.
    """

    def __setitem__(self, index: Union[str, int], value: TElement) -> None:
        element_index = self._original_structure.normalize_item_index(index)
        super().__setitem__(element_index, value)

    def __getitem__(self, index: Union[str, int]) -> TElement:
        element_index = self._original_structure.normalize_item_index(index)
        return super().__getitem__(element_index)


class SignedHashableContainer(
    HashableContainer[TElement], metaclass=GenericMetaSignedHashableContainer
):
    _meta: MetaSigned

    @property
    def signing_root(self) -> Hash32:
        return self._meta.signing_container_sedes.get_hash_tree_root(self)

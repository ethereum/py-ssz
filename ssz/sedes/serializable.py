import abc
import collections
import copy
from itertools import (
    dropwhile,
    takewhile,
)
from typing import (
    NamedTuple,
    Optional,
    Tuple,
    Type,
    TypeVar,
)

from eth_utils import (
    ValidationError,
    to_dict,
    to_tuple,
)
from eth_utils.toolz import (
    assoc,
)

import ssz
from ssz.sedes.base import (
    BaseSedes,
)
from ssz.sedes.container import (
    Container,
)
from ssz.utils import (
    get_duplicates,
)

TSerializable = TypeVar("TSerializable", bound="BaseSerializable")


class Field(abc.ABC):

    def __init__(self, sedes):
        self.sedes = sedes
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name
        if hasattr(owner, name):
            raise TypeError(f"Tried to define field with name {name} twice")

    def __get__(self, instance, owner):
        try:
            return instance.__dict__[self.name]
        except KeyError:
            raise AttributeError("Field has not been set")

    def __set__(self, instance, value):
        if self.name in instance.__dict__:
            raise AttributeError("Field can only be set once")
        else:
            instance.__dict__[self.name] = value


class Meta(NamedTuple):
    has_fields: bool
    fields: Optional[Tuple[Field]]
    container_sedes: Optional[Container]


def validate_args_and_kwargs(args, kwargs, arg_names):
    duplicate_arg_names = get_duplicates(arg_names)
    if duplicate_arg_names:
        raise ValueError("Duplicate argument names: {0}".format(sorted(duplicate_arg_names)))

    needed_arg_names = set(arg_names[len(args):])
    used_arg_names = set(arg_names[:len(args)])

    duplicate_arg_names = used_arg_names.intersection(kwargs.keys())
    if duplicate_arg_names:
        raise TypeError("Duplicate kwargs: {0}".format(sorted(duplicate_arg_names)))

    unknown_arg_names = set(kwargs.keys()).difference(arg_names)
    if unknown_arg_names:
        raise TypeError("Unknown kwargs: {0}".format(sorted(unknown_arg_names)))

    missing_arg_names = set(needed_arg_names).difference(kwargs.keys())
    if missing_arg_names:
        raise TypeError("Missing kwargs: {0}".format(sorted(missing_arg_names)))


@to_tuple
def merge_kwargs_to_args(args, kwargs, arg_names):
    validate_args_and_kwargs(args, kwargs, arg_names)

    needed_arg_names = arg_names[len(args):]

    yield from args
    for arg_name in needed_arg_names:
        yield kwargs[arg_name]


@to_dict
def merge_args_to_kwargs(args, kwargs, arg_names):
    yield from kwargs.items()
    for value, name in zip(args, arg_names):
        yield name, value


class BaseSerializable(collections.Sequence):
    _cached_ssz = None

    def __init__(self, *args, **kwargs):
        arg_names = tuple(field.name for field in self._meta.fields) if self._meta.fields else ()
        validate_args_and_kwargs(args, kwargs, arg_names)
        field_values = merge_kwargs_to_args(args, kwargs, arg_names)

        # Ensure that all the fields have been given values in initialization
        if len(field_values) != len(arg_names):
            raise TypeError(
                'Argument count mismatch. expected {0} - got {1} - missing {2}'.format(
                    len(arg_names),
                    len(field_values),
                    ','.join(arg_names[len(field_values):]),
                )
            )

        for value, attr in zip(field_values, arg_names):
            setattr(self, attr, make_immutable(value))

    def as_dict(self):
        return {
            field.name: getattr(self, field.name)
            for field in self._meta.fields
        }

    def __iter__(self):
        for field in self._meta.fields:
            yield getattr(self, field.name)

    def __getitem__(self, index):
        if isinstance(index, int):
            return getattr(self, self._meta.fields[index].name)
        elif isinstance(index, slice):
            field_name_slice = tuple(field.name for field in self._meta.fields[index])
            return tuple(getattr(self, field_name) for field_name in field_name_slice)
        elif isinstance(index, str):
            if index not in set(field.name for field in self._meta.fields):
                raise KeyError(f"Field {index} does not exist")
            else:
                return getattr(self, index)
        else:
            raise IndexError("Unsupported type for __getitem__: {0}".format(type(index)))

    def __len__(self):
        return len(self._meta.fields)

    def __eq__(self, other):
        satisfies_class_relationship = (
            issubclass(self.__class__, other.__class__) or
            issubclass(other.__class__, self.__class__)
        )

        if not satisfies_class_relationship:
            return False
        else:
            return self.root == other.root

    def __getstate__(self):
        state = self.__dict__.copy()
        # The hash() builtin is not stable across processes
        # (https://docs.python.org/3/reference/datamodel.html#object.__hash__), so we do this here
        # to ensure pickled instances don't carry the cached hash() as that may cause issues like
        # https://github.com/ethereum/py-evm/issues/1318
        state['_hash_cache'] = None
        return state

    _hash_cache = None

    def __hash__(self):
        if self._hash_cache is None:
            self._hash_cache = hash(self.__class__) * int.from_bytes(self.root, "little")
        return self._hash_cache

    def copy(self, *args, **kwargs):
        field_names = tuple(field.name for field in self._meta.fields)
        missing_overrides = set(
            field_names
        ).difference(
            kwargs.keys()
        ).difference(
            field_names[:len(args)]
        )
        unchanged_kwargs = {
            key: copy.deepcopy(value)
            for key, value
            in self.as_dict().items()
            if key in missing_overrides
        }
        combined_kwargs = dict(**unchanged_kwargs, **kwargs)
        all_kwargs = merge_args_to_kwargs(args, combined_kwargs, field_names)
        return type(self)(**all_kwargs)

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self, *args):
        return self.copy()

    _root_cache = None

    @property
    def root(self):
        if self._root_cache is None:
            self._root_cache = ssz.hash_tree_root(self)
        return self._root_cache


def make_immutable(value):
    if isinstance(value, list):
        return tuple(make_immutable(item) for item in value)
    else:
        return value


def validate_fields_in_namespace(namespace):
    def is_no_field(namespace_item):
        return isinstance(namespace_item[1], Field)

    namespace_items = tuple(namespace.items())
    pre_field_item_num = len(tuple(dropwhile(is_no_field, namespace_items)))
    post_field_item_num = len(tuple(takewhile(is_no_field, reversed(namespace_items))))
    field_items = namespace_items[pre_field_item_num:-post_field_item_num]

    non_field_items_between_fields = tuple(item for item in field_items if is_no_field(item))
    if non_field_items_between_fields:
        raise TypeError(
            f"SSZ fields are not defined consecutively. The following attributes appear in "
            f"between: {', '.join(non_field_items_between_fields.keys())}"
        )


class MetaSerializable(abc.ABCMeta):
    def __new__(mcls, name, bases, namespace):
        validate_fields_in_namespace(namespace)
        fields = tuple(element for element in namespace.values() if isinstance(element, Field))

        if len(fields) > 0:
            has_fields = True
            field_sedes = tuple(field.sedes for field in fields)
            try:
                sedes = Container(field_sedes)
            except ValidationError as exception:
                # catch empty or duplicate fields and reraise as a TypeError as this would be an
                # invalid class definition
                raise TypeError(str(exception)) from exception

        else:
            serializable_bases = tuple(base for base in bases if isinstance(base, MetaSerializable))
            bases_with_fields = tuple(base for base in serializable_bases if base._meta.has_fields)

            if len(bases_with_fields) == 0:
                has_fields = False
                fields = None
                sedes = None
            elif len(bases_with_fields) == 1:
                has_fields = True
                fields = bases_with_fields[0]._meta.fields
                sedes = bases_with_fields[0]._meta.container_sedes
            else:
                raise TypeError(
                    "Fields need to be declared explicitly as class has multiple `Serializable` "
                    "parents with fields themselves"
                )

        # create the class without any fields as neither the class itself nor any of its ancestors
        # have defined fields
        if not has_fields:
            meta = Meta(
                has_fields=False,
                fields=None,
                container_sedes=None,
            )
            return super().__new__(
                mcls,
                name,
                bases,
                assoc(namespace, "_meta", meta),
            )

        # from here on, we can assume that we've got fields and a sedes object
        if sedes is None:
            raise Exception("Invariant: sedes has been initialized earlier")
        if len(fields) == 0:
            raise Exception("Invariant: number of fields has been checked at initializion of sedes")

        # construct the Meta object to store field information for the class
        meta = Meta(
            has_fields=True,
            fields=fields,
            container_sedes=sedes,
        )
        return super().__new__(
            mcls,
            name,
            bases,
            assoc(namespace, "_meta", meta)
        )

    #
    # Implement BaseSedes methods as pass-throughs to the container sedes
    #
    def serialize(cls: Type[TSerializable], value: TSerializable) -> bytes:
        return cls._meta.container_sedes.serialize(value)

    def deserialize(cls: Type[TSerializable], data: bytes) -> TSerializable:
        deserialized_fields = cls._meta.container_sedes.deserialize(data)
        field_names = tuple(field.name for field in cls._meta.fields)
        deserialized_field_dict = dict(zip(field_names, deserialized_fields))
        return cls(**deserialized_field_dict)

    def hash_tree_root(cls: Type[TSerializable], value: TSerializable) -> bytes:
        return cls._meta.container_sedes.hash_tree_root(value)

    @property
    def is_fixed_sized(cls):
        return cls._meta.container_sedes.is_fixed_sized

    def get_fixed_size(cls):
        return cls._meta.container_sedes.get_fixed_size()


# Make any class created with MetaSerializable an instance of BaseSedes
BaseSedes.register(MetaSerializable)


class Serializable(BaseSerializable, metaclass=MetaSerializable):
    """
    The base class for serializable objects.
    """
    def __str__(self) -> str:
        return f"[{', '.join((str(v) for v in self))}]"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {str(self)}>"

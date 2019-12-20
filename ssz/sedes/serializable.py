import abc
import collections.abc
import copy
import operator
import re
from typing import NamedTuple, Optional, Sequence, Tuple, Type

from eth_utils import ValidationError, to_dict, to_set, to_tuple
from eth_utils.toolz import assoc, merge
from lru import LRU

from ssz.cache.cache import DEFAULT_CACHE_SIZE
from ssz.cache.utils import get_base_key
from ssz.constants import FIELDS_META_ATTR
from ssz.sedes.base import BaseSedes
from ssz.sedes.container import Container
from ssz.typing import TSerializable
from ssz.utils import get_duplicates, is_immutable_field_value


class Meta(NamedTuple):
    has_fields: bool
    fields: Optional[Tuple[Tuple[str, BaseSedes], ...]]
    container_sedes: Optional[Container]
    field_names: Optional[Tuple[str, ...]]
    field_attrs: Optional[Tuple[str, ...]]


def validate_args_and_kwargs(args, kwargs, arg_names):
    duplicate_arg_names = get_duplicates(arg_names)
    if duplicate_arg_names:
        raise ValueError(
            "Duplicate argument names: {0}".format(sorted(duplicate_arg_names))
        )

    needed_arg_names = set(arg_names[len(args) :])
    used_arg_names = set(arg_names[: len(args)])

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

    needed_arg_names = arg_names[len(args) :]

    yield from args
    for arg_name in needed_arg_names:
        yield kwargs[arg_name]


@to_dict
def merge_args_to_kwargs(args, kwargs, arg_names):
    yield from kwargs.items()
    for value, name in zip(args, arg_names):
        yield name, value


class BaseSerializable(collections.abc.Sequence):
    cache = None

    def __init__(self, *args, cache=None, **kwargs):
        arg_names = self._meta.field_names or ()
        validate_args_and_kwargs(args, kwargs, arg_names)
        field_values = merge_kwargs_to_args(args, kwargs, arg_names)

        # Ensure that all the fields have been given values in initialization
        if len(field_values) != len(arg_names):
            raise TypeError(
                "Argument count mismatch. expected {0} - got {1} - missing {2}".format(
                    len(arg_names),
                    len(field_values),
                    ",".join(arg_names[len(field_values) :]),
                )
            )

        for value, attr in zip(field_values, self._meta.field_attrs or ()):
            setattr(self, attr, make_immutable(value))

        self.cache = LRU(DEFAULT_CACHE_SIZE) if cache is None else cache

    def as_dict(self):
        return dict(
            (field, value) for field, value in zip(self._meta.field_names, self)
        )

    def __iter__(self):
        for attr in self._meta.field_attrs:
            yield getattr(self, attr)

    def __getitem__(self, index):
        if isinstance(index, int):
            attr = self._meta.field_attrs[index]
            return getattr(self, attr)
        elif isinstance(index, slice):
            field_slice = self._meta.field_attrs[index]
            return tuple(getattr(self, field) for field in field_slice)
        elif isinstance(index, str):
            return getattr(self, index)
        else:
            raise IndexError(
                "Unsupported type for __getitem__: {0}".format(type(index))
            )

    def __len__(self):
        return len(self._meta.fields)

    def __eq__(self, other):
        satisfies_class_relationship = issubclass(
            self.__class__, other.__class__
        ) or issubclass(other.__class__, self.__class__)

        if not satisfies_class_relationship:
            return False
        else:
            return self.hash_tree_root == other.hash_tree_root

    def __getstate__(self):
        state = self.__dict__.copy()
        # The hash() builtin is not stable across processes
        # (https://docs.python.org/3/reference/datamodel.html#object.__hash__), so we do this here
        # to ensure pickled instances don't carry the cached hash() as that may cause issues like
        # https://github.com/ethereum/py-evm/issues/1318
        state["_hash_cache"] = None
        return state

    _hash_cache = None

    def __hash__(self):
        if self._hash_cache is None:
            self._hash_cache = hash(self.__class__) * int.from_bytes(
                self.hash_tree_root, "little"
            )
        return self._hash_cache

    def copy(self, *args, **kwargs):
        missing_overrides = (
            set(self._meta.field_names)
            .difference(kwargs.keys())
            .difference(self._meta.field_names[: len(args)])
        )
        unchanged_kwargs = {
            key: value if is_immutable_field_value(value) else copy.deepcopy(value)
            for key, value in self.as_dict().items()
            if key in missing_overrides
        }

        combined_kwargs = dict(**unchanged_kwargs, **kwargs)
        all_kwargs = merge_args_to_kwargs(args, combined_kwargs, self._meta.field_names)

        result = type(self)(**all_kwargs)
        result.cache = self.cache

        return result

    def reset_cache(self):
        self.cache.clear()
        self._fixed_size_section_length_cache = None
        self._serialize_cache = None

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self, memodict=None):
        if memodict is None:
            memodict = {}

        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result

        for k, v in self.__dict__.items():
            if k != "cache":
                setattr(result, k, copy.deepcopy(v, memodict))

        result.cache = self.cache
        result._fixed_size_section_length_cache = self._fixed_size_section_length_cache

        return result

    _fixed_size_section_length_cache = None
    _serialize_cache = None

    @property
    def hash_tree_root(self):
        return self.__class__.get_hash_tree_root(self, cache=True)

    @classmethod
    def get_sedes_id(cls) -> str:
        # Serializable implementation name should be unique
        return cls.__name__

    def get_key(self) -> bytes:
        # Serilaize with self._meta.container_sedes
        key = get_base_key(self._meta.container_sedes, self).hex()

        if len(key) == 0:
            key = ""

        return f"{self.__class__.get_sedes_id()}{key}"


def make_immutable(value):
    if isinstance(value, list):
        return tuple(make_immutable(item) for item in value)
    else:
        return value


@to_tuple
def _mk_field_attrs(field_names, extra_namespace):
    namespace = set(field_names).union(extra_namespace)
    for field in field_names:
        while True:
            field = "_" + field
            if field not in namespace:
                namespace.add(field)
                yield field
                break


@to_dict
def _mk_field_props(field_names, field_attrs):
    for field, attr in zip(field_names, field_attrs):
        getter = operator.attrgetter(attr)
        yield field, property(getter)


def _validate_field_names(field_names: Sequence[str]) -> None:
    # check that field names are unique
    duplicate_field_names = get_duplicates(field_names)
    if duplicate_field_names:
        raise TypeError(
            "The following fields are duplicated in the `fields` "
            "declaration: "
            "{0}".format(",".join(sorted(duplicate_field_names)))
        )

    # check that field names are valid identifiers
    invalid_field_names = {
        field_name for field_name in field_names if not _is_valid_identifier(field_name)
    }
    if invalid_field_names:
        raise TypeError(
            "The following field names are not valid python identifiers: {0}".format(
                ",".join("`{0}`".format(item) for item in sorted(invalid_field_names))
            )
        )


IDENTIFIER_REGEX = re.compile(r"^[^\d\W]\w*\Z", re.UNICODE)


def _is_valid_identifier(value):
    # Source: https://stackoverflow.com/questions/5474008/regular-expression-to-confirm-whether-a-string-is-a-valid-identifier-in-python  # noqa: E501
    if not isinstance(value, str):
        return False
    return bool(IDENTIFIER_REGEX.match(value))


@to_set
def _get_class_namespace(cls):
    if hasattr(cls, "__dict__"):
        yield from cls.__dict__.keys()
    if hasattr(cls, "__slots__"):
        yield from cls.__slots__


class MetaSerializable(abc.ABCMeta):
    def __new__(mcls, name, bases, namespace):
        declares_fields = FIELDS_META_ATTR in namespace

        if declares_fields:
            has_fields = True
            fields = namespace.pop(FIELDS_META_ATTR)
            field_sedes = tuple(sedes for field_name, sedes in fields)
            try:
                sedes = Container(field_sedes)
            except ValidationError as exception:
                # catch empty or duplicate fields and reraise as a TypeError as this would be an
                # invalid class definition
                raise TypeError(str(exception)) from exception

        else:
            serializable_bases = tuple(
                base for base in bases if isinstance(base, MetaSerializable)
            )
            bases_with_fields = tuple(
                base for base in serializable_bases if base._meta.has_fields
            )

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
                field_names=None,
                field_attrs=None,
            )
            return super().__new__(mcls, name, bases, assoc(namespace, "_meta", meta))

        # from here on, we can assume that we've got fields and a sedes object
        if sedes is None:
            raise Exception("Invariant: sedes has been initialized earlier")
        if len(fields) == 0:
            raise Exception(
                "Invariant: number of fields has been checked at initializion of sedes"
            )

        field_names, _ = zip(*fields)
        _validate_field_names(field_names)

        # the actual field values are stored in separate *private* attributes.
        # This computes attribute names that don't conflict with other
        # attributes already present on the class.
        reserved_namespace = set(namespace.keys()).union(
            attr
            for base in bases
            for parent_cls in base.__mro__
            for attr in _get_class_namespace(parent_cls)
        )
        field_attrs = _mk_field_attrs(field_names, reserved_namespace)
        field_props = _mk_field_props(field_names, field_attrs)

        # construct the Meta object to store field information for the class
        meta = Meta(
            has_fields=True,
            fields=fields,
            container_sedes=sedes,
            field_names=field_names,
            field_attrs=field_attrs,
        )
        return super().__new__(
            mcls, name, bases, merge(namespace, field_props, {"_meta": meta})
        )

    #
    # Implement BaseSedes methods as pass-throughs to the container sedes
    #
    def serialize(cls: Type[TSerializable], value: TSerializable) -> bytes:
        # return cls._meta.container_sedes.serialize(value)
        if value._serialize_cache is None:
            value._serialize_cache = cls._meta.container_sedes.serialize(value)
        return value._serialize_cache

    def deserialize(cls: Type[TSerializable], data: bytes) -> TSerializable:
        deserialized_fields = cls._meta.container_sedes.deserialize(data)
        deserialized_field_dict = dict(zip(cls._meta.field_names, deserialized_fields))
        return cls(**deserialized_field_dict)

    def get_hash_tree_root(
        cls: Type[TSerializable], value: TSerializable, cache: bool = True
    ) -> bytes:
        if cache:
            root, cache = cls._meta.container_sedes.get_hash_tree_root_and_leaves(
                value, value.cache
            )
            value.cache = cache
            return root
        else:
            return cls._meta.container_sedes.get_hash_tree_root(value)

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

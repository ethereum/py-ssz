import abc
import collections
import copy
import re
from typing import (
    Tuple,
    Type,
    TypeVar,
)

from eth_utils import (
    to_dict,
    to_set,
    to_tuple,
)

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


class MetaBase:
    fields = None
    field_names = None
    field_attrs = None
    container_sedes = None


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
        validate_args_and_kwargs(args, kwargs, self._meta.field_names)
        field_values = merge_kwargs_to_args(args, kwargs, self._meta.field_names)

        # Ensure that all the fields have been given values in initialization
        if len(field_values) != len(self._meta.field_names):
            raise TypeError(
                'Argument count mismatch. expected {0} - got {1} - missing {2}'.format(
                    len(self._meta.field_names),
                    len(field_values),
                    ','.join(self._meta.field_names[len(field_values):]),
                )
            )

        for value, attr in zip(field_values, self._meta.field_attrs):
            setattr(self, attr, make_immutable(value))

    def as_dict(self):
        return dict(
            (field, value)
            for field, value
            in zip(self._meta.field_names, self)
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
            raise IndexError("Unsupported type for __getitem__: {0}".format(type(index)))

    def __len__(self):
        return len(self._meta.fields)

    def __eq__(self, other):
        return isinstance(other, Serializable) and hash(self) == hash(other)

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
            self._hash_cache = hash(tuple(self))

        return self._hash_cache

    def copy(self, *args, **kwargs):
        missing_overrides = set(
            self._meta.field_names
        ).difference(
            kwargs.keys()
        ).difference(
            self._meta.field_names[:len(args)]
        )
        unchanged_kwargs = {
            key: copy.deepcopy(value)
            for key, value
            in self.as_dict().items()
            if key in missing_overrides
        }
        combined_kwargs = dict(**unchanged_kwargs, **kwargs)
        all_kwargs = merge_args_to_kwargs(args, combined_kwargs, self._meta.field_names)
        return type(self)(**all_kwargs)

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self, *args):
        return self.copy()


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
            field = '_' + field
            if field not in namespace:
                namespace.add(field)
                yield field
                break


def _mk_field_property(field, attr):
    def field_fn_getter(self):
        return getattr(self, attr)

    def field_fn_setter(self, value):
        raise AttributeError(
            "Created Object is Immutable, can't set attribute"
        )

    return property(field_fn_getter, field_fn_setter)


IDENTIFIER_REGEX = re.compile(r"^[^\d\W]\w*\Z", re.UNICODE)


def _is_valid_identifier(value):
    # Source: https://stackoverflow.com/questions/5474008/regular-expression-to-confirm-whether-a-string-is-a-valid-identifier-in-python  # noqa: E501
    if not isinstance(value, str):
        return False
    return bool(IDENTIFIER_REGEX.match(value))


@to_set
def _get_class_namespace(cls):
    if hasattr(cls, '__dict__'):
        yield from cls.__dict__.keys()
    if hasattr(cls, '__slots__'):
        yield from cls.__slots__


class SerializableBase(abc.ABCMeta):

    def __new__(cls, name, bases, attrs):
        super_new = super(SerializableBase, cls).__new__

        serializable_bases = tuple(b for b in bases if isinstance(b, SerializableBase))
        has_multiple_serializable_parents = len(serializable_bases) > 1
        is_serializable_subclass = any(serializable_bases)
        declares_fields = 'fields' in attrs

        if not is_serializable_subclass:
            # If this is the original creation of the `Serializable` class,
            # just create the class.
            return super_new(cls, name, bases, attrs)
        elif not declares_fields:
            if has_multiple_serializable_parents:
                raise TypeError(
                    "Cannot create subclass from multiple parent `Serializable` "
                    "classes without explicit `fields` declaration."
                )
            else:
                # This is just a vanilla subclass of a `Serializable` parent class.
                parent_serializable = serializable_bases[0]

                if hasattr(parent_serializable, '_meta'):
                    fields = parent_serializable._meta.fields
                else:
                    # This is a subclass of `Serializable` which has no
                    # `fields`, likely intended for further subclassing.
                    fields = ()
        else:
            # ensure that the `fields` property is a tuple of tuples to ensure
            # immutability.
            fields = tuple(tuple(field) for field in attrs.pop('fields'))

        # split the fields into names and sedes
        if fields:
            field_names, sedes = zip(*fields)
        else:
            field_names = ()

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
            field_name
            for field_name
            in field_names
            if not _is_valid_identifier(field_name)
        }
        if invalid_field_names:
            raise TypeError(
                "The following field names are not valid python identifiers: {0}".format(
                    ",".join("`{0}`".format(item) for item in sorted(invalid_field_names))
                )
            )

        # extract all of the fields from parent `Serializable` classes.
        parent_field_names = {
            field_name
            for base in serializable_bases if hasattr(base, '_meta')
            for field_name in base._meta.field_names
        }

        # check that all fields from parent serializable classes are
        # represented on this class.
        missing_fields = parent_field_names.difference(field_names)
        if missing_fields:
            raise TypeError(
                "Subclasses of `Serializable` **must** contain a full superset "
                "of the fields defined in their parent classes.  The following "
                "fields are missing: "
                "{0}".format(",".join(sorted(missing_fields)))
            )

        # the actual field values are stored in separate *private* attributes.
        # This computes attribute names that don't conflict with other
        # attributes already present on the class.
        reserved_namespace = set(attrs.keys()).union(
            attr
            for base in bases
            for parent_cls in base.__mro__
            for attr in _get_class_namespace(parent_cls)
        )
        field_attrs = _mk_field_attrs(field_names, reserved_namespace)

        # construct the Meta object to store field information for the class
        meta_namespace = {
            'fields': fields,
            'field_attrs': field_attrs,
            'field_names': field_names,
            'container_sedes': Container(fields),
        }

        meta_base = attrs.pop('_meta', MetaBase)
        meta = type(
            'Meta',
            (meta_base,),
            meta_namespace,
        )
        attrs['_meta'] = meta

        # construct `property` attributes for read only access to the fields.
        field_props = tuple(
            (field, _mk_field_property(field, attr))
            for field, attr
            in zip(meta.field_names, meta.field_attrs)
        )

        return super_new(
            cls,
            name,
            bases,
            dict(field_props + tuple(attrs.items())),
        )

    #
    # Implement BaseSedes methods as pass-throughs to the container sedes
    #
    @property
    def is_static_sized(cls):
        return cls._meta.container_sedes.is_static_sized

    def get_static_size(cls):
        cls._meta.container_sedes.get_static_size()

    def serialize(cls: Type[TSerializable], value: TSerializable) -> bytes:
        return cls._meta.container_sedes.serialize(value)

    def deserialize(cls: Type[TSerializable], data: bytes) -> TSerializable:
        deserialized_field_dict = cls._meta.container_sedes.deserialize(data)
        return cls(**deserialized_field_dict)

    def deserialize_segment(cls: Type[TSerializable],
                            data: bytes,
                            start_index: int) -> Tuple[TSerializable, int]:
        deserialized_field_dict, continuation_index = cls._meta.container_sedes.deserialize_segment(
            data,
            start_index,
        )
        return cls(**deserialized_field_dict), continuation_index

    def consume_bytes(cls, data: bytes, start_index: int, num_bytes: int) -> Tuple[bytes, int]:
        return cls._meta.container_sedes.consume_bytes(data, start_index, num_bytes)

    def hash_tree_root(cls: Type[TSerializable], value: TSerializable) -> bytes:
        return cls._meta.container_sedes.hash_tree_root(value)


# Make any class created with SerializableBase an instance of BaseSedes
BaseSedes.register(SerializableBase)


class Serializable(BaseSerializable, metaclass=SerializableBase):
    """
    The base class for serializable objects.
    """
    pass

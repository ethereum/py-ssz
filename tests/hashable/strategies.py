from hypothesis import strategies as st

from ssz.hashable_container import HashableContainer
from ssz.hashable_list import HashableList
from ssz.hashable_vector import HashableVector
from ssz.sedes import BasicSedes, Container, List, UInt, Vector, boolean
from ssz.sedes.serializable import Serializable


#
# Basic value strategies
#
@st.composite
def uint_value_st(draw, bits=None):
    if bits is None:
        bytes_ = 2 ** draw(st.integers(0, 5))
        bits = bytes_ * 8
    return draw(st.integers(0, bits))


def bool_value_st():
    return st.booleans()


#
# Composite value strategies
#
@st.composite
def vector_value_st(draw, elements, *, size=None):
    if size is None:
        size = draw(st.integers(0, 10))
    return st.builds(tuple, st.lists(elements, min_size=size, max_size=size))


@st.composite
def list_value_st(draw, elements, *, size=None):
    if size is None:
        size = draw(st.integers(0, 10))
    return st.lists(elements, min_size=size, max_size=size)


def container_value_st(element_sequence):
    return st.tuples(*element_sequence)


#
# Strategies for basic sedes with corresponding value strategy
#
def boolean_sedes_and_values_st():
    return st.just((boolean, bool_value_st()))


@st.composite
def uint_sedes_and_values_st(draw):
    bytes_ = 2 ** draw(st.integers(0, 5))
    bits = bytes_ * 8
    return UInt(bits), uint_value_st(bits)


#
# Strategies for composite sedes objects with corresponding value strategy
#
@st.composite
def general_vector_sedes_and_values_st(draw, element_sedes_and_elements, size=None):
    element_sedes, elements = element_sedes_and_elements

    if size is None:
        size = draw(st.integers(min_value=1, max_value=10))

    sedes = Vector(length=size, element_sedes=element_sedes)
    values = st.builds(tuple, st.lists(elements, min_size=size, max_size=size))
    return sedes, values


@st.composite
def general_list_sedes_and_values_st(draw, element_sedes_and_elements, size=None):
    element_sedes, elements = element_sedes_and_elements

    if size is None:
        size = draw(st.integers(min_value=1, max_value=10))
    max_size = draw(st.integers(min_value=size))

    sedes = List(element_sedes, max_length=max_size)
    values = st.lists(elements, min_size=size, max_size=size)
    return sedes, values


@st.composite
def general_container_sedes_and_values_st(draw, element_sedes_and_elements_sequence):
    element_sedes, elements = zip(*element_sedes_and_elements_sequence)
    sedes = Container(element_sedes)
    values = st.tuples(*elements)
    return sedes, values


#
# Strategies for depth-1 composite sedes objects with corresponding value strategy
#
@st.composite
def basic_vector_sedes_and_values_st(draw, size=None):
    sedes, values = draw(basic_sedes_and_values_st())
    return draw(general_vector_sedes_and_values_st((sedes, values), size=size))


@st.composite
def basic_list_sedes_and_values_st(draw, size=None):
    sedes, values = draw(basic_sedes_and_values_st())
    return draw(general_list_sedes_and_values_st((sedes, values), size=size))


@st.composite
def basic_container_sedes_and_values_st(draw, size=None):
    if size is None:
        size = draw(st.integers(min_value=1, max_value=4))

    element_sedes_and_elements_sequence = draw(
        st.lists(basic_sedes_and_values_st(), min_size=size, max_size=size)
    )
    return draw(
        general_container_sedes_and_values_st(element_sedes_and_elements_sequence)
    )


#
# Strategies for depth-2 composite sedes objects with corresponding value strategy
#
@st.composite
def nested_vector_sedes_and_values_st(draw, size=None):
    sedes, values = draw(basic_composite_sedes_and_values_st())
    return draw(general_vector_sedes_and_values_st((sedes, values), size=size))


@st.composite
def nested_list_sedes_and_values_st(draw, size=None):
    sedes, values = draw(basic_composite_sedes_and_values_st())
    return draw(general_list_sedes_and_values_st((sedes, values), size=size))


@st.composite
def nested_container_sedes_and_values_st(draw, size=None):
    if size is None:
        size = draw(st.integers(min_value=1, max_value=4))
    fields = st.one_of(
        basic_sedes_and_values_st(), basic_composite_sedes_and_values_st()
    )
    element_sedes_and_elements_sequence = draw(
        st.lists(fields, min_size=size, max_size=size)
    )
    return draw(
        general_container_sedes_and_values_st(element_sedes_and_elements_sequence)
    )


#
# Combinations
#
def basic_sedes_and_values_st():
    return st.one_of(boolean_sedes_and_values_st(), uint_sedes_and_values_st())


def basic_composite_sedes_and_values_st():
    return st.one_of(
        basic_vector_sedes_and_values_st(),
        basic_list_sedes_and_values_st(),
        basic_container_sedes_and_values_st(),
    )


def nested_composite_sedes_and_values_st():
    return st.one_of(
        nested_vector_sedes_and_values_st(),
        nested_list_sedes_and_values_st(),
        nested_container_sedes_and_values_st(),
    )


def composite_sedes_and_values_st():
    return st.one_of(
        basic_composite_sedes_and_values_st(), nested_composite_sedes_and_values_st()
    )


def vector_sedes_and_values_st(size=None):
    return st.one_of(
        basic_vector_sedes_and_values_st(size=size),
        nested_vector_sedes_and_values_st(size=size),
    )


def list_sedes_and_values_st(size=None):
    return st.one_of(
        basic_list_sedes_and_values_st(size=size),
        nested_list_sedes_and_values_st(size=size),
    )


def container_sedes_and_values_st(size=None):
    return st.one_of(
        basic_container_sedes_and_values_st(size=size),
        nested_container_sedes_and_values_st(size=size),
    )


#
# Convert plain Python values generated by strategies to serializable or hashable datatypes
#
def to_serializable_value(value, sedes):
    if isinstance(sedes, BasicSedes):
        return value

    elif isinstance(sedes, List):
        elements = tuple(
            to_serializable_value(element, sedes.element_sedes) for element in value
        )
        return elements

    elif isinstance(sedes, Vector):
        elements = tuple(
            to_serializable_value(element, sedes.element_sedes) for element in value
        )
        return elements

    elif isinstance(sedes, Container):
        field_names = [f"field{index}" for index in range(len(value))]

        class ValueClass(Serializable):
            fields = tuple(
                (field_name, field_sedes)
                for field_name, field_sedes in zip(field_names, sedes.field_sedes)
            )

        kwargs = {
            field_name: to_hashable_value(field_value, field_sedes)
            for field_name, field_value, field_sedes in zip(
                field_names, value, sedes.field_sedes
            )
        }

        return ValueClass(**kwargs)

    else:
        assert False


def to_hashable_value(value, sedes):
    if isinstance(sedes, BasicSedes):
        return value

    elif isinstance(sedes, List):
        elements = (
            to_hashable_value(element, sedes.element_sedes) for element in value
        )
        return HashableList.from_iterable(elements, sedes)

    elif isinstance(sedes, Vector):
        elements = (
            to_hashable_value(element, sedes.element_sedes) for element in value
        )
        return HashableVector.from_iterable(value, sedes)

    elif isinstance(sedes, Container):
        field_names = [f"field{index}" for index in range(len(value))]

        class ValueClass(HashableContainer):
            fields = tuple(
                (field_name, field_sedes)
                for field_name, field_sedes in zip(field_names, sedes.field_sedes)
            )

        kwargs = {
            field_name: to_hashable_value(field_value, field_sedes)
            for field_name, field_value, field_sedes in zip(
                field_names, value, sedes.field_sedes
            )
        }

        return ValueClass.create(**kwargs)

    else:
        assert False


def to_plain_value(serializable_or_hashable_value, sedes):
    if isinstance(sedes, BasicSedes):
        return serializable_or_hashable_value

    elif isinstance(sedes, List):
        return [
            to_plain_value(element, sedes.element_sedes)
            for element in serializable_or_hashable_value
        ]

    elif isinstance(sedes, Vector):
        return tuple(
            to_plain_value(element, sedes.element_sedes)
            for element in serializable_or_hashable_value
        )

    elif isinstance(sedes, Container):
        return tuple(
            to_plain_value(element, field_sedes)
            for element, field_sedes in zip(
                serializable_or_hashable_value, sedes.field_sedes
            )
        )

    else:
        assert False

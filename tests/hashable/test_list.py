import itertools

from hypothesis import assume, given
from hypothesis import strategies as st

import ssz
from tests.hashable.strategies import (
    composite_sedes_and_values_st,
    container_sedes_and_values_st,
    list_sedes_and_values_st,
    to_hashable_value,
    to_plain_value,
    to_serializable_value,
    vector_sedes_and_values_st,
)


@given(st.data(), composite_sedes_and_values_st())
def test_root(data, sedes_and_values):
    sedes, values = sedes_and_values
    value = data.draw(values)

    serializable_value = to_serializable_value(value, sedes)
    serializable_root = ssz.get_hash_tree_root(serializable_value, sedes)

    hashable_value = to_hashable_value(value, sedes)
    hashable_root = ssz.get_hash_tree_root(hashable_value, sedes)

    assert serializable_root == hashable_root


@given(st.data(), composite_sedes_and_values_st())
def test_encoding(data, sedes_and_values):
    sedes, values = sedes_and_values
    value = data.draw(values)

    serializable_value = to_serializable_value(value, sedes)
    serializable_encoding = ssz.encode(serializable_value, sedes)

    hashable_value = to_hashable_value(value, sedes)
    hashable_encoding = ssz.encode(hashable_value, sedes)

    assert serializable_encoding == hashable_encoding


@given(st.data(), composite_sedes_and_values_st(), composite_sedes_and_values_st())
def test_equality(data, sedes_and_values_1, sedes_and_values_2):
    sedes1, values1 = sedes_and_values_1
    sedes2, values2 = sedes_and_values_2
    value1 = data.draw(values1)
    value2 = data.draw(values2)
    assume(sedes1 != sedes2 or value1 != value2)

    hashable_value_1 = to_hashable_value(value1, sedes1)
    hashable_value_2 = to_hashable_value(value2, sedes2)

    assert hashable_value_1 == hashable_value_1
    assert hashable_value_2 == hashable_value_2
    assert hash(hashable_value_1) == hash(hashable_value_1)
    assert hash(hashable_value_2) == hash(hashable_value_2)
    assert hashable_value_1 != hashable_value_2
    assert hash(hashable_value_1) != hash(hashable_value_2)


@given(st.data(), st.one_of(list_sedes_and_values_st(), vector_sedes_and_values_st()))
def test_sequence_access(data, sequence_sedes_and_values):
    sedes, values = sequence_sedes_and_values
    value = data.draw(values)

    element_sedes = sedes.element_sedes
    hashable_value = to_hashable_value(value, sedes)

    # __len__
    assert len(hashable_value) == len(value)

    # __getitem__
    for index in range(len(value)):
        index_neg = index - len(value)
        plain_value = to_plain_value(hashable_value[index], element_sedes)
        plain_value_neg = to_plain_value(hashable_value[index_neg], element_sedes)
        assert plain_value == value[index]
        assert plain_value_neg == value[index_neg]

    # __iter__
    for hashable_element, plain_element in zip(hashable_value, value):
        assert to_plain_value(hashable_element, sedes.element_sedes) == plain_element


@given(st.data(), container_sedes_and_values_st())
def test_container_access(data, sedes_and_values):
    sedes, values = sedes_and_values
    value = data.draw(values)

    hashable_value = to_hashable_value(value, sedes)
    field_names = [f"field{index}" for index in range(len(value))]

    # __len__
    assert len(hashable_value) == len(value)

    # __getitem__ with int
    for index, field_sedes in enumerate(sedes.field_sedes):
        index_neg = index - len(value)
        plain_value = to_plain_value(hashable_value[index], field_sedes)
        plain_value_neg = to_plain_value(hashable_value[index_neg], field_sedes)
        assert plain_value == value[index]
        assert plain_value_neg == value[index_neg]

    # __getitem__ with field name and __getattr__
    for index, (field_name, field_sedes) in enumerate(
        zip(field_names, sedes.field_sedes)
    ):
        value_item = hashable_value[field_name]
        value_attr = getattr(hashable_value, field_name)
        plain_value_item = to_plain_value(value_item, field_sedes)
        plain_value_attr = to_plain_value(value_attr, field_sedes)
        assert plain_value_item == value[index]
        assert plain_value_attr == value[index]

    # __iter__
    for hashable_element, plain_element, field_sedes in zip(
        hashable_value, value, sedes.field_sedes
    ):
        assert to_plain_value(hashable_element, field_sedes) == plain_element


@given(
    st.data(),
    st.one_of(st.just(list_sedes_and_values_st), st.just(vector_sedes_and_values_st)),
    st.integers(min_value=1, max_value=10),
)
def test_sequence_manipulation(data, sequence_type_and_values_st, sequence_size):
    sedes, values = data.draw(sequence_type_and_values_st(size=sequence_size))

    value = data.draw(values)
    replacement_value = data.draw(values)

    hashable_value = to_hashable_value(value, sedes)
    hashable_replacement_value = to_hashable_value(replacement_value, sedes)

    replacement_index_st = st.integers(
        min_value=-sequence_size, max_value=sequence_size - 1
    )
    replacement_indices = data.draw(st.lists(replacement_index_st, unique=True))
    replacements = [(index, replacement_value[index]) for index in replacement_indices]
    hashable_replacements = [
        (index, hashable_replacement_value[index]) for index in replacement_indices
    ]

    # expected result
    replaced_value = list(value)
    for index, new_value in replacements:
        replaced_value[index] = new_value
    replaced_value = type(value)(replaced_value)

    # set
    hashable_value_set = hashable_value
    for index, new_value in hashable_replacements:
        hashable_value_set = hashable_value_set.set(index, new_value)
        assert hashable_value_set[index] == new_value

    # mset
    hashable_value_mset = hashable_value.mset(
        *itertools.chain.from_iterable(hashable_replacements)
    )

    # evolver
    evolver = hashable_value.evolver()
    for index, new_value in hashable_replacements:
        evolver[index] = new_value
        assert evolver[index] == new_value
    hashable_value_evolved = evolver.persistent()

    assert to_plain_value(hashable_value_mset, sedes) == replaced_value
    assert hashable_value_set == hashable_value_mset
    assert hashable_value_evolved == hashable_value_mset


@given(st.data(), st.integers(min_value=1, max_value=10))
def test_container_manipulation(data, size):
    sedes, values = data.draw(container_sedes_and_values_st(size=size))

    value = data.draw(values)
    replacement_value = data.draw(values)

    hashable_value = to_hashable_value(value, sedes)
    hashable_replacement_value = to_hashable_value(replacement_value, sedes)

    replacement_index_st = st.integers(min_value=-size, max_value=size - 1)
    replacement_indices = data.draw(st.lists(replacement_index_st, unique=True))
    replacement_names = [
        hashable_replacement_value._meta.fields[index][0]
        for index in replacement_indices
    ]

    replacements = [replacement_value[index] for index in replacement_indices]
    hashable_replacements = [
        hashable_replacement_value[index] for index in replacement_indices
    ]
    indices_names_replacements = zip(
        replacement_indices, replacement_names, hashable_replacements
    )

    # expected result
    replaced_value = list(value)
    for index, new_value in zip(replacement_indices, replacements):
        replaced_value[index] = new_value
    replaced_value = tuple(replaced_value)

    # set by index, name, and attr
    hashable_value_set_index = hashable_value
    hashable_value_set_name = hashable_value
    evolver = hashable_value.evolver()

    for index, name, new_value in indices_names_replacements:
        hashable_value_set_index = hashable_value_set_index.set(index, new_value)
        hashable_value_set_name = hashable_value_set_name.set(name, new_value)
        setattr(evolver, name, new_value)
        for container in (hashable_value_set_index, hashable_value_set_name, evolver):
            assert container[index] == new_value
            assert container[name] == new_value
            assert getattr(container, name) == new_value
    hashable_value_evolved = evolver.persistent()

    # mset by index and name
    hashable_value_mset_index = hashable_value.mset(
        *itertools.chain.from_iterable(zip(replacement_indices, hashable_replacements))
    )
    hashable_value_mset_name = hashable_value.mset(
        *itertools.chain.from_iterable(zip(replacement_names, hashable_replacements))
    )

    assert to_plain_value(hashable_value_set_index, sedes) == replaced_value
    assert hashable_value_set_name == hashable_value_set_index
    assert hashable_value_evolved == hashable_value_set_index
    assert hashable_value_mset_index == hashable_value_set_index
    assert hashable_value_mset_name == hashable_value_set_index


@given(st.data(), list_sedes_and_values_st())
def test_list_extend(data, list_sedes_and_values):
    sedes, values = list_sedes_and_values

    value = data.draw(values)
    extension = data.draw(values)[: len(value) - sedes.max_length]
    hashable_value = to_hashable_value(value, sedes)
    hashable_extension = to_hashable_value(extension, sedes)

    # expected result
    extended_value = value + extension

    # extend with appends
    hashable_value_appended = hashable_value
    append_evolver = hashable_value.evolver()
    for num_appended, element in enumerate(hashable_extension, start=1):
        hashable_value_appended = hashable_value_appended.append(element)
        append_evolver.append(element)
        for intermediate in (hashable_value_appended, append_evolver):
            assert len(intermediate) == len(value) + num_appended
            assert intermediate[len(intermediate) - 1] == element
            assert intermediate[-1] == element
    hashable_value_append_evolved = append_evolver.persistent()

    # extend with extend
    hashable_value_extended = hashable_value.extend(hashable_extension)
    extend_evolver = hashable_value.evolver()
    extend_evolver.extend(hashable_extension)
    hashable_value_extend_evolved = extend_evolver.persistent()

    # extend with +
    hashable_value_plussed = hashable_value + hashable_extension

    # compare results
    assert to_plain_value(hashable_value_appended, sedes) == extended_value
    assert hashable_value_append_evolved == hashable_value_appended
    assert hashable_value_extended == hashable_value_appended
    assert hashable_value_extend_evolved == hashable_value_appended
    assert hashable_value_plussed == hashable_value_appended

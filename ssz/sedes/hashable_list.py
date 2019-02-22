from itertools import (
    count,
    dropwhile,
)
import math

from eth_utils import (
    to_tuple,
    ValidationError,
)
from eth_utils.toolz import (
    first,
    iterate,
    partition,
    sliding_window,
    take,
)

import ssz
from ssz.hash import (
    hash_eth2,
)
from ssz.constants import (
    CHUNK_SIZE,
    EMPTY_CHUNK,
)


def get_next_power_of_two(value):
    """Get the smallest power of two that is greater or equal to the given value."""
    powers_of_two = (2**exponent for exponent in count())
    greater_or_equal_powers_of_two = dropwhile(lambda power: power < value, powers_of_two)
    return first(greater_or_equal_powers_of_two)


def get_items_per_chunk(item_length):
    """Get the number of items that fit inside a single chunk."""
    if item_length <= CHUNK_SIZE:
        return CHUNK_SIZE // item_length
    else:
        return 1


def get_chunk_index_for_item(item_index, item_length):
    """Get the index of the chunk in which a certain item will be placed."""
    items_per_chunk = get_items_per_chunk(item_length)
    return item_index // items_per_chunk


def get_item_index_in_chunk(item_index, item_length):
    """Get the index that a given item will have relative to its containing shard."""
    items_per_chunk = get_items_per_chunk(item_length)
    return item_index % items_per_chunk


def get_chunks(encoded_items):
    """Get a sequence of chunks encoding the given items. Each item must have the same size."""
    if len(encoded_items) == 0:
        return (EMPTY_CHUNK,)
    else:
        item_length = len(encoded_items[0])
        if any(item_length != len(encoded_item) for encoded_item in encoded_items):
            raise ValueError("Encoded items must have the same length")
        items_per_chunk = get_items_per_chunk(item_length)

        items_grouped_by_chunk = partition(items_per_chunk, encoded_items, pad=b"")
        chunks = tuple(
            b"".join(items_in_chunk).ljust(CHUNK_SIZE, b"\x00")
            for items_in_chunk in items_grouped_by_chunk
        )

        return chunks


def calc_chunk_tree(chunks):
    """Calculate the merkle tree defined by a sequence of chunks at the base layer."""
    chunks = tuple(chunks)
    if len(chunks) == 0:
        chunks = (EMPTY_CHUNK,)

    base_layer_length = get_next_power_of_two(len(chunks))
    base_layer = chunks + (EMPTY_CHUNK,) * (base_layer_length - len(chunks))

    assert math.log2(len(base_layer)).is_integer()
    number_of_layers = int(math.log2(len(base_layer)) + 1)

    layers = take(
        number_of_layers,
        iterate(calc_parent_layer, base_layer),
    )
    return tuple(layers)


def validate_merkle_tree(merkle_tree):
    """Check that the given tree is a valid binary merkle tree."""
    for child_layer, parent_layer in sliding_window(2, merkle_tree):
        if not len(parent_layer) * 2 == len(child_layer):
            raise ValidationError("Given merkle tree is not binary")

        for left_child_index, right_child_index in partition(2, range(len(child_layer))):
            left_child = child_layer[left_child_index]
            right_child = child_layer[right_child_index]
            expected_parent = calc_parent_hash(left_child, right_child)

            parent_index = left_child_index // 2
            parent = parent_layer[parent_index]

            if not parent == expected_parent:
                raise ValidationError("Given merkle tree contains invalid entries")


def calc_parent_hash(left_child, right_child):
    """Calculate the parent of two children in a merkle tree."""
    return hash_eth2(left_child + right_child)


def calc_parent_layer(child_layer):
    """Calculate the next layer in a merkle tree."""
    return tuple(
        calc_parent_hash(left, right)
        for left, right in partition(2, child_layer)
    )


def get_sibling_index(index):
    """Given the index of a node in some layer of a merkle tree, get the index of its sibling."""
    return index // 2 * 2 + (index + 1) % 2


def calc_updated_chunk(chunk, index_in_chunk, encoded_item):
    """Replace an item at a given index in a chunk."""
    item_length = len(encoded_item)

    new_chunk = b"".join((
        chunk[:index_in_chunk * item_length],
        encoded_item,
        chunk[(index_in_chunk + 1) * item_length:],
    ))
    if len(new_chunk) != CHUNK_SIZE:
        raise Exception("Invariant: chunk size does not change")

    return new_chunk


@to_tuple
def calc_updated_chunk_tree(chunk_tree, chunk_index, chunk):
    """Replace a chunk in a chunk tree and return the updated chunk tree."""
    old_base_layer = chunk_tree[0]
    new_base_layer = old_base_layer[:chunk_index] + (chunk,) + old_base_layer[chunk_index + 1:]
    yield new_base_layer

    affected_indices = tuple(take(
        len(chunk_tree),
        iterate(lambda value: value // 2, chunk_index),
    ))
    sibling_indices = tuple(get_sibling_index(index) for index in affected_indices)

    new_child_layer = new_base_layer
    for (
        old_parent_layer,
        affected_parent_index,
        affected_child_index,
        sibling_child_index
    ) in zip(
        chunk_tree[1:],
        affected_indices[1:],
        affected_indices,
        sibling_indices,
    ):
        left_child = new_child_layer[min(affected_child_index, sibling_child_index)]
        right_child = new_child_layer[max(affected_child_index, sibling_child_index)]
        new_parent = calc_parent_hash(left_child, right_child)

        new_parent_layer = (
            old_parent_layer[:affected_parent_index] +
            (new_parent,) +
            old_parent_layer[affected_parent_index + 1:]
        )
        yield new_parent_layer

        new_child_layer = new_parent_layer


def get_root(merkle_tree):
    """Get the root of a merkle tree."""
    return merkle_tree[-1][0]


@to_tuple
def get_conjoined_merkle_tree(left_tree, right_tree):
    """Join two merkle trees of same size and return the result."""
    if len(left_tree) != len(right_tree):
        raise ValidationError("Cannot join merkle trees as they have different sizes")

    for left_layer, right_layer in zip(left_tree, right_tree):
        yield left_layer + right_layer

    left_root = get_root(left_tree)
    right_root = get_root(right_tree)
    yield calc_parent_layer((left_root, right_root))


def validate_copy_arguments(*,
                            replace=None,
                            insert=None,
                            remove=None,
                            prepend=None,
                            append=None):
    specified_arguments = [
        name
        for name, value in (
            ("replace", replace),
            ("insert", insert),
            ("remove", remove),
            ("prepend", prepend),
            ("append", append),
        )
        if value is not None
    ]

    if len(specified_arguments) > 1:
        raise ValidationError(
            f"At most one copy argument is allowed, but got the following:"
            f"{', '.join(not_none_arguments)}"
        )


class HashableList:

    def __init__(self, items, item_sedes, tree=None) -> None:
        self._items = tuple(items)
        self._item_sedes = item_sedes

        if tree is None:
            self._initialize_tree()
        else:
            self._tree = tree

    def _initialize_tree(self):
        encoded_items = tuple(ssz.encode(item, self._item_sedes) for item in self._items)
        chunks = get_chunks(encoded_items)
        self._tree = calc_chunk_tree(chunks)

    def __len__(self):
        return len(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def __iter__(self):
        return self._items.__iter__()

    @property
    def _chunks(self):
        return self._tree[0]

    @property
    def _item_length(self):
        return self._item_sedes.length

    @property
    def root(self):
        # The stored tree can be bigger than necessary if items have been removed. In that case,
        # only return the root of the subtree that is actually used.
        used_chunks = get_chunk_index_for_item(len(self) - 1, self._item_length) + 1
        effective_chunk_layer_size = get_next_power_of_two(used_chunks)
        effective_root_layer_index = int(math.log2(effective_chunk_layer_size))
        effective_tree_root = self._tree[effective_root_layer_index][0]

        return hash_eth2(effective_tree_root + len(self).to_bytes(32, "little"))

    #
    # Copy and update methods
    #
    def copy(self,
             *,
             replace=None,
             append=None,
             ):

        validate_copy_arguments(
            replace=replace,
            append=append,
        )

        if replace is not None:
            if len(replace) == 0:
                return self.copy()
            else:
                (index, item), *rest = replace.items()
                return self.copy_and_replace(index, item).copy(replace=dict(rest))

        elif append is not None:
            return self.copy_and_append(append)

        else:
            return self.__class__(self._items, self._item_sedes, self._tree)

    def copy_and_replace(self, index, item):
        if index >= len(self):
            raise ValidationError(
                f"Item at index {index} does not exist as list has a length of only "
                f"{len(self)}"
            )

        items = self._items[:index] + (item,) + self._items[index + 1:]

        encoded_item = ssz.encode(item, self._item_sedes)

        chunk_index = get_chunk_index_for_item(index, self._item_length)
        item_index_in_chunk = get_item_index_in_chunk(index, self._item_length)

        chunk = calc_updated_chunk(
            chunk=self._chunks[chunk_index],
            index_in_chunk=item_index_in_chunk,
            encoded_item=encoded_item,
        )

        tree = calc_updated_chunk_tree(
            chunk_tree=self._tree,
            chunk_index=chunk_index,
            chunk=chunk,
        )

        return self.__class__(items, self._item_sedes, tree)

    def copy_and_append(self, item):
        items = self._items + (item,)

        item_index = len(self)
        chunk_index = get_chunk_index_for_item(item_index, self._item_length)
        index_in_chunk = get_item_index_in_chunk(item_index, self._item_length)

        encoded_item = ssz.encode(item, self._item_sedes)

        if chunk_index < len(self._chunks):
            chunk = calc_updated_chunk(self._chunks[chunk_index], index_in_chunk, encoded_item)
            tree = calc_updated_chunk_tree(self._tree, chunk_index, chunk)
        else:
            if chunk_index != len(self._chunks) or index_in_chunk != 0:
                raise Exception("Invariant: Item is first in the first chunk that will be added")

            chunk = calc_updated_chunk(EMPTY_CHUNK, 0, encoded_item)
            added_subtree = calc_chunk_tree((chunk,) + (EMPTY_CHUNK,) * (len(self._chunks) - 1))
            tree = get_conjoined_merkle_tree(self._tree, added_subtree)

        return self.__class__(items, self._item_sedes, tree)

from functools import partial
import itertools
from numbers import Integral
from typing import Any, Generator, Iterable, Optional, Union

# `transform` comes from a non-public API which is considered stable, but future changes can not be
# ruled out completely. Therefore, the implementation should be reviewed whenever pyrsistent is
# updated. See https://github.com/tobgu/pyrsistent/issues/180 for more information.
from eth_typing import Hash32
from eth_utils.toolz import drop, iterate, partition, pipe, take
from pyrsistent import pmap, pvector
from pyrsistent._transformations import transform
from pyrsistent.typing import PMap, PVector

from ssz.constants import ZERO_HASHES
from ssz.hash import hash_eth2
from ssz.utils import get_next_power_of_two

RawHashTreeLayer = PVector[Hash32]
RawHashTree = PVector[RawHashTreeLayer]


def validate_chunk_count(chunk_count: Optional[int]) -> None:
    if chunk_count is not None:
        if chunk_count <= 0:
            raise ValueError(f"Chunk count is not positive: {chunk_count}")


def validate_raw_hash_tree(
    raw_hash_tree: RawHashTree, chunk_count: Optional[int] = None
) -> None:
    if len(raw_hash_tree) == 0:
        raise ValueError("Hash tree is empty")

    if len(raw_hash_tree[0]) == 0:
        raise ValueError("Hash tree contains zero chunks")

    if chunk_count is not None and len(raw_hash_tree[0]) > chunk_count:
        raise ValueError(
            f"Hash tree contains {len(raw_hash_tree[0])} chunks which exceeds chunk count "
            f"{chunk_count}"
        )

    if len(raw_hash_tree[-1]) != 1:
        raise ValueError(
            f"Hash tree root layer contains {len(raw_hash_tree[-1])} items instead of 1"
        )


class HashTree(PVector[Hash32]):
    def __init__(
        self, raw_hash_tree: RawHashTree, chunk_count: Optional[int] = None
    ) -> None:
        validate_chunk_count(chunk_count)
        validate_raw_hash_tree(raw_hash_tree, chunk_count)

        self.chunk_count = chunk_count
        self.raw_hash_tree = raw_hash_tree

    @classmethod
    def compute(
        cls, chunks: Iterable[Hash32], chunk_count: Optional[int] = None
    ) -> "HashTree":
        raw_hash_tree = compute_hash_tree(chunks, chunk_count)
        return cls(raw_hash_tree, chunk_count)

    @property
    def chunks(self) -> RawHashTreeLayer:
        return self.raw_hash_tree[0]

    @property
    def root(self) -> Hash32:
        return self.raw_hash_tree[-1][0]

    def transform(self, *transformations):
        return transform(self, transformations)

    def evolver(self):
        return HashTreeEvolver(self)

    #
    # Comparison
    #
    def __hash__(self) -> int:
        return hash((self.root, self.chunk_count))

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, HashTree)
            and self.root == other.root
            and self.chunk_count == other.chunk_count
        )

    #
    # Chunk access
    #
    def __len__(self) -> int:
        return len(self.chunks)

    def __getitem__(self, index: Union[int, slice]) -> Hash32:
        return self.chunks[index]

    def index(self, value: Hash32, *args, **kwargs) -> Hash32:
        return self.chunks.index(value, *args, **kwargs)

    def count(self, value: Hash32) -> int:
        return self.chunks.count(value)

    #
    # Tree modifications via evolver
    #
    def append(self, value: Hash32) -> "HashTree":
        evolver = self.evolver()
        evolver.append(value)
        return evolver.persistent()

    def extend(self, value: Iterable[Hash32]) -> "HashTree":
        evolver = self.evolver()
        evolver.extend(value)
        return evolver.persistent()

    def __add__(self, other: Iterable[Hash32]) -> "HashTree":
        return self.extend(other)

    def __mul__(self, times: int) -> "HashTree":
        if times <= 0:
            raise ValueError(f"Multiplier must be greater or equal to 1, got {times}")

        evolver = self.evolver()

        for _ in range(times - 1):
            evolver.extend(self)

        return evolver.persistent()

    def mset(self, *args: Union[int, Hash32]) -> "HashTree":
        if len(args) % 2 != 0:
            raise TypeError(
                f"mset must be called with an even number of arguments, got {len(args)}"
            )

        evolver = self.evolver()
        for index, value in partition(2, args):
            evolver[index] = value
        return evolver.persistent()

    def set(self, index: int, value: Hash32) -> "HashTree":
        return self.mset(index, value)

    #
    # Removal of chunks
    #
    def delete(self, index: int, stop: Optional[int] = None) -> "HashTree":
        if stop is None:
            stop = index + 1
        chunks = self.chunks.delete(index, stop)
        return self.__class__.compute(chunks, self.chunk_count)

    def remove(self, value: Hash32) -> "HashTree":
        chunks = self.chunks.remove(value)
        return self.__class__.compute(chunks, self.chunk_count)


class HashTreeEvolver:
    def __init__(self, hash_tree: "HashTree") -> None:
        self.original_hash_tree = hash_tree
        self.updated_chunks: PMap[int, Hash32] = pmap()
        self.appended_chunks: PVector[Hash32] = pvector()

    #
    # Getters
    #
    def __getitem__(self, index: int) -> Hash32:
        if index < 0:
            index += len(self)

        if index in self.updated_chunks:
            return self.updated_chunks[index]
        else:
            if 0 <= index < len(self.original_hash_tree):
                return self.original_hash_tree[index]
            elif index < len(self):
                index_in_appendix = index - len(self.original_hash_tree)
                return self.appended_chunks[index_in_appendix]
            else:
                raise IndexError(f"Index out of bounds: {index}")

    def __len__(self) -> int:
        return len(self.original_hash_tree) + len(self.appended_chunks)

    def is_dirty(self) -> bool:
        return self.updated_chunks or self.appended_chunks

    #
    # Setters
    #
    def set(self, index: Integral, value: Hash32) -> None:
        self[index] = value

    def __setitem__(self, index: Integral, value: Hash32) -> None:
        if index < 0:
            index += len(self)

        if 0 <= index < len(self.original_hash_tree):
            self.updated_chunks = self.updated_chunks.set(index, value)
        elif index < len(self):
            index_in_appendix = index - len(self.original_hash_tree)
            self.appended_chunks = self.appended_chunks.set(index_in_appendix, value)
        else:
            raise IndexError(f"Index out of bounds: {index}")

    #
    # Length changing modifiers
    #
    def append(self, value: Hash32) -> None:
        self.appended_chunks = self.appended_chunks.append(value)
        self._check_chunk_count()

    def extend(self, values: Iterable[Hash32]) -> None:
        self.appended_chunks = self.appended_chunks.extend(values)
        self._check_chunk_count()

    def _check_chunk_count(self) -> None:
        chunk_count = self.original_hash_tree.chunk_count
        if chunk_count is not None and len(self) > chunk_count:
            raise ValueError(f"Hash tree exceeds size chunk count {chunk_count}")

    #
    # Not implemented
    #
    def delete(self, index, stop=None):
        raise NotImplementedError()

    def __delitem__(self, index):
        raise NotImplementedError()

    def remove(self, value):
        raise NotImplementedError()

    #
    # Persist
    #
    def persistent(self) -> "HashTree":
        if not self.is_dirty():
            return self.original_hash_tree
        else:
            setters = (
                partial(set_chunk_in_tree, index=index, chunk=chunk)
                for index, chunk in self.updated_chunks.items()
            )
            appenders = (
                partial(append_chunk_to_tree, chunk=chunk)
                for chunk in self.appended_chunks
            )
            raw_hash_tree = pipe(
                self.original_hash_tree.raw_hash_tree, *setters, *appenders
            )
            return self.original_hash_tree.__class__(
                raw_hash_tree, self.original_hash_tree.chunk_count
            )


def hash_layer(child_layer: RawHashTreeLayer, layer_index: int) -> RawHashTreeLayer:
    if len(child_layer) % 2 == 0:
        padded_child_layer = child_layer
    else:
        padded_child_layer = child_layer.append(ZERO_HASHES[layer_index])

    child_pairs = partition(2, padded_child_layer)
    parent_layer = pvector(
        hash_eth2(left_child + right_child) for left_child, right_child in child_pairs
    )
    return parent_layer


def generate_hash_tree_layers(
    chunks: RawHashTreeLayer
) -> Generator[RawHashTreeLayer, None, None]:
    yield chunks
    previous_layer = chunks

    for previous_layer_index in itertools.count():
        # stop if the root has been reached
        if len(previous_layer) <= 1:
            break
        if previous_layer_index > 1000:
            raise Exception("Invariant: Root is reached quickly")

        next_layer = hash_layer(previous_layer, previous_layer_index)

        yield next_layer
        previous_layer = next_layer


def get_num_layers(num_chunks: int, chunk_count: Optional[int]) -> int:
    if chunk_count is not None:
        virtual_size = chunk_count
    else:
        virtual_size = num_chunks

    return get_next_power_of_two(virtual_size).bit_length()


def generate_chunk_tree_padding(
    unpadded_chunk_tree: PVector[Hash32], chunk_count: Optional[int]
) -> Generator[Hash32, None, None]:
    if chunk_count is None:
        return

    num_chunks = len(unpadded_chunk_tree[0])
    if num_chunks > chunk_count:
        raise ValueError(
            f"Number of chunks in tree ({num_chunks}) exceeds chunk count {chunk_count}"
        )

    num_existing_layers = len(unpadded_chunk_tree)
    num_target_layers = get_next_power_of_two(chunk_count).bit_length()

    previous_root = unpadded_chunk_tree[-1][0]
    for previous_layer_index in range(num_existing_layers - 1, num_target_layers - 1):
        next_root = hash_eth2(previous_root + ZERO_HASHES[previous_layer_index])
        yield pvector([next_root])
        previous_root = next_root


def pad_hash_tree(
    unpadded_chunk_tree: RawHashTree, chunk_count: Optional[int] = None
) -> RawHashTree:
    padding = pvector(generate_chunk_tree_padding(unpadded_chunk_tree, chunk_count))
    return unpadded_chunk_tree + padding


def compute_hash_tree(
    chunks: Iterable[Hash32], chunk_count: Optional[int] = None
) -> RawHashTree:
    validate_chunk_count(chunk_count)

    chunks = pvector(chunks)

    if not chunks:
        raise ValueError("Number of chunks is 0")
    if chunk_count is not None and len(chunks) > chunk_count:
        raise ValueError(
            f"Number of chunks ({len(chunks)}) exceeds chunk_count ({chunk_count})"
        )

    unpadded_chunk_tree = pvector(generate_hash_tree_layers(chunks))
    return pad_hash_tree(unpadded_chunk_tree, chunk_count)


def recompute_hash_in_tree(
    hash_tree: RawHashTree, layer_index: int, hash_index: int
) -> RawHashTree:
    if layer_index == 0:
        raise ValueError(
            "Cannot recompute hash in leaf layer as it consists of chunks not hashes"
        )

    child_layer_index = layer_index - 1
    left_child_hash_index = hash_index * 2
    right_child_hash_index = left_child_hash_index + 1

    child_layer = hash_tree[child_layer_index]
    left_child_hash = child_layer[left_child_hash_index]
    try:
        right_child_hash = child_layer[right_child_hash_index]
    except IndexError:
        right_child_hash = ZERO_HASHES[child_layer_index]

    # create the layer if it doesn't exist yet (otherwise, pyrsistent would create a PMap)
    if layer_index == len(hash_tree):
        hash_tree = hash_tree.append(pvector())

    parent_hash = hash_eth2(left_child_hash + right_child_hash)
    return hash_tree.transform((layer_index, hash_index), parent_hash)


def set_chunk_in_tree(hash_tree: RawHashTree, index: int, chunk: Hash32) -> RawHashTree:
    hash_tree_with_updated_chunk = hash_tree.transform((0, index), chunk)

    parent_layer_indices = drop(1, range(len(hash_tree)))
    parent_hash_indices = drop(
        1, take(len(hash_tree), iterate(lambda index: index // 2, index))
    )

    update_functions = (
        partial(recompute_hash_in_tree, layer_index=layer_index, hash_index=hash_index)
        for layer_index, hash_index in zip(parent_layer_indices, parent_hash_indices)
    )

    hash_tree_with_updated_branch = pipe(
        hash_tree_with_updated_chunk, *update_functions
    )

    if len(hash_tree_with_updated_branch[-1]) == 1:
        return hash_tree_with_updated_branch
    elif len(hash_tree_with_updated_branch[-1]) == 2:
        return recompute_hash_in_tree(hash_tree_with_updated_branch, len(hash_tree), 0)
    else:
        raise Exception("Unreachable")


def append_chunk_to_tree(hash_tree: RawHashTree, chunk: Hash32) -> RawHashTree:
    return set_chunk_in_tree(hash_tree, len(hash_tree[0]), chunk)

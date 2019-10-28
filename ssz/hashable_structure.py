import itertools
from typing import (
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
)

from eth_typing import Hash32
from eth_utils.toolz import groupby, partition, pipe
from pyrsistent import pvector
from pyrsistent._transformations import transform
from pyrsistent.typing import PVector

import ssz
from ssz.abc import (
    HashableStructureAPI,
    HashableStructureEvolverAPI,
    ResizableHashableStructureAPI,
    ResizableHashableStructureEvolverAPI,
)
from ssz.constants import CHUNK_SIZE, ZERO_BYTES32
from ssz.hash_tree import HashTree
from ssz.sedes.base import BaseCompositeSedes
from ssz.sedes.basic import BasicSedes
from ssz.sedes.list import List as ListSedes
from ssz.sedes.vector import Vector

TStructure = TypeVar("TStructure", bound="BaseHashableStructure")
TElement = TypeVar("TElement")


def update_element_in_chunk(
    original_chunk: Hash32, index: int, element: bytes
) -> Hash32:
    element_size = len(element)
    chunk_size = len(original_chunk)
    if chunk_size % element_size != 0:
        raise ValueError(f"Element size is not a divisor of chunk size: {element_size}")
    if not 0 <= index < chunk_size // element_size:
        raise ValueError(f"Index out of range for element size {element_size}: {index}")

    first_byte_index = index * element_size
    last_byte_index = first_byte_index + element_size

    prefix = original_chunk[:first_byte_index]
    suffix = original_chunk[last_byte_index:]
    return Hash32(prefix + element + suffix)


def update_elements_in_chunk(
    original_chunk: Hash32, updated_elements: Dict[int, bytes]
) -> Hash32:
    return pipe(
        original_chunk,
        *(
            lambda chunk, index=index, element=element: update_element_in_chunk(
                chunk, index, element
            )
            for index, element in updated_elements.items()
        ),
    )


def get_updated_and_appended_chunks(
    updated_elements: Dict[int, bytes],
    appended_elements: List[bytes],
    original_chunks: Sequence[Hash32],
    num_original_elements: int,
) -> Tuple[Dict[int, Hash32], List[Hash32]]:
    if not updated_elements and not appended_elements:
        return {}, []

    try:
        some_element = next(iter(updated_elements.values()))
    except StopIteration:
        some_element = appended_elements[0]
    element_size = len(some_element)
    elements_per_chunk = CHUNK_SIZE // element_size

    # Find the elements whose chunk already exists. This is the case for all updated elements, but
    # possibly also for the first few appended elements (if the original last chunk was not filled
    # completely but zero-padded)
    padding_length = (
        len(original_chunks) * CHUNK_SIZE - num_original_elements * element_size
    )
    num_elements_in_padding = padding_length // element_size
    effective_updated_elements = {
        **updated_elements,
        **dict(
            enumerate(
                appended_elements[:num_elements_in_padding], start=num_original_elements
            )
        ),
    }

    # Compute the updated chunks
    element_indices = effective_updated_elements.keys()
    element_indices_by_chunk = groupby(
        lambda element_index: element_index // elements_per_chunk, element_indices
    )
    in_chunk_updates_by_chunk = {
        chunk_index: {
            element_index
            % elements_per_chunk: effective_updated_elements[element_index]
            for element_index in element_indices
        }
        for chunk_index, element_indices in element_indices_by_chunk.items()
    }
    updated_chunks = {
        chunk_index: update_elements_in_chunk(
            original_chunks[chunk_index], in_chunk_updates
        )
        for chunk_index, in_chunk_updates in in_chunk_updates_by_chunk.items()
    }

    # Compute appended chunks by packing the remaining elements
    chunk_partitioned_elements = partition(
        elements_per_chunk,
        appended_elements[num_elements_in_padding:],
        pad=b"\x00" * element_size,
    )
    appended_chunks = [
        Hash32(b"".join(elements)) for elements in chunk_partitioned_elements
    ]

    return updated_chunks, appended_chunks


class BaseHashableStructure(HashableStructureAPI[TElement]):
    def __init__(
        self,
        elements: PVector[TElement],
        hash_tree: HashTree,
        sedes: BaseCompositeSedes,
    ) -> None:
        self._elements = elements
        self._hash_tree = hash_tree
        self._sedes = sedes

        self._is_packing_cache: Optional[bool] = None

    @classmethod
    def from_iterable(
        cls: TStructure,
        iterable: Iterable[TElement],
        sedes: BaseCompositeSedes,
        limit: Optional[int],
    ) -> TStructure:

        # create an empty structure first to get access to some helpful instance methods
        minimal_hash_tree = HashTree.compute([ZERO_BYTES32], limit)
        hashable_structure_template = cls([], minimal_hash_tree, sedes)

        # now create the actual object
        elements = pvector(iterable)
        serialized_elements = [
            hashable_structure_template.serialize_element_for_tree(index, element)
            for index, element in enumerate(elements)
        ]
        updated_chunks, appended_chunks = get_updated_and_appended_chunks(
            {}, serialized_elements, minimal_hash_tree.chunks, 0
        )

        hash_tree = HashTree.compute(
            [updated_chunks.get(0, ZERO_BYTES32)] + appended_chunks, limit
        )
        return cls(elements, hash_tree, sedes)

    @property
    def elements(self) -> PVector[TElement]:
        return self._elements

    @property
    def hash_tree(self) -> HashTree:
        return self._hash_tree

    @property
    def chunks(self) -> PVector[Hash32]:
        return self.hash_tree.chunks

    @property
    def raw_root(self) -> Hash32:
        return self.hash_tree.root

    @property
    def sedes(self) -> BaseCompositeSedes:
        return self._sedes

    @property
    def is_packing(self) -> bool:
        if self._is_packing_cache is None:

            def has_basic_elements(sedes):
                return isinstance(sedes.element_sedes, BasicSedes)

            self._is_packing_cache = any(
                (
                    isinstance(self.sedes, Vector) and has_basic_elements(self.sedes),
                    isinstance(self.sedes, ListSedes)
                    and has_basic_elements(self.sedes),
                )
            )

        return self._is_packing_cache

    def serialize_element_for_tree(self, index: int, element: TElement) -> bytes:
        element_sedes = self.sedes.get_element_sedes(index)
        if self.is_packing:
            return ssz.encode(element, element_sedes)
        else:
            return ssz.get_hash_tree_root(element, element_sedes)

    #
    # PVector interface
    #
    def __len__(self) -> int:
        return len(self.elements)

    def __getitem__(self, index: int) -> TElement:
        return self.elements[index]

    def __iter__(self) -> Iterator[TElement]:
        return iter(self.elements)

    def transform(self, *transformations):
        return transform(self, transformations)

    def mset(self: TStructure, *args: Union[int, TElement]) -> TStructure:
        if len(args) % 2 != 0:
            raise TypeError(
                f"mset must be called with an even number of arguments, got {len(args)}"
            )

        evolver = self.evolver()
        for index, value in partition(2, args):
            evolver[index] = value
        return evolver.persistent()

    def set(self: TStructure, index: int, value: TElement) -> TStructure:
        return self.mset(index, value)

    def evolver(self: TStructure) -> "HashableStructureEvolverAPI[TStructure]":
        return HashableStructureEvolver(self)


class HashableStructureEvolver(HashableStructureEvolverAPI[TStructure]):
    def __init__(self, hashable_structure: TStructure) -> None:
        self._original_structure = hashable_structure
        self._updated_elements: Dict[int, Any] = {}
        # `self._appended_elements` is only used in the subclass ResizableHashableStructureEvolver,
        # but the implementation of `persistent` already processes it so that it does not have to
        # be implemented twice.
        self._appended_elements: List[Any] = []

    def __getitem__(self, index: int) -> Any:
        if index in self._updated_elements:
            return self._updated_elements[index]
        else:
            return self._original_structure[index]

    def set(self, index: int, element: Any) -> None:
        self[index] = element

    def __setitem__(self, index: int, element: Any) -> None:
        if 0 <= index < len(self):
            self._updated_elements[index] = element
        else:
            raise IndexError("Index out of bounds: {index}")

    def __len__(self) -> int:
        return len(self._original_structure)

    def is_dirty(self) -> bool:
        return bool(self._updated_elements or self._appended_elements)

    def persistent(self) -> TStructure:
        if not self.is_dirty():
            return self._original_structure

        updated_elements = {
            index: self._original_structure.serialize_element_for_tree(index, element)
            for index, element in self._updated_elements.items()
        }
        appended_elements = [
            self._original_structure.serialize_element_for_tree(index, element)
            for index, element in enumerate(
                self._appended_elements, start=len(self._original_structure)
            )
        ]
        updated_chunks, appended_chunks = get_updated_and_appended_chunks(
            updated_elements,
            appended_elements,
            self._original_structure.hash_tree.chunks,
            len(self._original_structure),
        )

        elements = self._original_structure.elements.mset(
            *itertools.chain(self._updated_elements.items())
        ).extend(self._appended_elements)
        hash_tree = self._original_structure.hash_tree.mset(
            *itertools.chain(*updated_chunks.items())
        ).extend(appended_chunks)

        return self._original_structure.__class__(
            elements, hash_tree, self._original_structure.sedes
        )


class BaseResizableHashableStructure(
    BaseHashableStructure, ResizableHashableStructureAPI[TElement]
):
    def append(self: TStructure, value: TElement) -> TStructure:
        evolver = self.evolver()
        evolver.append(value)
        return evolver.persistent()

    def extend(self: TStructure, values: Iterable[TElement]) -> TStructure:
        evolver = self.evolver()
        evolver.extend(values)
        return evolver.persistent()

    def __add__(self: TStructure, values: Iterable[TElement]) -> TStructure:
        return self.extend(values)

    def __mul__(self: TStructure, times: int) -> TStructure:
        if times < 0:
            raise ValueError("Multiplication factor must not be negative: {times}")
        elif times == 0:
            return None
        elif times == 1:
            return self
        else:
            return (self + self) * (times - 1)

    def evolver(self: TStructure) -> "ResizableHashableStructureEvolverAPI[TStructure]":
        return ResizableHashableStructureEvolver(self)


class ResizableHashableStructureEvolver(
    HashableStructureEvolver, ResizableHashableStructureEvolverAPI[TStructure]
):
    def append(self, element: Any) -> None:
        self._appended_elements.append(element)

    def extend(self, iterable: Iterable[Any]) -> None:
        self._appended_elements.extend(iterable)

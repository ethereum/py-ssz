import functools
import itertools
from typing import (
    Any,
    Dict,
    Generator,
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
from eth_utils import to_dict, to_tuple
from eth_utils.toolz import groupby, partition, pipe
from pyrsistent import pvector
from pyrsistent._transformations import transform
from pyrsistent.typing import PVector

from ssz.abc import (
    HashableStructureAPI,
    HashableStructureEvolverAPI,
    ResizableHashableStructureAPI,
    ResizableHashableStructureEvolverAPI,
)
from ssz.constants import CHUNK_SIZE, ZERO_BYTES32
from ssz.hash_tree import HashTree
from ssz.sedes.base import BaseProperCompositeSedes

TStructure = TypeVar("TStructure", bound="BaseHashableStructure")
TResizableStructure = TypeVar(
    "TResizableStructure", bound="BaseResizableHashableStructure"
)
TElement = TypeVar("TElement")


def update_element_in_chunk(
    original_chunk: Hash32, index: int, element: bytes
) -> Hash32:
    """Replace part of a chunk with a given element.

    The chunk is interpreted as a concatenated sequence of equally sized elements. This function
    replaces the element given by its index in the chunk with the given data.

    If the length of the element is zero or not a divisor of the chunk size, a `ValueError` is
    raised. If the index is out of range, an `IndexError is raised.

    Example:
        >>> update_element_in_chunk(b"aabbcc", 1, b"xx")
        b'aaxxcc'
    """
    element_size = len(element)
    chunk_size = len(original_chunk)

    if element_size == 0:
        raise ValueError(f"Element size is zero")
    if chunk_size % element_size != 0:
        raise ValueError(f"Element size is not a divisor of chunk size: {element_size}")
    if not 0 <= index < chunk_size // element_size:
        raise IndexError(f"Index out of range for element size {element_size}: {index}")

    first_byte_index = index * element_size
    last_byte_index = first_byte_index + element_size

    prefix = original_chunk[:first_byte_index]
    suffix = original_chunk[last_byte_index:]
    return Hash32(prefix + element + suffix)


def update_elements_in_chunk(
    original_chunk: Hash32, updated_elements: Dict[int, bytes]
) -> Hash32:
    """Update multiple elements in a chunk.

    The set of updates is given by a dictionary mapping indices to elements. The items of the
    dictionary will be passed one by one to `update_element_in_chunk`.
    """
    return pipe(
        original_chunk,
        *(
            functools.partial(update_element_in_chunk, index=index, element=element)
            for index, element in updated_elements.items()
        ),
    )


def get_num_padding_elements(
    *, num_original_elements: int, num_original_chunks: int, element_size: int
) -> int:
    """Compute the number of elements that would still fit in the empty space of the last chunk."""
    total_size = num_original_chunks * CHUNK_SIZE
    used_size = num_original_elements * element_size
    padding_size = total_size - used_size
    num_elements_in_padding = padding_size // element_size
    return num_elements_in_padding


@to_dict
def get_updated_chunks(
    *,
    updated_elements: Dict[int, bytes],
    appended_elements: Sequence[bytes],
    original_chunks: Sequence[Hash32],
    element_size: int,
    num_original_elements: int,
    num_padding_elements: int,
) -> Generator[Tuple[int, Hash32], None, None]:
    """For an element changeset, compute the updates that have to be applied to the existing chunks.

    The changeset is given as a dictionary of element indices to updated elements and a sequence of
    appended elements. Note that appended elements that do not affect existing chunks are ignored.

    The pre-existing state is given by the sequence of original chunks and the number of elements
    represented by these chunks.

    The return value is a dictionary mapping chunk indices to chunks.
    """
    effective_appended_elements = appended_elements[:num_padding_elements]
    elements_per_chunk = CHUNK_SIZE // element_size

    padding_elements_with_indices = dict(
        enumerate(effective_appended_elements, start=num_original_elements)
    )
    effective_updated_elements = {**updated_elements, **padding_elements_with_indices}

    element_indices = effective_updated_elements.keys()
    element_indices_by_chunk = groupby(
        lambda element_index: element_index // elements_per_chunk, element_indices
    )

    for chunk_index, element_indices in element_indices_by_chunk.items():
        chunk_updates = {
            element_index
            % elements_per_chunk: effective_updated_elements[element_index]
            for element_index in element_indices
        }
        updated_chunk = update_elements_in_chunk(
            original_chunks[chunk_index], chunk_updates
        )
        yield chunk_index, updated_chunk


@to_tuple
def get_appended_chunks(
    *, appended_elements: Sequence[bytes], element_size: int, num_padding_elements: int
) -> Generator[Hash32, None, None]:
    """Get the sequence of appended chunks."""
    if len(appended_elements) <= num_padding_elements:
        return

    elements_per_chunk = CHUNK_SIZE // element_size

    chunk_partitioned_elements = partition(
        elements_per_chunk,
        appended_elements[num_padding_elements:],
        pad=b"\x00" * element_size,
    )
    for elements_in_chunk in chunk_partitioned_elements:
        yield Hash32(b"".join(elements_in_chunk))


class BaseHashableStructure(HashableStructureAPI[TElement]):
    def __init__(
        self,
        elements: PVector[TElement],
        hash_tree: HashTree,
        sedes: BaseProperCompositeSedes,
        max_length: Optional[int] = None,
    ) -> None:
        self._elements = elements
        self._hash_tree = hash_tree
        self._sedes = sedes
        self._max_length = max_length

    @classmethod
    def from_iterable_and_sedes(
        cls,
        iterable: Iterable[TElement],
        sedes: BaseProperCompositeSedes,
        max_length: Optional[int] = None,
    ):
        elements = pvector(iterable)
        if max_length and len(elements) > max_length:
            raise ValueError(
                f"Number of elements {len(elements)} exceeds maximum length {max_length}"
            )

        serialized_elements = [
            sedes.serialize_element_for_tree(index, element)
            for index, element in enumerate(elements)
        ]
        appended_chunks = get_appended_chunks(
            appended_elements=serialized_elements,
            element_size=sedes.element_size_in_tree,
            num_padding_elements=0,
        )
        hash_tree = HashTree.compute(
            appended_chunks or [ZERO_BYTES32], sedes.chunk_count
        )
        return cls(elements, hash_tree, sedes, max_length)

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
    def max_length(self) -> Optional[int]:
        return self._max_length

    @property
    def raw_root(self) -> Hash32:
        return self.hash_tree.root

    @property
    def sedes(self) -> BaseProperCompositeSedes:
        return self._sedes

    #
    # Hash and equality
    #
    def __hash__(self) -> int:
        # hashable structures have the same hash if they share both sedes and root
        return hash((self.sedes, self.hash_tree_root))

    def __eq__(self, other: Any) -> bool:
        # hashable structures are equal if they use the same sedes and have the same root
        if isinstance(other, BaseHashableStructure):
            sedes_equal = self.sedes == other.sedes
            roots_equal = self.hash_tree_root == other.hash_tree_root
            return sedes_equal and roots_equal
        else:
            return False

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

    def evolver(
        self: TStructure
    ) -> "HashableStructureEvolverAPI[TStructure, TElement]":
        return HashableStructureEvolver(self)


class HashableStructureEvolver(HashableStructureEvolverAPI[TStructure, TElement]):
    def __init__(self, hashable_structure: TStructure) -> None:
        self._original_structure = hashable_structure
        self._updated_elements: Dict[int, TElement] = {}
        # `self._appended_elements` is only used in the subclass ResizableHashableStructureEvolver,
        # but the implementation of `persistent` already processes it so that it does not have to
        # be implemented twice.
        self._appended_elements: List[TElement] = []

    def __getitem__(self, index: int) -> TElement:
        if index < 0:
            index += len(self)

        if index in self._updated_elements:
            return self._updated_elements[index]
        elif 0 <= index < len(self._original_structure):
            return self._original_structure[index]
        elif 0 <= index < len(self):
            return self._appended_elements[index - len(self._original_structure)]
        else:
            raise IndexError(f"Index out of bounds: {index}")

    def set(self, index: int, element: TElement) -> None:
        self[index] = element

    def __setitem__(self, index: int, element: TElement) -> None:
        if index < 0:
            index += len(self)

        if 0 <= index < len(self._original_structure):
            self._updated_elements[index] = element
        elif 0 <= index < len(self):
            self._appended_elements[index - len(self._original_structure)] = element
        else:
            raise IndexError(f"Index out of bounds: {index}")

    def __len__(self) -> int:
        return len(self._original_structure) + len(self._appended_elements)

    def is_dirty(self) -> bool:
        return bool(self._updated_elements or self._appended_elements)

    def persistent(self) -> TStructure:
        if not self.is_dirty():
            return self._original_structure

        sedes = self._original_structure.sedes

        num_original_elements = len(self._original_structure)
        num_original_chunks = len(self._original_structure.chunks)
        num_padding_elements = get_num_padding_elements(
            num_original_elements=num_original_elements,
            num_original_chunks=num_original_chunks,
            element_size=sedes.element_size_in_tree,
        )

        updated_elements = {
            index: sedes.serialize_element_for_tree(index, element)
            for index, element in self._updated_elements.items()
        }
        appended_elements = [
            sedes.serialize_element_for_tree(index, element)
            for index, element in enumerate(
                self._appended_elements, start=num_original_elements
            )
        ]

        updated_chunks = get_updated_chunks(
            updated_elements=updated_elements,
            appended_elements=appended_elements,
            original_chunks=self._original_structure.chunks,
            num_original_elements=num_original_elements,
            num_padding_elements=num_padding_elements,
            element_size=sedes.element_size_in_tree,
        )
        appended_chunks = get_appended_chunks(
            appended_elements=appended_elements,
            element_size=sedes.element_size_in_tree,
            num_padding_elements=num_padding_elements,
        )

        elements = self._original_structure.elements.mset(
            *itertools.chain.from_iterable(  # type: ignore
                self._updated_elements.items()
            )
        ).extend(self._appended_elements)
        hash_tree = self._original_structure.hash_tree.mset(
            *itertools.chain.from_iterable(  # type: ignore
                updated_chunks.items()
            )
        ).extend(appended_chunks)

        return self._original_structure.__class__(
            elements, hash_tree, self._original_structure.sedes
        )


class BaseResizableHashableStructure(
    BaseHashableStructure, ResizableHashableStructureAPI[TElement]
):
    def append(self: TResizableStructure, value: TElement) -> TResizableStructure:
        evolver = self.evolver()
        evolver.append(value)
        return evolver.persistent()

    def extend(
        self: TResizableStructure, values: Iterable[TElement]
    ) -> TResizableStructure:
        evolver = self.evolver()
        evolver.extend(values)
        return evolver.persistent()

    def __add__(
        self: TResizableStructure, values: Iterable[TElement]
    ) -> TResizableStructure:
        return self.extend(values)

    def __mul__(self: TResizableStructure, times: int) -> TResizableStructure:
        if times <= 0:
            raise ValueError(f"Multiplication factor must be positive: {times}")
        elif times == 1:
            return self
        else:
            return (self + self) * (times - 1)

    def evolver(
        self: TResizableStructure,
    ) -> "ResizableHashableStructureEvolverAPI[TResizableStructure, TElement]":
        return ResizableHashableStructureEvolver(self)


class ResizableHashableStructureEvolver(
    HashableStructureEvolver, ResizableHashableStructureEvolverAPI[TStructure, TElement]
):
    def append(self, element: TElement) -> None:
        max_length = self._original_structure.max_length
        if max_length is not None and len(self) + 1 > max_length:
            raise ValueError(f"Structure would exceed maximum length {max_length}")
        self._appended_elements.append(element)

    def extend(self, elements: Iterable[TElement]) -> None:
        extension = list(elements)

        max_length = self._original_structure.max_length
        if max_length is not None and len(self) + len(extension) > max_length:
            raise ValueError(f"Structure would exceed maximum length {max_length}")

        self._appended_elements.extend(extension)

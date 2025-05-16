from typing import (
    TYPE_CHECKING,
    Iterable,
    Sequence,
    TypeVar,
)

from eth_typing import (
    Hash32,
)

from ssz.hashable_structure import (
    BaseResizableHashableStructure,
)
from ssz.utils import (
    mix_in_length,
)

TElement = TypeVar("TElement")

if TYPE_CHECKING:
    from ssz.sedes import (
        List,
    )


class HashableList(BaseResizableHashableStructure[TElement], Sequence[TElement]):
    @classmethod
    def from_iterable(
        cls, iterable: Iterable[TElement], sedes: "List[TElement, TElement]"
    ):
        return super().from_iterable_and_sedes(
            iterable, sedes, max_length=sedes.max_length
        )

    def __getitem__(self, index):
        # Handle both integer indices and slices to be compatible with Sequence
        if isinstance(index, int):
            return self.elements[index]
        elif isinstance(index, slice):
            return type(self).from_iterable(self.elements[index], self.sedes)
        else:
            raise TypeError(
                f"Indices must be integers or slices, not {type(index).__name__}"
            )

    @property
    def hash_tree_root(self) -> Hash32:
        return mix_in_length(self.raw_root, len(self))

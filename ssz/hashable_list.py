from typing import Iterable, Type

from eth_typing import Hash32
from pyrsistent import pvector

from ssz.hashable_structure import BaseHashableStructure
from ssz.sedes import BaseSedes, List
from ssz.utils import mix_in_length


class HashableList(BaseHashableStructure):
    @classmethod
    def from_iterable(
        cls: "Type[HashableList]",
        iterable: Iterable,
        element_sedes: BaseSedes,
        max_length: int,
    ) -> "HashableList":
        elements = pvector(iterable)

        if max_length <= 0:
            raise ValueError(f"List max length {max_length} is not positive")
        if len(elements) > max_length:
            raise ValueError(
                f"Number of elements {len(elements)} exceeds list max length {max_length}"
            )

        # TODO: check max length when changing list size? Partially, but not fully, checked during
        # chunk count check

        sedes = List(element_sedes, max_length)
        return super().from_iterable(elements, sedes)

    @property
    def root(self) -> Hash32:
        return mix_in_length(self.raw_root, len(self))

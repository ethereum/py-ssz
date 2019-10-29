from typing import Iterable, Type

from eth_typing import Hash32
from pyrsistent import pvector

from ssz.hashable_structure import BaseHashableStructure
from ssz.sedes import BaseSedes, Vector


class HashableVector(BaseHashableStructure):
    @classmethod
    def from_iterable(
        cls: "Type[HashableVector]", iterable: Iterable, element_sedes: BaseSedes
    ) -> "HashableVector":
        elements = pvector(iterable)
        sedes = Vector(element_sedes, len(elements))
        return super().from_iterable(elements, sedes)

    @property
    def root(self) -> Hash32:
        return self.raw_root

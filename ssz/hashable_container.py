from abc import ABC
from typing import Any, Dict

from eth_typing import Hash32

from ssz.hashable_structure import BaseHashableStructure
from ssz.sedes import Container


class HashableContainer(BaseHashableStructure, ABC):
    @classmethod
    def create(cls, **kwargs: Dict[str, Any]):
        try:
            field_names_and_sedes = cls.fields
        except AttributeError:
            raise TypeError("Type {cls} does not define fields")

        field_names, field_sedes = zip(*field_names_and_sedes)
        container = Container(field_sedes)
        elements = [kwargs[field_name] for field_name, _ in field_names_and_sedes]
        return cls.from_iterable(elements, container)

    @property
    def root(self) -> Hash32:
        return self.raw_root

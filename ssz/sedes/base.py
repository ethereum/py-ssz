from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, Tuple

from eth_typing import Hash32

from ssz.typing import CacheObj, TDeserialized, TSerializable


class BaseSedes(ABC, Generic[TSerializable, TDeserialized]):
    #
    # Size
    #
    @property
    @abstractmethod
    def is_fixed_sized(self) -> bool:
        ...

    @abstractmethod
    def get_fixed_size(self) -> int:
        ...

    #
    # Serialization
    #
    @abstractmethod
    def serialize(self, value: TSerializable) -> bytes:
        ...

    #
    # Deserialization
    #
    @abstractmethod
    def deserialize(self, data: bytes) -> TDeserialized:
        ...

    #
    # Tree hashing
    #
    @abstractmethod
    def get_hash_tree_root(self, value: TSerializable) -> Hash32:
        ...

    @abstractmethod
    def get_hash_tree_root_and_leaves(
        self, value: TSerializable, cache: CacheObj
    ) -> Tuple[Hash32, CacheObj]:
        ...

    @abstractmethod
    def get_sedes_id(self) -> str:
        ...

    @abstractmethod
    def get_key(self, value: Any) -> str:
        ...

    #
    # Equality and hashing
    #
    @abstractmethod
    def __hash__(self) -> int:
        ...

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        ...


TSedes = BaseSedes[Any, Any]


class BaseProperCompositeSedes(BaseSedes[TSerializable, TDeserialized]):
    @property
    @abstractmethod
    def is_packing(self) -> bool:
        ...

    @abstractmethod
    def get_element_sedes(self, index: int) -> BaseSedes:
        ...

    @property
    @abstractmethod
    def element_size_in_tree(self) -> int:
        ...

    @abstractmethod
    def serialize_element_for_tree(self, index: int, element: TSerializable) -> bytes:
        ...

    @property
    @abstractmethod
    def chunk_count(self) -> Optional[int]:
        ...


class BaseBitfieldCompositeSedes(BaseSedes[TSerializable, TDeserialized]):
    ...

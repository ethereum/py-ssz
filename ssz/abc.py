from abc import ABC, abstractmethod
from typing import Any, Generic, Iterable, Iterator, TypeVar, Union

from eth_typing import Hash32
from pyrsistent.typing import PVector

from ssz.hash_tree import HashTree

TStructure = TypeVar("TStructure")
TElement = TypeVar("TElement")


class HashableStructureAPI(ABC, Generic[TElement]):
    @property
    @abstractmethod
    def raw_root(self) -> Hash32:
        ...

    #
    # Element and hash tree access
    #
    @property
    @abstractmethod
    def elements(self) -> PVector[TElement]:
        ...

    @property
    @abstractmethod
    def chunks(self) -> PVector[Hash32]:
        ...

    @property
    @abstractmethod
    def hash_tree(self) -> HashTree:
        ...

    #
    # Partial PVector interface
    #
    @abstractmethod
    def __len__(self) -> int:
        ...

    @abstractmethod
    def __getitem__(self, index: int) -> TElement:
        ...

    @abstractmethod
    def __iter__(self) -> Iterator[TElement]:
        ...

    # @abstractmethod
    # def __hash__(self) -> int:
    #     ...

    # @abstractmethod
    # def __eq__(self, other: Any) -> bool:
    #     ...

    @abstractmethod
    def transform(self, *transformations):
        ...

    @abstractmethod
    def mset(self: TStructure, *args: Union[int, TElement]) -> TStructure:
        ...

    @abstractmethod
    def set(self: TStructure, index: int, value: TElement) -> TStructure:
        ...

    @abstractmethod
    def evolver(self: TStructure) -> "HashableStructureEvolverAPI[TStructure]":
        ...


class ResizableHashableStructureAPI(HashableStructureAPI[TElement]):
    @abstractmethod
    def append(self: TStructure, value: TElement) -> TStructure:
        ...

    @abstractmethod
    def extend(self: TStructure, values: Iterable[TElement]) -> TStructure:
        ...

    @abstractmethod
    def __add__(self: TStructure, values: Iterable[TElement]) -> TStructure:
        ...

    @abstractmethod
    def __mul__(self: TStructure, times: int) -> TStructure:
        ...

    @abstractmethod
    def evolver(self: TStructure) -> "ResizableHashableStructureEvolverAPI[TStructure]":
        ...


class HashableStructureEvolverAPI(ABC, Generic[TStructure]):
    @abstractmethod
    def __init__(self, hashable_structure: TStructure) -> None:
        ...

    @abstractmethod
    def __getitem__(self, index: int) -> Any:
        ...

    @abstractmethod
    def set(self, index: int, element: Any) -> None:
        ...

    @abstractmethod
    def __setitem__(self, index: int, element: Any) -> None:
        ...

    @abstractmethod
    def __len__(self) -> int:
        ...

    @abstractmethod
    def is_dirty(self) -> bool:
        ...

    @abstractmethod
    def persistent(self) -> TStructure:
        ...


class ResizableHashableStructureEvolverAPI(HashableStructureEvolverAPI[TStructure]):
    @abstractmethod
    def append(self, element: Any) -> None:
        ...

    @abstractmethod
    def extend(self, iterable: Iterable[Any]) -> None:
        ...

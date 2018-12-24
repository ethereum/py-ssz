from abc import (
    ABC,
    abstractmethod,
)


class BaseSSZSedes(ABC):

    @abstractmethod
    def serialize(self):
        raise NotImplementedError("SSZ Sedes classes must implement this property")

    @abstractmethod
    def deserialize(self):
        raise NotImplementedError("SSZ Sedes classes must implement this property")

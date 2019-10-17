from typing import NamedTuple, Optional, Tuple

import ssz
from ssz.constants import SIGNATURE_FIELD_NAME
from ssz.sedes.base import BaseSedes
from ssz.sedes.container import Container
from ssz.sedes.serializable import BaseSerializable, MetaSerializable


class SignedMeta(NamedTuple):
    has_fields: bool
    fields: Optional[Tuple[Tuple[str, BaseSedes]]]
    container_sedes: Optional[Container]
    signed_container_sedes: Optional[Container]
    field_names: Optional[Tuple[str, ...]]
    field_attrs: Optional[Tuple[str, ...]]


class MetaSignedSerializable(MetaSerializable):
    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)

        if cls._meta.has_fields:
            if len(cls._meta.fields) < 2:
                raise TypeError(
                    f"Signed serializables need to have at least two fields"
                )
            if cls._meta.field_names[-1] != SIGNATURE_FIELD_NAME:
                raise TypeError(
                    f"Last field of signed serializable must be {SIGNATURE_FIELD_NAME}, but is "
                    f"{cls._meta.field_names[-1]}"
                )

            signed_container_sedes = Container(
                cls._meta.container_sedes.field_sedes[:-1]
            )
        else:
            signed_container_sedes = None

        meta = SignedMeta(
            has_fields=cls._meta.has_fields,
            fields=cls._meta.fields,
            container_sedes=cls._meta.container_sedes,
            signed_container_sedes=signed_container_sedes,
            field_names=cls._meta.field_names,
            field_attrs=cls._meta.field_attrs,
        )
        cls._meta = meta

        return cls


BaseSedes.register(MetaSignedSerializable)


class SignedSerializable(BaseSerializable, metaclass=MetaSignedSerializable):
    @property
    def signing_root(self):
        return ssz.get_hash_tree_root(self, self._meta.signed_container_sedes)

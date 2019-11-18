from typing import IO, Any, Iterable, Sequence, Tuple

from eth_typing import Hash32
from eth_utils import ValidationError, to_tuple
from eth_utils.toolz import sliding_window

from ssz.exceptions import DeserializationError, SerializationError
from ssz.hashable_structure import BaseHashableStructure
from ssz.sedes.base import BaseSedes, TSedes
from ssz.sedes.basic import ProperCompositeSedes
from ssz.typing import CacheObj
from ssz.utils import merkleize, read_exact, s_decode_offset


@to_tuple
def _deserialize_fixed_size_items_and_offsets(stream, field_sedes):
    for sedes in field_sedes:
        if sedes.is_fixed_sized:
            field_size = sedes.get_fixed_size()
            field_data = read_exact(field_size, stream)
            yield (sedes.deserialize(field_data), sedes)
        else:
            yield (s_decode_offset(stream), sedes)


class Container(ProperCompositeSedes[Sequence[Any], Tuple[Any, ...]]):
    def __init__(self, field_sedes: Sequence[TSedes]) -> None:
        if len(field_sedes) == 0:
            raise ValidationError("Cannot define container without any fields")
        self.field_sedes = tuple(field_sedes)

    #
    # Size
    #
    @property
    def is_fixed_sized(self):
        return all(field.is_fixed_sized for field in self.field_sedes)

    def get_fixed_size(self):
        if not self.is_fixed_sized:
            raise ValueError("Container contains dynamically sized elements")

        return sum(field.get_fixed_size() for field in self.field_sedes)

    #
    # Serialization
    #
    def get_element_sedes(self, index: int) -> BaseSedes:
        return self.field_sedes[index]

    @property
    def is_packing(self) -> bool:
        return False

    @property
    def chunk_count(self) -> int:
        return len(self.field_sedes)

    def _validate_serializable(self, value: Sequence[Any]) -> None:
        if len(value) != len(self.field_sedes):
            raise SerializationError(
                f"Incorrect element count: Expected: {len(self.field_sedes)} / Got: {len(value)}"
            )

    #
    # Deserialization
    #
    def deserialize_fixed_size_parts(
        self, stream: IO[bytes]
    ) -> Iterable[Tuple[Tuple[Any], Tuple[int, TSedes]]]:
        fixed_items_and_offets = _deserialize_fixed_size_items_and_offsets(
            stream, self.field_sedes
        )
        fixed_size_values = tuple(
            item for item, sedes in fixed_items_and_offets if sedes.is_fixed_sized
        )
        offset_pairs = tuple(
            (item, sedes)
            for item, sedes in fixed_items_and_offets
            if not sedes.is_fixed_sized
        )
        return fixed_size_values, offset_pairs

    @to_tuple
    def deserialize_variable_size_parts(
        self, offset_pairs: Tuple[Tuple[int, TSedes], ...], stream: IO[bytes]
    ) -> Iterable[Any]:
        offsets, fields = zip(*offset_pairs)

        *head_fields, last_field = fields
        for sedes, (left_offset, right_offset) in zip(
            head_fields, sliding_window(2, offsets)
        ):
            field_length = right_offset - left_offset
            field_data = read_exact(field_length, stream)
            yield sedes.deserialize(field_data)

        # simply reading to the end of the current stream gives us all of the final element data
        final_field_data = stream.read()
        yield last_field.deserialize(final_field_data)

    def _deserialize_stream(self, stream: IO[bytes]) -> Tuple[Any, ...]:
        if not self.field_sedes:
            # TODO: likely remove once
            # https://github.com/ethereum/eth2.0-specs/issues/854 is resolved
            return tuple()

        fixed_size_values, offset_pairs = self.deserialize_fixed_size_parts(stream)

        if not offset_pairs:
            return fixed_size_values

        variable_size_values = self.deserialize_variable_size_parts(
            offset_pairs, stream
        )

        fixed_size_parts_iter = iter(fixed_size_values)
        variable_size_parts_iter = iter(variable_size_values)

        value = tuple(
            next(fixed_size_parts_iter)
            if sedes.is_fixed_sized
            else next(variable_size_parts_iter)
            for sedes in self.field_sedes
        )

        # Verify that both iterables have been fully consumed.
        try:
            next(fixed_size_parts_iter)
        except StopIteration:
            pass
        else:
            raise DeserializationError("Did not consume all fixed size values")

        try:
            next(variable_size_parts_iter)
        except StopIteration:
            pass
        else:
            raise DeserializationError("Did not consume all variable size values")

        return value

    #
    # Tree hashing
    #
    def get_hash_tree_root(self, value: Tuple[Any, ...]) -> bytes:
        if isinstance(value, BaseHashableStructure) and value.sedes == self:
            return value.hash_tree_root

        merkle_leaves = tuple(
            sedes.get_hash_tree_root(element)
            for element, sedes in zip(value, self.field_sedes)
        )
        return merkleize(merkle_leaves)

    def get_hash_tree_root_and_leaves(
        self, value: Tuple[Any, ...], cache: CacheObj
    ) -> Tuple[Hash32, CacheObj]:
        merkle_leaves = ()
        for element, sedes in zip(value, self.field_sedes):
            key = sedes.get_key(element)
            if key not in cache:
                if hasattr(sedes, "get_hash_tree_root_and_leaves"):
                    root, cache = sedes.get_hash_tree_root_and_leaves(element, cache)
                    cache[key] = root
                else:
                    cache[key] = sedes.get_hash_tree_root(element)

            merkle_leaves += (cache[key],)

        return merkleize(merkle_leaves), cache

    def serialize(self, value) -> bytes:
        if hasattr(value, "_serialize_cache") and value._serialize_cache is not None:
            return value._serialize_cache
        elif hasattr(value, "_serialize_cache") and value._serialize_cache is None:
            value._serialize_cache = super().serialize(value)
            return value._serialize_cache
        else:
            return super().serialize(value)

    def get_sedes_id(self) -> str:
        return ",".join(field.get_sedes_id() for field in self.field_sedes)

    #
    # Equality and hashing
    #
    def __hash__(self) -> int:
        return hash((hash(Container), hash(self.field_sedes)))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Container) and other.field_sedes == self.field_sedes

from ssz.hashable_container import HashableContainer, SignedHashableContainer
from ssz.sedes import (
    Bitlist,
    Bitvector,
    List,
    Vector,
    boolean,
    bytes32,
    bytes48,
    bytes96,
    uint64,
)


class ClockInRecords(SignedHashableContainer):
    fields = [
        ("epoch", uint64),
        ("bio_id_scan", bytes32),
        ("poo_log_bits", Bitlist(32)),
        ("wash_log_bits", Bitvector(32)),
        ("signature", bytes96),
    ]


class Animal(HashableContainer):
    fields = [
        ("id_hash", bytes32),
        ("public_key", bytes48),
        ("clock_in_records", List(ClockInRecords, 2**32)),
        ("vaccinated", boolean),
    ]


class Zoo(HashableContainer):
    fields = [("animals", Vector(Animal, 3))]


octopus = Animal.create(
    id_hash=b"\xab" * 32,
    public_key=b"\xab" * 48,
    clock_in_records=(
        ClockInRecords.create(
            epoch=123,
            bio_id_scan=b"\xab" * 32,
            signature=b"\xab" * 96,
            poo_log_bits=(True,) * 16 + (False,) * 16,
            wash_log_bits=(False,) * 16 + (True,) * 16,
        ),
        ClockInRecords.create(
            epoch=124,
            bio_id_scan=b"\xab" * 32,
            signature=b"\xab" * 96,
            poo_log_bits=(True,) * 16 + (False,) * 16,
            wash_log_bits=(False,) * 16 + (True,) * 16,
        ),
    ),
    vaccinated=True,
)
corgi = Animal.create(
    id_hash=b"\xcd" * 32,
    public_key=b"\xcd" * 48,
    clock_in_records=(
        ClockInRecords.create(
            epoch=125,
            bio_id_scan=b"\xcd" * 32,
            signature=b"\xcd" * 96,
            poo_log_bits=(True,) * 16 + (False,) * 16,
            wash_log_bits=(False,) * 16 + (True,) * 16,
        ),
    ),
    vaccinated=True,
)

bunny = Animal.create(
    id_hash=b"\xef" * 32, public_key=b"\xef" * 48, clock_in_records=(), vaccinated=False
)

zoo = Zoo.create(animals=(octopus, corgi, bunny))

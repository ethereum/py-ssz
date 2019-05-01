from ssz.sedes import (
    List,
    Serializable,
    SignedSerializable,
    Vector,
    boolean,
    byte_list,
    bytes32,
    bytes48,
    bytes96,
    uint64,
)


class ClockInRecords(SignedSerializable):
    fields = [
        ('epoch', uint64),
        ('bio_id_scan', byte_list),
        ('signature', bytes96),
    ]


class Animal(Serializable):
    fields = [
        ('id_hash', bytes32),
        ('public_key', bytes48),
        ('clock_in_records', List(ClockInRecords)),
        ('vaccinated', boolean),
    ]


class Zoo(Serializable):
    fields = [
        ('animals', Vector(Animal, 3)),
    ]


octopus = Animal(
    id_hash=b'\xab' * 32,
    public_key=b'\xab' * 48,
    clock_in_records=(
        ClockInRecords(
            epoch=123,
            bio_id_scan=b'\xab' * 16,
            signature=b'\xab' * 96,
        ),
        ClockInRecords(
            epoch=124,
            bio_id_scan=b'\xab' * 16,
            signature=b'\xab' * 96,
        )
    ),
    vaccinated=True,
)
corgi = Animal(
    id_hash=b'\xcd' * 32,
    public_key=b'\xcd' * 48,
    clock_in_records=(
        ClockInRecords(
            epoch=125,
            bio_id_scan=b'\xcd' * 16,
            signature=b'\xcd' * 96,
        ),
    ),
    vaccinated=True,
)

bunny = Animal(
    id_hash=b'\xef' * 32,
    public_key=b'\xef' * 48,
    clock_in_records=(),
    vaccinated=False,
)

zoo = Zoo(animals=(octopus, corgi, bunny))

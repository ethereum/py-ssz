from ssz.sedes import (
    List,
    Serializable,
    Vector,
    boolean,
    bytes32,
    bytes48,
    uint64,
)

SHARDCOUNT = 10


class Validator(Serializable):
    fields = [
        ('pubkey', bytes48),
        ('withdrawal_credentials', bytes32),
        ('exit_epoch', uint64),
        ('slashed', boolean),
    ]


class Crosslink(Serializable):
    fields = [
        ('slot', uint64),
        ('shard_block_root', bytes32),
    ]


class State(Serializable):
    fields = [
        ('validator_registry', List(Validator)),
        ('current_crosslinks', Vector(Crosslink, SHARDCOUNT))
    ]


validator = Validator(
    pubkey=b'\x56' * 48,
    withdrawal_credentials=b'\x56' * 32,
    exit_epoch=123,
    slashed=False,
)
crosslink = Crosslink(slot=12847, shard_block_root=b'\x67' * 32)
crosslink_record_stubs = [crosslink for i in range(SHARDCOUNT)]

state = State(
    validator_registry=tuple(validator for i in range(5)),
    current_crosslinks=crosslink_record_stubs,
)

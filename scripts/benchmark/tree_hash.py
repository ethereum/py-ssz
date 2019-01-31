import time

from ssz import (
    hash_tree_root,
)
from ssz.sedes import (
    List,
    Serializable,
    bytes32,
    uint24,
    uint64,
    uint384,
)

TOLERABLE_PERFORMANCE = 15  # Seconds


class ValidatorRecord(Serializable):
    fields = [
        ('pubkey', uint384),
        ('withdrawal_credentials', bytes32),
        ('randao_commitment', bytes32),
        ('randao_layers', uint64),
        ('status', uint64),
        ('latest_status_change_slot', uint64),
        ('exit_count', uint64),
        ('poc_commitment', bytes32),
        ('last_poc_change_slot', uint64),
        ('second_last_poc_change_slot', uint64),
    ]


class CrosslinkRecord(Serializable):
    fields = [
        ('slot', uint64),
        ('shard_block_root', bytes32),
    ]


class ShardCommittee(Serializable):
    fields = [
        ('shard', uint64),
        ('committee', List(uint24)),
        ('total_validator_count', uint64),
    ]


class State(Serializable):
    fields = [
        ('validator_registry', List(ValidatorRecord)),
        ('shard_and_committee_for_slots', List(List(ShardCommittee))),
        ('latest_crosslinks', List(CrosslinkRecord)),
    ]


validator_record = ValidatorRecord(
    pubkey=123,
    withdrawal_credentials=b'\x56' * 32,
    randao_commitment=b'\x56' * 32,
    randao_layers=123,
    status=123,
    latest_status_change_slot=123,
    exit_count=123,
    poc_commitment=b'\x56' * 32,
    last_poc_change_slot=123,
    second_last_poc_change_slot=123,
)
crosslink_record = CrosslinkRecord(slot=12847, shard_block_root=b'\x67' * 32)
crosslink_record_stubs = [crosslink_record for i in range(1024)]


def make_state(num_validators):
    shard_committee = ShardCommittee(
        shard=1,
        committee=tuple(range(num_validators // 1024)),
        total_validator_count=num_validators,
    )
    shard_committee_stubs = tuple(tuple(shard_committee for i in range(16)) for i in range(64))
    state = State(
        validator_registry=tuple(validator_record for i in range(num_validators)),
        shard_and_committee_for_slots=shard_committee_stubs,
        latest_crosslinks=crosslink_record_stubs,
    )
    return state


def run():
    state = make_state(2**18)

    start_time = time.time()

    hash_tree_root(state)

    actual_performance = time.time() - start_time

    print("Performance of hash_tree_root", actual_performance)

    if actual_performance > TOLERABLE_PERFORMANCE:
        raise TimeoutError("hash_tree_root is not fast enough. Tolerable: {}, Actual: {}".format(
            TOLERABLE_PERFORMANCE,
            actual_performance,
        ))


if __name__ == '__main__':
    run()

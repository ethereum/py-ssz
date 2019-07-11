import time

from ssz import (
    encode,
)
from ssz.sedes import (
    List,
    Serializable,
    bytes32,
    bytes48,
    uint32,
    uint64,
)


class ValidatorRecord(Serializable):
    fields = [
        ('pubkey', bytes48),
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
        ('committee', List(uint32, 2**32)),
        ('total_validator_count', uint64),
    ]


class State(Serializable):
    fields = [
        ('validator_registry', List(ValidatorRecord, 2**32)),
        ('shard_and_committee_for_slots', List(List(ShardCommittee, 2**32), 2**32)),
        ('latest_crosslinks', List(CrosslinkRecord, 2**32)),
    ]


validator_record = ValidatorRecord(
    pubkey=b'\x56' * 48,
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


def do_test_serialize(state, rounds=100):
    for _ in range(rounds):
        x = encode(state, cache=True)
    return x


def do_test_serialize_no_cache(state, rounds=100):
    for _ in range(rounds):
        x = encode(state, cache=False)

    return x


def test_encode_cache():
    state = make_state(2**10)

    start_time = time.time()
    without_cache_result = do_test_serialize_no_cache(state)
    without_cache_actual_performance = time.time() - start_time
    print("Performance of serialization without cache", without_cache_actual_performance)

    state = make_state(2**10)
    start_time = time.time()
    with_cache_result = do_test_serialize(state)
    with_cache_actual_performance = time.time() - start_time
    print("Performance of serialization with cache", with_cache_actual_performance)

    assert with_cache_result == without_cache_result
    assert with_cache_actual_performance * 10 < without_cache_actual_performance

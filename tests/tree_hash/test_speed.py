import time

from ssz.sedes import (
    List,
    Serializable,
    bytes32,
    uint24,
    uint64,
    uint384,
)
from ssz.tree_hash import (
    hash_tree_root,
)


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


def do_test_tree_hash_not_cache(state, rounds=100):
    for _ in range(rounds):
        result = hash_tree_root(state, cache=False)
    return result


def do_test_tree_hash_cache(state, rounds=100):
    for _ in range(rounds):
        result = hash_tree_root(state, cache=True)
    return result


def test_tree_hash_cache():
    state = make_state(2**10)

    start_time = time.time()
    without_cache_result = do_test_tree_hash_not_cache(state)
    without_cache_actual_performance = time.time() - start_time
    print("Performance of serialization without cache", without_cache_actual_performance)

    state = make_state(2**10)
    start_time = time.time()
    with_cache_result = do_test_tree_hash_cache(state)
    with_cache_actual_performance = time.time() - start_time
    print("Performance of serialization with cache", with_cache_actual_performance)

    assert with_cache_result == without_cache_result
    assert with_cache_actual_performance * 10 < without_cache_actual_performance

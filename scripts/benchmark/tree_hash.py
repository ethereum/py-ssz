import cProfile
import random
import time

import ssz
from ssz.sedes import (
    List,
    Serializable,
    ByteVector,
    byte_list,
    bytes32,
    bytes48,
    uint32,
    uint64,
)

random.seed(0)

do_profiling = False
TOLERABLE_PERFORMANCE = 15  # Seconds


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
        ('committee', List(uint32)),
        ('total_validator_count', uint64),
    ]


class State(Serializable):
    fields = [
        ('validator_registry', List(ValidatorRecord)),
        ('shard_and_committee_for_slots', List(List(ShardCommittee))),
        ('latest_crosslinks', List(CrosslinkRecord)),
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


def prepare_byte_vector_benchmark():
    size = 512
    repetitions = 10000
    byte_vector = ByteVector(size)
    data = tuple(
        bytes(random.getrandbits(8) for _ in range(size))
        for _ in range(repetitions)
    )

    def benchmark():
        for data_item in data:
            ssz.hash_tree_root(data_item, byte_vector)

    return benchmark


def prepare_byte_list_benchmark():
    size_range = (0, 1000)
    repetitions = 10000

    sizes = tuple(random.randint(*size_range) for _ in range(repetitions))
    data = tuple(
        bytes(random.getrandbits(8) for _ in range(size))
        for size in sizes
    )

    def benchmark():
        for data_item in data:
            ssz.hash_tree_root(data_item, byte_list)

    return benchmark


def prepare_state_benchmark():
    state = make_state(2**15)

    def benchmark():
        ssz.hash_tree_root(state)

    return benchmark


if __name__ == '__main__':
    benchmarks = {
        # "byte_vector": prepare_byte_vector_benchmark(),
        # "byte_list": prepare_byte_list_benchmark(),
        "state": prepare_state_benchmark(),
    }
    results = {}

    for name, benchmark in benchmarks.items():
        if do_profiling:
            profile = cProfile.Profile()
            profile.enable()

        start_time = time.time()
        benchmark()
        end_time = time.time()

        if do_profiling:
            profile.disable()
            profile.print_stats(sort="tottime")

        duration = end_time - start_time
        results[name] = duration
        print(f"{name}: {duration:.2f}s")

    if "state" not in results:
        raise RuntimeError("state benchmark has not been run")
    elif results["state"] > TOLERABLE_PERFORMANCE:
        raise TimeoutError("hash_tree_root is not fast enough. Tolerable: {}, Actual: {}".format(
            TOLERABLE_PERFORMANCE,
            results["state"],
        ))

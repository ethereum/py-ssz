import cProfile
import io
import pstats
import random
import time

import ssz
from ssz.cache.cache import (
    SSZCache,
)
from ssz.sedes import (
    List,
    Serializable,
    Vector,
    boolean,
    bytes32,
    bytes48,
    bytes96,
    uint64,
)

random.seed(0)

do_profiling = True

TOLERABLE_PERFORMANCE = 15  # Seconds

VALIDATOR_REGISTRY_LIMIT = 2**40  # (= 1,099,511,627,776)
EPOCHS_PER_HISTORICAL_VECTOR = 2**16  # (= 65,536)

FAR_FUTURE_EPOCH = 0

USE_SSZ_CACHE = True


class BeaconBlockHeader(ssz.SignedSerializable):

    fields = [
        ('slot', uint64),
        ('parent_root', bytes32),
        ('state_root', bytes32),
        ('body_root', bytes32),
        ('signature', bytes96),
    ]


class Eth1Data(ssz.Serializable):

    fields = [
        ('deposit_root', bytes32),
        ('deposit_count', uint64),
        ('block_hash', bytes32),
    ]

    def __init__(self,
                 deposit_root,
                 deposit_count,
                 block_hash) -> None:
        super().__init__(
            deposit_root=deposit_root,
            deposit_count=deposit_count,
            block_hash=block_hash,
        )


class Validator(ssz.Serializable):
    fields = [
        ('pubkey', bytes48),
        ('withdrawal_credentials', bytes32),
        ('effective_balance', uint64),
        ('slashed', boolean),
        # Epoch when validator became eligible for activation
        ('activation_eligibility_epoch', uint64),
        # Epoch when validator activated
        ('activation_epoch', uint64),
        # Epoch when validator exited
        ('exit_epoch', uint64),
        # Epoch when validator withdrew
        ('withdrawable_epoch', uint64),
    ]

    @classmethod
    def create_validator(cls, pubkey, withdrawal_credentials):
        return cls(
            pubkey=pubkey,
            withdrawal_credentials=withdrawal_credentials,
            effective_balance=0,
            slashed=False,
            activation_eligibility_epoch=FAR_FUTURE_EPOCH,
            activation_epoch=FAR_FUTURE_EPOCH,
            exit_epoch=FAR_FUTURE_EPOCH,
            withdrawable_epoch=FAR_FUTURE_EPOCH,
        )


class State(Serializable):
    fields = [
        ('validators', List(Validator, VALIDATOR_REGISTRY_LIMIT)),
        ('balances', List(uint64, VALIDATOR_REGISTRY_LIMIT)),
        ('randao_mixes', Vector(bytes32, EPOCHS_PER_HISTORICAL_VECTOR)),
        ('latest_block_header', BeaconBlockHeader),
        ('eth1_data', Eth1Data),
    ]


def update_tuple_item_with_fn(tuple_data,
                              index,
                              fn,
                              *args):
    """
    Update the ``index``th item of ``tuple_data`` to the result of calling ``fn`` on the existing
    value.
    """
    list_data = list(tuple_data)

    try:
        old_value = list_data[index]
        list_data[index] = fn(old_value, *args)
    except IndexError:
        raise Exception(
            "the length of the given tuple_data is {}, the given index {} is out of index".format(
                len(tuple_data),
                index,
            )
        )
    else:
        return tuple(list_data)


def update_tuple_item(tuple_data,
                      index,
                      new_value):
    """
    Update the ``index``th item of ``tuple_data`` to ``new_value``
    """
    return update_tuple_item_with_fn(
        tuple_data,
        index,
        lambda *_: new_value
    )


def make_state(num_validators):
    state = State(
        validators=tuple(
            Validator.create_validator(
                pubkey=i.to_bytes(48, 'little'),
                withdrawal_credentials=i.to_bytes(32, 'little'),
            )
            for i in range(num_validators)
        ),
        balances=tuple(
            i + 1000
            for i in range(num_validators)
        ),
        randao_mixes=tuple(
            i.to_bytes(32, 'little')
            for i in range(EPOCHS_PER_HISTORICAL_VECTOR)
        ),
        latest_block_header=BeaconBlockHeader(
            slot=1,
            parent_root=b'\x22' * 32,
            state_root=b'\x22' * 32,
            body_root=b'\x22' * 32,
            signature=b'\x55' * 96,
        ),
        eth1_data=Eth1Data(
            deposit_root=b'\x12' * 32,
            deposit_count=1,
            block_hash=b'\x12' * 32,
        ),
        cache=SSZCache() if USE_SSZ_CACHE else None,
    )
    return state


def prepare_state_benchmark():
    num_validators = 2**13
    state = make_state(num_validators)
    print('state.hash_tree_root\t', state.hash_tree_root.hex())
    index = 100
    block_header = BeaconBlockHeader(
        slot=1,
        parent_root=b'\x22' * 32,
        state_root=b'\x22' * 32,
        body_root=b'\x22' * 32,
        signature=b'\x66' * 96,
    )

    def benchmark():
        print('----- start -----')
        oh_state = state.copy(
            balances=update_tuple_item(
                state.balances,
                index,
                state.balances[index] + 10,
            ),
            validators=update_tuple_item(
                state.validators,
                index,
                Validator.create_validator(
                    pubkey=(666).to_bytes(48, 'little'),
                    withdrawal_credentials=(666).to_bytes(32, 'little'),
                ),
            ),
            randao_mixes=update_tuple_item(
                state.randao_mixes,
                index,
                b'\x56' * 32,
            ),
            latest_block_header=block_header,
            eth1_data=Eth1Data(
                deposit_root=b'\x22' * 32,
                deposit_count=1,
                block_hash=b'\x22' * 32,
            ),
        )
        print('updated\t', oh_state.hash_tree_root.hex())
        print('----- end -----')

    return benchmark


if __name__ == '__main__':
    benchmarks = {
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
            s = io.StringIO()
            ps = pstats.Stats(profile, stream=s).sort_stats('tottime')
            ps.print_stats()
            print(s.getvalue())
            ps.dump_stats('hash_tree_root.pstats')

        duration = end_time - start_time
        results[name] = duration
        print(f"{name}: {duration:.4f}s")

    if "state" not in results:
        raise RuntimeError("state benchmark has not been run")
    elif results["state"] > TOLERABLE_PERFORMANCE:
        raise TimeoutError("hash_tree_root is not fast enough. Tolerable: {}, Actual: {}".format(
            TOLERABLE_PERFORMANCE,
            results["state"],
        ))

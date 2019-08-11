import functools


def get_key(sedes, value):
    key = _get_key(sedes, value).hex()
    if len(key) > 0:
        sedes_name = type(sedes).__name__
        return sedes_name + _get_key(sedes, value).hex()
    else:
        return key


@functools.lru_cache(maxsize=2**10, typed=False)
def _get_key(sedes, value):
    return sedes.serialize(value)

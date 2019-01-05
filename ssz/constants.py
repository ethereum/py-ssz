BYTES_PREFIX_LENGTH = 4
# This constant was added here for optimization of calculating below value only once
MAX_LEN_SERIALIZED_BYTES_OBJECT = 2 ** (BYTES_PREFIX_LENGTH * 8)

CONTAINER_PREFIX_LENGTH = 4
# This constant was added here for optimization of calculating below value only once
MAX_LEN_SERIALIZED_CONTAINER_OBJECT = 2 ** (CONTAINER_PREFIX_LENGTH * 8)

LIST_PREFIX_LENGTH = 4
# This constant was added here for optimization of calculating below value only once
MAX_LEN_SERIALIZED_LIST_OBJECT = 2 ** (LIST_PREFIX_LENGTH * 8)

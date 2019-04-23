import json
from typing import (
    Any,
)

from ruamel.yaml import (
    YAML,
)
from ruamel.yaml.compat import (
    StringIO,
)

from ssz.sedes import (
    Serializable,
    infer_sedes,
)
from ssz.sedes.base import (
    BaseSedes,
)


def encode_text(value: Serializable):
    sedes_obj = infer_sedes(value)
    return sedes_obj.serialize_text(value)


def decode_text(content: Any, sedes: BaseSedes) -> Serializable:
    return sedes.deserialize_text(content)


def to_json(value: Serializable) -> str:
    return json.dumps(encode_text(value), indent=4)


def from_json(content: Any, sedes: BaseSedes) -> str:
    return decode_text(json.loads(content), sedes)


def to_yaml(value: Serializable) -> str:
    class CustomYAML(YAML):
        def dump(self, data, stream=None, **kw):
            inefficient = False
            if stream is None:
                inefficient = True
                stream = StringIO()
            YAML.dump(self, data, stream, **kw)
            if inefficient:
                return stream.getvalue()
    yaml = CustomYAML()
    return yaml.dump(encode_text(value))


def from_yaml(content: Any, sedes: BaseSedes) -> str:
    yaml = YAML()
    return decode_text(yaml.load(content), sedes)

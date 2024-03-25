import pytest

import ssz
from ssz.sedes import (
    uint8,
)


def create_inheritance_structure(structure):
    class_definitions = tuple(definition.strip() for definition in structure.split())

    class_dict = {}
    field_names_dict = {}

    for index, class_definition in enumerate(class_definitions):
        # get the name of the class
        class_name_start = 0
        class_name_end = class_definition.index("(")
        class_name = class_definition[class_name_start:class_name_end]
        assert class_name.isalpha(), "invalid class definition"

        # get the names of the parent classes
        parent_names_start = class_name_end + 1
        parent_names_end = class_definition.index(")")
        if parent_names_start == parent_names_end:
            parent_names = ()
        else:
            parent_names = class_definition[parent_names_start:parent_names_end].split(
                ","
            )

        assert all(
            parent_name in class_dict for parent_name in parent_names
        ), "invalid class definition"

        # define fields if necessary and figure out expected argument names
        class_defines_fields = class_definition.endswith("*")
        if class_defines_fields:
            field_names = (f"field{index}",)
            namespace = {
                "fields": tuple((field_name, uint8) for field_name in field_names)
            }
        else:
            parent_field_names = tuple(
                field_names_dict[parent_name]
                for parent_name in parent_names
                if field_names_dict[parent_name]
            )

            if not parent_field_names:
                field_names = ()
            else:
                field_names = parent_field_names[0]
            namespace = {}

        # create the class
        if not parent_names:
            parents = (ssz.Serializable,)
        else:
            parents = tuple(class_dict[parent_name] for parent_name in parent_names)
        class_dict[class_name] = type(class_name, parents, namespace)
        field_names_dict[class_name] = field_names

    return class_dict, field_names_dict


@pytest.mark.parametrize(
    "structure",
    (
        "A()",
        "A()*",
        "A()  B(A)",
        "A()  B(A)*",
        "A()* B(A)",
        "A()* B(A)*",
        "A()  B()  C(A,B)",
        "A()  B()  C(A,B)*",
        "A()* B()  C(A,B)",
        "A()* B()  C(A,B)*",
        "A()  B()* C(A,B)",
        "A()  B()* C(A,B)*",
        "A()* B()* C(A,B)*",
        "A()  B(A)  C(A)  D(B,C)",
        "A()  B(A)* C(A)  D(B,C)",
        "A()  B(A)  C(A)* D(B,C)",
        "A()  B(A)  C(A)  D(B,C)*",
        "A()* B(A)* C(A)  D(B,C)*",
        "A()* B(A)  C(A)* D(B,C)*",
        "A()* B(A)  C(A)  D(B,C)*",
    ),
)
def test_valid_inheritance(structure):
    class_dict, field_names_dict = create_inheritance_structure(structure)

    for class_name in class_dict.keys():
        class_ = class_dict[class_name]
        field_names = field_names_dict[class_name]

        kwargs = {field_name: 0 for field_name in field_names}
        instance = class_(**kwargs)
        for field_name in field_names:
            assert hasattr(instance, field_name)


@pytest.mark.parametrize(
    "structure",
    (
        "A()* B()* C(A,B)",
        "A()  B(A)* C(A)* D(B,C)",
        "A()* B(A)  C(A)  D(B,C)",
        "A()* B(A)* C(A)  D(B,C)",
        "A()* B(A)  C(A)* D(B,C)",
        "A()* B(A)* C(A)* D(B,C)",
    ),
)
def test_invalid_inheritance(structure):
    with pytest.raises(TypeError):
        create_inheritance_structure(structure)

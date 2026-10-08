import pytest
from kb.client import KBClient

REQUIRED_METHODS = ["search", "list_documents", "retrieve", "add"]


def make_client_class(methods):
    namespace = {name: (lambda self, *args, **kwargs: None) for name in methods}
    return type(KBClient)("TestClient", (KBClient,), namespace)


@pytest.mark.parametrize("missing", REQUIRED_METHODS)
def test_client_missing_a_method_cannot_be_created(missing):
    methods = [name for name in REQUIRED_METHODS if name != missing]
    client_class = make_client_class(methods)

    with pytest.raises(TypeError):
        client_class()


def test_client_with_all_methods_can_be_created():
    client_class = make_client_class(REQUIRED_METHODS)

    client_class()
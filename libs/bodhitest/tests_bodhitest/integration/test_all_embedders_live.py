import pytest
from bodhilib import Embedder, get_embedder

from tests_bodhitest.all_data import bodhiext_embedders


@pytest.fixture
def embedder_service(request):
    service_name = bodhiext_embedders[request.param]["service_name"]
    service_class = bodhiext_embedders[request.param]["service_class"]
    service_args = bodhiext_embedders[request.param]["service_args"]
    return get_embedder(service_name, oftype=service_class, **service_args)


@pytest.mark.live
@pytest.mark.parametrize("embedder_service", bodhiext_embedders.keys(), indirect=True)
def test_all_embedders_embeds_given_inputs(embedder_service: Embedder):
    nodes = list(embedder_service.embed(["foo", "bar"]))
    assert len(nodes) == 2
    assert len(nodes[0].embedding) == embedder_service.dimension
    assert len(nodes[1].embedding) == embedder_service.dimension

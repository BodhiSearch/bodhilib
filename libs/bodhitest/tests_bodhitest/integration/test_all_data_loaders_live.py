import pytest
from bodhilib import ResourceQueue, get_resource_queue

from tests_bodhitest.all_data import bodhiext_resource_queue


@pytest.fixture
def data_loader_service(request):
  data_loader = request.param
  params = bodhiext_resource_queue[data_loader]
  service_name = params["service_name"]
  service_class = params["service_class"]
  return get_resource_queue(service_name=service_name, oftype=service_class)


@pytest.fixture
def happypath_args(request):
  data_loader = request.param
  return bodhiext_resource_queue[data_loader]["happypath"]


@pytest.mark.live
@pytest.mark.parametrize(
  ["data_loader_service", "happypath_args"],
  [(key, key) for key in bodhiext_resource_queue.keys()],
  indirect=["data_loader_service", "happypath_args"],
)
def test_all_data_loaders_live_happypath(data_loader_service: ResourceQueue, happypath_args):
  try:
    happypath_args["setup"]()
    data_loader_service.push(files=happypath_args["resources"])
    nodes = data_loader_service.load()
    assert len(nodes) == len(happypath_args["text"])
    assert [node.text for node in nodes] == happypath_args["text"]
  finally:
    happypath_args["teardown"]()

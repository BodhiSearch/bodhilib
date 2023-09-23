from unittest.mock import MagicMock

import pytest
from bodhilib import Service, VectorDBError, list_vector_dbs

from tests_bodhitest.all_data import bodhiext_vector_dbs


@pytest.fixture
def service_class(request):
    return bodhiext_vector_dbs[request.param]["service_class"]


@pytest.fixture
def vector_db_params(request):
    return bodhiext_vector_dbs[request.param]


@pytest.mark.parametrize("service_class", bodhiext_vector_dbs.keys(), indirect=True)
def test_all_vector_db_calls_client_for_close(service_class):
    mock_client = MagicMock()
    vector_db = service_class(client=mock_client)
    assert vector_db.close() is True
    mock_client.close.assert_called_once()


@pytest.mark.parametrize("service_class", bodhiext_vector_dbs.keys(), indirect=True)
def test_all_vector_db_close_bubbles_client_error(service_class):
    mock_client = MagicMock()
    mock_client.close.side_effect = ValueError("test exception")
    vector_db = service_class(client=mock_client)
    with pytest.raises(VectorDBError) as e:
        _ = vector_db.close()
    assert str(e.value) == "test exception"
    mock_client.close.assert_called_once()


@pytest.mark.parametrize("service_class", bodhiext_vector_dbs.keys(), indirect=True)
def test_all_vector_db_ping(service_class):
    mock_client = MagicMock()
    vector_db = service_class(client=mock_client)
    assert vector_db.ping() is True


@pytest.mark.parametrize("service_class", bodhiext_vector_dbs.keys(), indirect=True)
def test_all_vector_db_connect(service_class):
    mock_client = MagicMock()
    vector_db = service_class(client=mock_client)
    assert vector_db.connect() is True


@pytest.mark.parametrize("vector_db_params", bodhiext_vector_dbs.keys(), indirect=True)
def test_all_vector_dbs_list_vector_dbs(vector_db_params):
    service_name, service_builder, publisher, version = (
        vector_db_params["service_name"],
        vector_db_params["service_builder"],
        vector_db_params["publisher"],
        vector_db_params["version"],
    )
    services = list_vector_dbs()
    assert (
        Service(
            service_name=service_name,
            service_type="vector_db",
            publisher=publisher,
            service_builder=service_builder,
            version=version,
        )
        in services
    )

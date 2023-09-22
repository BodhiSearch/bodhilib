from unittest.mock import MagicMock

import pytest
from bodhilib import Service, VectorDBError, get_vector_db, list_vector_dbs

from tests_bodhitest.components import bodhiext_vector_dbs, unwrap_vector_db


@pytest.fixture
def vector_db_class(request):
    return bodhiext_vector_dbs[request.param]["vector_db_class"]


@pytest.fixture
def vector_db_params(request):
    return bodhiext_vector_dbs[request.param]


@pytest.mark.parametrize("vector_db_class", bodhiext_vector_dbs.keys(), indirect=True)
def test_all_vector_db_calls_client_for_close(vector_db_class):
    mock_client = MagicMock()
    vector_db = vector_db_class(client=mock_client)
    assert vector_db.close() is True
    mock_client.close.assert_called_once()


@pytest.mark.parametrize("vector_db_class", bodhiext_vector_dbs.keys(), indirect=True)
def test_all_vector_db_close_bubbles_client_error(vector_db_class):
    mock_client = MagicMock()
    mock_client.close.side_effect = ValueError("test exception")
    vector_db = vector_db_class(client=mock_client)
    with pytest.raises(VectorDBError) as e:
        _ = vector_db.close()
    assert str(e.value) == "test exception"
    mock_client.close.assert_called_once()


@pytest.mark.parametrize("vector_db_class", bodhiext_vector_dbs.keys(), indirect=True)
def test_all_vector_db_ping(vector_db_class):
    mock_client = MagicMock()
    vector_db = vector_db_class(client=mock_client)
    assert vector_db.ping() is True


@pytest.mark.parametrize("vector_db_class", bodhiext_vector_dbs.keys(), indirect=True)
def test_all_vector_db_connect(vector_db_class):
    mock_client = MagicMock()
    vector_db = vector_db_class(client=mock_client)
    assert vector_db.connect() is True


@pytest.mark.parametrize("vector_db_params", bodhiext_vector_dbs.keys(), indirect=True)
def test_all_vector_db_get_vector_db(vector_db_params):
    service_name, _, vector_db_class, _, _ = unwrap_vector_db(vector_db_params)
    service = get_vector_db(service_name)
    assert isinstance(service, vector_db_class)


@pytest.mark.parametrize("vector_db_params", bodhiext_vector_dbs.keys(), indirect=True)
def test_all_vector_dbs_list_vector_dbs(vector_db_params):
    service_name, service_builder, _, publisher, version = unwrap_vector_db(vector_db_params)
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

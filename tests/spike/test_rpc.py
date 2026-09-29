"""Deterministic unit tests for RPC observation fetching and error distinction."""

import pytest
import httpx
from konsyra.spike.models import FetchFailure, SlotAbsent, SlotObservation
from konsyra.spike.rpc import fetch_slot_observation


def test_fetch_slot_observation_success(monkeypatch):
    def mock_query(rpc_url, method, params):
        return {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "blockhash": "Blockhash123",
                "parentSlot": 99,
                "blockTime": 1700000000,
                "signatures": ["sig1", "sig2"],
            },
        }

    monkeypatch.setattr("konsyra.spike.rpc.query_rpc_json", mock_query)
    res = fetch_slot_observation("http://mock-rpc", "source-a", 100)

    assert isinstance(res, SlotObservation)
    assert res.slot == 100
    assert res.blockhash == "Blockhash123"
    assert res.transaction_signatures == {"sig1", "sig2"}


def test_fetch_slot_observation_slot_absent_null(monkeypatch):
    def mock_query(rpc_url, method, params):
        return {"jsonrpc": "2.0", "id": 1, "result": None}

    monkeypatch.setattr("konsyra.spike.rpc.query_rpc_json", mock_query)
    res = fetch_slot_observation("http://mock-rpc", "source-a", 100)

    assert isinstance(res, SlotAbsent)
    assert res.slot == 100
    assert res.reason == "RESULT_NULL"


@pytest.mark.parametrize("code,message", [
    (-32007, "Slot 100 was skipped or not available"),
    (-32004, "Block not available"),
    (-32600, "not found"),
    (-32600, "skipped"),
])
def test_rpc_absence_like_errors_preserve_unresolved_evidence(monkeypatch, code, message):
    monkeypatch.setattr("konsyra.spike.rpc.query_rpc_json", lambda *args: {
        "error": {"code": code, "message": message}
    })
    result = fetch_slot_observation("http://mock-rpc", "source-a", 100)
    assert result == FetchFailure("source-a", 100, "RPC_ERROR", message, code)


def test_fetch_slot_observation_fetch_failure_rpc_error(monkeypatch):
    def mock_query(rpc_url, method, params):
        return {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {"code": -32600, "message": "Invalid Request"},
        }

    monkeypatch.setattr("konsyra.spike.rpc.query_rpc_json", mock_query)
    res = fetch_slot_observation("http://mock-rpc", "source-a", 100)

    assert isinstance(res, FetchFailure)
    assert res.error_type == "RPC_ERROR"
    assert res.code == -32600


def test_fetch_slot_observation_fetch_failure_network(monkeypatch):
    def mock_query(rpc_url, method, params):
        raise httpx.ConnectError("Connection refused")

    monkeypatch.setattr("konsyra.spike.rpc.query_rpc_json", mock_query)
    res = fetch_slot_observation("http://mock-rpc", "source-a", 100)

    assert isinstance(res, FetchFailure)
    assert res.error_type == "NETWORK_ERROR"
    assert "Connection refused" in res.message


@pytest.mark.parametrize("error", [RuntimeError("programming failure"), TypeError("bad type")])
def test_unexpected_python_exception_propagates(monkeypatch, error):
    def mock_query(*args):
        raise error
    monkeypatch.setattr("konsyra.spike.rpc.query_rpc_json", mock_query)
    with pytest.raises(type(error)) as caught:
        fetch_slot_observation("http://mock-rpc", "source-a", 100)
    assert caught.value is error


def test_http_status_error_is_not_network_error(monkeypatch):
    request = httpx.Request("POST", "http://mock-rpc")
    response = httpx.Response(503, request=request)
    def mock_query(*args):
        raise httpx.HTTPStatusError("Unavailable", request=request, response=response)
    monkeypatch.setattr("konsyra.spike.rpc.query_rpc_json", mock_query)
    result = fetch_slot_observation("http://mock-rpc", "source-a", 100)
    assert result == FetchFailure("source-a", 100, "HTTP_ERROR", "Unavailable", 503)

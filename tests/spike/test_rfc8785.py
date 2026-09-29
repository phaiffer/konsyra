"""Focused RFC 8785 (JCS) conformance and numeric safety tests for Konsyra."""

import pytest
import rfc8785
from konsyra.spike.models import CheckResult, Divergence
from konsyra.spike.report import (
    build_canonical_payload,
    canonicalize_payload,
    compute_payload_sha256,
)


def assert_no_floats(obj: object, path: str = "$") -> None:
    """Recursively validates that a payload structure contains no float values."""
    if isinstance(obj, float):
        raise AssertionError(f"Float value found in canonical payload at {path}: {obj}")
    elif isinstance(obj, dict):
        for key, val in obj.items():
            assert_no_floats(val, path=f"{path}.{key}")
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            assert_no_floats(item, path=f"{path}[{idx}]")


def test_rfc8785_object_property_ordering():
    obj1 = {"b": 2, "a": 1}
    obj2 = {"a": 1, "b": 2}
    canonical1 = rfc8785.dumps(obj1)
    canonical2 = rfc8785.dumps(obj2)
    assert canonical1 == b'{"a":1,"b":2}'
    assert canonical2 == b'{"a":1,"b":2}'


def test_rfc8785_whitespace_independence():
    obj = {"key2": "val2", "key1": "val1", "list": [1, 2, 3]}
    canonical = rfc8785.dumps(obj)
    assert b" " not in canonical
    assert b"\n" not in canonical
    assert canonical == b'{"key1":"val1","key2":"val2","list":[1,2,3]}'


def test_rfc8785_unicode_encoding():
    obj = {"network": "solana_☀️", "status": "Válid"}
    canonical = rfc8785.dumps(obj)
    assert canonical == '{"network":"solana_☀️","status":"Válid"}'.encode("utf-8")
    assert b"\\u" not in canonical


def test_rfc8785_primitives():
    obj = {
        "null_val": None,
        "bool_true": True,
        "bool_false": False,
        "integer_val": 42,
        "string_val": "konsyra",
        "array_val": [1, "two", False, None],
        "object_val": {"nested": 1},
    }
    canonical = rfc8785.dumps(obj)
    expected = b'{"array_val":[1,"two",false,null],"bool_false":false,"bool_true":true,"integer_val":42,"null_val":null,"object_val":{"nested":1},"string_val":"konsyra"}'
    assert canonical == expected


def test_rfc8785_nested_objects():
    nested1 = {"z": {"d": 4, "c": 3}, "a": {"b": 2, "a": 1}}
    nested2 = {"a": {"a": 1, "b": 2}, "z": {"c": 3, "d": 4}}
    assert rfc8785.dumps(nested1) == rfc8785.dumps(nested2)
    assert rfc8785.dumps(nested1) == b'{"a":{"a":1,"b":2},"z":{"c":3,"d":4}}'


def test_rfc8785_integer_range_limits():
    max_safe_int = 2**53 - 1  # 9007199254740991
    min_safe_int = -(2**53 - 1)  # -9007199254740991

    assert rfc8785.dumps(max_safe_int) == b"9007199254740991"
    assert rfc8785.dumps(min_safe_int) == b"-9007199254740991"

    out_of_range_pos = 2**53  # 9007199254740992
    out_of_range_neg = -(2**53)  # -9007199254740992

    with pytest.raises(rfc8785.CanonicalizationError):
        rfc8785.dumps(out_of_range_pos)

    with pytest.raises(rfc8785.CanonicalizationError):
        rfc8785.dumps(out_of_range_neg)


def test_rfc8785_invalid_numeric_values():
    for invalid_val in [float("nan"), float("inf"), float("-inf")]:
        with pytest.raises(rfc8785.CanonicalizationError):
            rfc8785.dumps(invalid_val)


def test_konsyra_report_contains_no_floats():
    sources = [
        {"source_id": "source_a", "provider_name": "Alchemy"},
        {"source_id": "source_b", "provider_name": "QuickNode"},
    ]
    check = CheckResult(
        check_type="RECONCILIATION",
        status="FAIL",
        summary="Found 1 divergence",
        evidence=[
            Divergence(
                slot=300000000,
                source_a_id="source_a",
                source_b_id="source_b",
                source_a_signature_count=3,
                source_b_signature_count=2,
                missing_in_source_a=[],
                missing_in_source_b=["sig_x"],
            ).to_dict()
        ],
    )
    payload = build_canonical_payload(300000000, 300000005, sources, "FAIL", [check])
    assert_no_floats(payload)


def test_frozen_konsyra_canonicalization_vector():
    sources = [
        {"source_id": "source_a", "provider_name": "Alchemy"},
        {"source_id": "source_b", "provider_name": "QuickNode"},
    ]
    check = CheckResult(
        check_type="RECONCILIATION",
        status="FAIL",
        summary="Found 1 divergence",
        evidence=[
            Divergence(
                slot=100,
                source_a_id="source_a",
                source_b_id="source_b",
                source_a_signature_count=3,
                source_b_signature_count=2,
                missing_in_source_a=[],
                missing_in_source_b=["sig_x"],
            ).to_dict()
        ],
    )

    payload = build_canonical_payload(100, 105, sources, "FAIL", [check])

    expected_bytes = (
        b'{"checks":[{"check_type":"RECONCILIATION",'
        b'"evidence":[{"missing_in_source_a":[],"missing_in_source_b":["sig_x"],'
        b'"slot":100,"source_a_id":"source_a","source_a_signature_count":3,'
        b'"source_b_id":"source_b","source_b_signature_count":2}],'
        b'"status":"FAIL","summary":"Found 1 divergence"}],'
        b'"evidence":[{"missing_in_source_a":[],"missing_in_source_b":["sig_x"],'
        b'"slot":100,"source_a_id":"source_a","source_a_signature_count":3,'
        b'"source_b_id":"source_b","source_b_signature_count":2}],'
        b'"network":"solana","quality_status":"FAIL",'
        b'"report_schema_version":"0.1.0",'
        b'"sources":[{"provider_name":"Alchemy","source_id":"source_a"},'
        b'{"provider_name":"QuickNode","source_id":"source_b"}],'
        b'"validation_range":{"end_slot":105,"start_slot":100},'
        b'"validator_version":"0.1.0-alpha"}'
    )
    expected_digest = "285debe97ab5b90a2233daa877696dd359d12571684beea97be32122e8b6757f"

    canonical_bytes = canonicalize_payload(payload)
    digest = compute_payload_sha256(payload)

    assert canonical_bytes == expected_bytes
    assert digest == expected_digest
    assert len(digest) == 64

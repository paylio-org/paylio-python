from __future__ import annotations

import pytest

from paylio._paylio_object import PaylioObject


class TestDictAccess:
    def test_get_value(self) -> None:
        obj = PaylioObject({"status": "active"})
        assert obj["status"] == "active"

    def test_set_value(self) -> None:
        obj = PaylioObject()
        obj["name"] = "test"
        assert obj["name"] == "test"

    def test_missing_key_raises_key_error(self) -> None:
        obj = PaylioObject()
        with pytest.raises(KeyError):
            _ = obj["missing"]


class TestAttrAccess:
    def test_get_value(self) -> None:
        obj = PaylioObject({"status": "active"})
        assert obj.status == "active"

    def test_set_value(self) -> None:
        obj = PaylioObject()
        obj.name = "test"
        assert obj["name"] == "test"
        assert obj.name == "test"

    def test_missing_attr_raises_attribute_error(self) -> None:
        obj = PaylioObject()
        with pytest.raises(AttributeError, match="has no attribute 'nonexistent'"):
            _ = obj.nonexistent

    def test_private_attr_raises_attribute_error(self) -> None:
        """Accessing undefined private attrs raises AttributeError."""
        obj = PaylioObject({"status": "active"})
        with pytest.raises(AttributeError, match="has no attribute '_secret'"):
            _ = obj._secret

    def test_private_attr_setattr(self) -> None:
        """Private attrs go to object __dict__, not into the dict."""
        obj = PaylioObject({"id": "123"})
        obj._internal = "private"
        assert obj._internal == "private"
        assert "_internal" not in obj  # not in the dict

    def test_delattr_public_key(self) -> None:
        """del obj.key removes the key from the dict."""
        obj = PaylioObject({"status": "active", "plan": "pro"})
        del obj.status
        assert "status" not in obj
        with pytest.raises(AttributeError, match="has no attribute 'status'"):
            _ = obj.status

    def test_delattr_private_key(self) -> None:
        """del obj._private removes the private attribute."""
        obj = PaylioObject()
        obj._temp = "value"
        assert obj._temp == "value"
        del obj._temp
        with pytest.raises(AttributeError):
            _ = obj._temp


class TestInit:
    def test_kwargs_constructor(self) -> None:
        """PaylioObject(status='active', name='Pro') works like a dict."""
        obj = PaylioObject(status="active", name="Pro")
        assert obj.status == "active"
        assert obj.name == "Pro"
        assert obj["status"] == "active"

    def test_empty_constructor(self) -> None:
        obj = PaylioObject()
        assert len(obj) == 0

    def test_none_data_constructor(self) -> None:
        obj = PaylioObject(None)
        assert len(obj) == 0


class TestNestedObjects:
    def test_nested_dict_becomes_paylio_object(self) -> None:
        obj = PaylioObject({"plan": {"name": "Pro", "amount": 999}})
        assert isinstance(obj.plan, PaylioObject)
        assert obj.plan.name == "Pro"
        assert obj.plan.amount == 999

    def test_nested_list_items(self) -> None:
        obj = PaylioObject(
            {
                "items": [
                    {"id": "sub_1", "status": "active"},
                    {"id": "sub_2", "status": "canceled"},
                ]
            }
        )
        assert len(obj.items) == 2
        assert isinstance(obj.items[0], PaylioObject)
        assert obj.items[0].id == "sub_1"
        assert obj.items[1].status == "canceled"

    def test_list_with_non_dict_items(self) -> None:
        obj = PaylioObject({"tags": ["a", "b", "c"]})
        assert obj.tags == ["a", "b", "c"]

    def test_paylio_object_in_list_not_rewrapped(self) -> None:
        """Existing PaylioObject instances in lists are preserved, not re-wrapped."""
        inner = PaylioObject({"id": "inner_1"})
        obj = PaylioObject({"items": [inner]})
        assert obj.items[0] is inner

    def test_paylio_object_not_rewrapped(self) -> None:
        """Existing PaylioObject passed as a value is preserved, not re-wrapped."""
        inner = PaylioObject({"nested": True})
        obj = PaylioObject({"child": inner})
        assert obj.child is inner

    def test_plain_value_passthrough(self) -> None:
        """Non-dict, non-list values are passed through as-is."""
        obj = PaylioObject({"count": 42, "active": True, "rate": 3.14})
        assert obj.count == 42
        assert obj.active is True
        assert obj.rate == 3.14


class TestToDict:
    def test_flat(self) -> None:
        obj = PaylioObject({"id": "123", "status": "active"})
        result = obj.to_dict()
        assert result == {"id": "123", "status": "active"}
        assert type(result) is dict

    def test_nested(self) -> None:
        obj = PaylioObject({"plan": {"name": "Pro"}, "items": [{"id": "1"}]})
        result = obj.to_dict()
        assert result == {"plan": {"name": "Pro"}, "items": [{"id": "1"}]}
        assert type(result["plan"]) is dict
        assert type(result["items"][0]) is dict

    def test_to_dict_with_non_object_list_items(self) -> None:
        """to_dict handles lists that contain plain values."""
        obj = PaylioObject({"tags": ["a", "b"]})
        result = obj.to_dict()
        assert result == {"tags": ["a", "b"]}


class TestRepr:
    def test_with_id(self) -> None:
        obj = PaylioObject({"id": "sub_abc"})
        r = repr(obj)
        assert r == "<PaylioObject id=sub_abc>"

    def test_without_id(self) -> None:
        obj = PaylioObject({"status": "active"})
        r = repr(obj)
        assert "PaylioObject" in r
        assert "status" in r


class TestConstructFrom:
    def test_construct_from_creates_object(self) -> None:
        obj = PaylioObject.construct_from({"id": "test", "status": "active"})
        assert isinstance(obj, PaylioObject)
        assert obj.id == "test"
        assert obj.status == "active"

    def test_construct_from_wraps_nested(self) -> None:
        obj = PaylioObject.construct_from({"plan": {"name": "Pro"}})
        assert isinstance(obj.plan, PaylioObject)
        assert obj.plan.name == "Pro"

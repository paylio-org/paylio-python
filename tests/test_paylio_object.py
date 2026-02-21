from __future__ import annotations

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
        try:
            _ = obj["missing"]
            assert False, "should have raised KeyError"
        except KeyError:
            pass


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
        try:
            _ = obj.nonexistent
            assert False, "should have raised AttributeError"
        except AttributeError:
            pass


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


class TestRepr:
    def test_with_id(self) -> None:
        obj = PaylioObject({"id": "sub_abc"})
        assert "id=sub_abc" in repr(obj)

    def test_without_id(self) -> None:
        obj = PaylioObject({"status": "active"})
        r = repr(obj)
        assert "PaylioObject" in r

    def test_construct_from(self) -> None:
        obj = PaylioObject.construct_from({"id": "test", "status": "active"})
        assert obj.id == "test"
        assert obj.status == "active"

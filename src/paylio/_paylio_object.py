from __future__ import annotations

from typing import Any


class PaylioObject(dict):  # type: ignore[type-arg]
    """Base class for Paylio API response objects.

    Supports both dict-style and attribute-style access:
        obj["status"]  # dict access
        obj.status     # attribute access
    """

    def __init__(self, data: dict[str, Any] | None = None, **kwargs: Any) -> None:
        super().__init__()
        if data:
            self._init_from_dict(data)
        if kwargs:
            self._init_from_dict(kwargs)

    def _init_from_dict(self, data: dict[str, Any]) -> None:
        for key, value in data.items():
            dict.__setitem__(self, key, self._wrap(value))

    @staticmethod
    def _wrap(value: Any) -> Any:
        if isinstance(value, dict):
            return PaylioObject(value)
        if isinstance(value, list):
            return [PaylioObject(item) if isinstance(item, dict) else item for item in value]
        return value

    def __getattribute__(self, name: str) -> Any:
        # Prioritize dict keys over dict methods (e.g. "items" key vs dict.items()).
        if not name.startswith("_"):
            try:
                return dict.__getitem__(self, name)
            except KeyError:
                pass
        return super().__getattribute__(name)

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            self[name] = value

    def __delattr__(self, name: str) -> None:
        if name.startswith("_"):
            super().__delattr__(name)
        else:
            del self[name]

    def __repr__(self) -> str:
        ident = self.get("id")
        if ident:
            return f"<{type(self).__name__} id={ident}>"
        return f"<{type(self).__name__} {dict.__repr__(self)}>"

    def to_dict(self) -> dict[str, Any]:
        """Convert to a plain dict, recursively."""
        result: dict[str, Any] = {}
        for key, value in dict.items(self):
            if isinstance(value, PaylioObject):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [
                    item.to_dict() if isinstance(item, PaylioObject) else item for item in value
                ]
            else:
                result[key] = value
        return result

    @classmethod
    def construct_from(cls, data: dict[str, Any]) -> PaylioObject:
        """Construct a PaylioObject from API response data."""
        return cls(data)

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Dict, Optional


class FyooResource:
    __resource_types: Dict[str, type] = {}

    def __init__(self, value: Optional[str] = None) -> None:
        self.identifier = value if value else self.name
        self.opened = False

    @abstractmethod
    def open(self, **config) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError()

    @property
    @classmethod
    @abstractmethod
    def name(cls) -> str:
        raise NotImplementedError()

    def __init_subclass__(cls) -> None:
        if not hasattr(cls, 'name'):
            raise ValueError(f'{cls} should have a name')
        cls_name = getattr(cls, 'name')
        if cls_name in FyooResource.__resource_types:
            if FyooResource.__resource_types[cls_name] is not cls:
                raise ValueError(
                    f'Duplicate name {cls_name} for classes {cls} and {FyooResource.__resource_types[cls_name]}')
        else:
            FyooResource.__resource_types[cls_name] = cls

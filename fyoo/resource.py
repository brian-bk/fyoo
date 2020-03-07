from __future__ import annotations
from abc import abstractmethod
import functools
from typing import Any, Callable, Dict, Optional


class FyooResource:
    """The abstract FyooResource class.

    Subclasses of FyooResources
    must implement :attr:`name`, :meth:`open`, and :meth:`close`.

    Example class implementing FyooResource:

    .. code-block:: python

        class FileWriterFyooResource(FyooResource):
            name = 'mine'

            def open(self, filename, **config) -> TextIO:
                return open(filename, 'w')

            def close(self, file: TextIO) -> None:
                file.close()

    Attributes:
        name: Class abstract attribute, must be unique
        identifier: Unique identifier of an instantiated FyooResource
        opened: Whether the FyooResource is actively opened
    Args:
        value (Optional[str]): If no value is provided, :attr:`identifier` will
            default to :attr:`name`. Otherwise :attr:`identifier` will be
            set to the provided value.
    """

    __resource_types: Dict[str, type] = {}

    def __init__(self, value: Optional[str] = None) -> None:
        self.identifier: str = value if value else self.name
        self.opened: bool = False
        self._asset: Optional[Any] = None

    @abstractmethod
    def open(self, **config: Dict[str, Any]) -> Any:
        """Subclasses must implement an open method.

        The returned value will typically be a connection or
        client. It will be provided to a Flow function as
        a keyword argument.

        Args:
            **config (Dict[str, Any]): The configuration dictionary from the ``fyoo.ini`` file
            for this resource.

        Returns:
            Any: The connection, client, or file resource.
        """
        raise NotImplementedError('FyooResource.open() is not implemented')

    @abstractmethod
    def close(self, asset: Optional[Any]) -> None:
        """Subclasses must implement a close method.

        This method should close the connection, client, or file.

        Args:
            asset (Optional[Any]): The returned value from :attr:`open`.

        Returns:
            None
        """
        raise NotImplementedError('FyooResource.close() is not implemented')

    @property
    @classmethod
    @abstractmethod
    def name(cls) -> str:
        raise NotImplementedError('FyooResource.name is not implemented')

    @classmethod
    def _open_decorator(cls, open_func: Callable):
        """This decorator wraps around the open function.

        It stores the connection/client/file in :attr:`_asset`
        and set :attr:`opened` to ``True``.

        Args:
            open_func (Callable): The sub-class's open function.

        Raises:
            RuntimeError: Attempting to open an already opened instantiated
            FyooResource

        Returns:
            Callable: The decorated open function.
        """
        @functools.wraps(open_func)
        def wrapped_func(self, **config) -> Callable:
            if self.opened:
                raise RuntimeError(f'Tried to double-open {self}')
            returned_value = open_func(self, **config)
            self._asset = returned_value  # pylint: disable=protected-access
            self.opened = True
            return returned_value
        return wrapped_func

    @classmethod
    def _close_decorator(cls, close_func: Callable):
        """This decorator wraps around the close function.

        It provides the stored :attr:`_asset` to the close function
        and sets :attr:`opened` to ``False``. If the instantiated
        FyooResource is already closed, this function does nothing.

        Args:
            close_func (Callable): The sub-class's close function.

        Returns:
            Callable: The decorated close function.
        """
        @functools.wraps(close_func)
        def wrapped_func(self, _asset: Optional[Any] = None):
            if not self.opened:
                return None
            asset = self._asset  # pylint: disable=protected-access
            returned_value = close_func(self, asset)
            self.opened = False
            return returned_value
        return wrapped_func

    def __init_subclass__(cls) -> None:
        """Store all FyooResource subclasses and decorate implemented functions.

        We have to decorate at subclass init time, because we don't
        want to just decorate the abstract methods.

        Raises:
            ValueError: If ``cls`` does name have a ``name`` attribute,
            or if there are duplicate different sub-classes with the same
            ``name`` attribute.
        """
        if not hasattr(cls, 'name'):
            raise ValueError(f'{cls} should have a name')
        cls_name = getattr(cls, 'name')
        if cls_name in FyooResource.__resource_types:
            if FyooResource.__resource_types[cls_name] is not cls:
                raise ValueError(
                    f'Duplicate name {cls_name} for classes {cls} and {FyooResource.__resource_types[cls_name]}')
        else:
            cls.open = cls._open_decorator(cls.open)
            cls.close = cls._close_decorator(cls.close)
            FyooResource.__resource_types[cls_name] = cls

from fyoo.resource import FyooResource


class DummyResource(FyooResource):
    name = 'dummy'

    def open(self, **config) -> str:
        return self.identifier

    def close(self, asset: str) -> None:
        pass

from fyoo.resource import FyooResource


class DummyResource(FyooResource):
    name = 'dummy'

    def open(self, **config):
        return self.identifier

    def close(self):
        pass

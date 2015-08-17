class Property(object):
    description = ''
    types = []

    def __init__(self, thing):
        self.count = 0
        self.thing = thing

    def destroy(self):
        pass

    @classmethod
    def key(cls):
        return str(cls)

    def clone(self, new_thing=None):
        output = self.__class__(new_thing or self.thing)
        output.__dict__ = dict(self.__dict__)
        return output

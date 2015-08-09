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

    def clone(self, new_thing):
        output = self.__class__(new_thing)
        output.description = self.description
        output.types = self.types
        output.count = self.count
        return output

class Action(object):
    @classmethod
    def describe(cls, thing):
        return "Do something?"

    @classmethod
    def can_perform(self, performer):
        return False

    @classmethod
    def perform(self, *args, **kwargs):
        pass

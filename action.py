class Action(object):
    prereq = None

    @classmethod
    def describe(cls, thing):
        return "Do something?"

    @classmethod
    def can_perform(self, thing, performer):
        return True

    @classmethod
    def perform(self, *args, **kwargs):
        pass

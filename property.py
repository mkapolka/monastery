class Property(object):
    description = ''
    types = []

    def __init__(self, thing):
        self.count = 0
        self.thing = thing
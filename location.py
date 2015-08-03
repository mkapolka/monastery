class Location(object):
    def __init__(self):
        self.things = []
        self._name = 'Nowhere in particular'
        # Static exits for rooms
        self.exits = []

    def __repr__(self):
        return '<Location:"%s">' % self.name

    def can_contain(self, thing):
        return True

    def add_thing(self, thing):
        if thing.location is not None:
            thing.location.things.remove(thing)

        if object not in self.things:
            self.things.append(thing)
        thing.location = self

    def get_all_exits(self):
        """ Static and property exits """
        result = []
        result.extend(self.exits)
        for thing in self.things:
            for lp in thing.location_properties:
                result.extend(lp.entrances)
        return result

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value


class PropertyLocation(Location):
    """ For locations implanted within properties """
    def __init__(self, prop):
        super(PropertyLocation, self).__init__()
        self.thing = prop.thing
        self.prop = prop

    def can_contain(self, thing):
        return thing.size < self.thing.size

    @property
    def name(self):
        return self.name_template % {
            'thing_name': self.thing.name,
            'prop': self.prop
        }


class Exit(object):
    def __init__(self):
        self.description_template = 'To %(to_location)s'

    @property
    def description(self):
        return self.description_template % self._get_description_parameters()

    def _get_description_parameters(self):
        return {
            'to_location': self.to_location.name
        }

    def can_traverse(self, thing):
        return True

    @property
    def from_location(self):
        raise NotImplementedError()

    @property
    def to_location(self):
        raise NotImplementedError()


class StaticExit(Exit):
    """ Exits with a static exit location, i.e. built in room exits """

    def __init__(self, from_loc, to_loc):
        super(StaticExit, self).__init__()
        self._from_loc = from_loc
        self._to_loc = to_loc
        self.description_template = 'To %(to_location)s'

    @property
    def from_location(self):
        return self._from_loc

    @property
    def to_location(self):
        return self._to_loc


class OutsideExit(Exit):
    """ Exits to outside the given thing """

    def __init__(self, from_loc, thing):
        super(OutsideExit, self).__init__()
        self._from_location = from_loc
        self._thing = thing
        self.description_template = 'Out of %(thing)s'

    def _get_description_parameters(self):
        d = super(OutsideExit, self)._get_description_parameters()
        d.update({'thing': self._thing.name})
        return d

    @property
    def to_location(self):
        return self._thing.location

    @property
    def from_location(self):
        return self._from_location


class EntranceExit(Exit):
    """ Entrance into a particular thing """
    def __init__(self, thing, to_loc):
        self._thing = thing
        self._to_location = to_loc
        self.description_template = 'Into %(thing)s'

    def _get_description_parameters(self):
        d = super(EntranceExit, self)._get_description_parameters()
        d.update({'thing': self._thing.name})
        return d

    @property
    def to_location(self):
        return self._to_location

    @property
    def from_location(self):
        return self._thing.location

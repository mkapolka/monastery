import sys

from properties.properties import *
from properties.materials import Metal, Wood
from properties.location_properties import *
from properties.forms import Human
from thing import Thing

class LazyTemplate(object):
    def __init__(self, template_name):
        self.template_name = template_name

    def instantiate(self):
        return getattr(sys.modules[__name__], self.template_name).instantiate()

def lazy(template_name):
    return LazyTemplate(template_name)

class Template(object):
    size = Thing.Size.medium
    form = None
    material = None

    @classmethod
    def instantiate(cls):
        thing = Thing()
        thing.name = cls.name
        thing.set_form(cls.form)
        thing.set_material(cls.material)
        thing.size = cls.size
        for prop in cls.properties:
            thing.become(prop)

        if hasattr(cls, 'contents'):
            for prop, contents in cls.contents.items():
                for template in contents:
                    thing.get_property(prop).add_thing(template.instantiate())

        return thing

class Apple(Template):
    name = "an apple"
    properties = [Edible, Holdable, ShrinkOnEat]
    size = Thing.Size.small

class Barrel(Template):
    name = "A barrel"
    properties = [IsContainer]
    size = Thing.Size.medium
    material = Wood

    contents = {
        IsContainer: [
            lazy('Apple'),
            lazy('Apple'),
            lazy('Apple')
        ]
    }

class Firepit(Template):
    name = "A fire pit"
    properties = [IsContainer, Hot]
    form = None
    material = None

class Player(Template):
    name = "The player"
    properties = [Inventory]
    form = Human
    material = None

class Teapot(Template):
    name = "A teapot"
    size = Thing.Size.small
    properties = [Holdable, IsContainer]
    form = None
    material = Metal

    reactions = [
        # make_reaction("tick", None)
    ]

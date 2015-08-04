import sys

from form import Form
from properties.forms import Human
from properties.location_properties import IsContainer, Inventory, HasStomach
from properties.materials import Metal, Wood, Stone, Flesh
from properties.properties import Edible, ShrinkOnEat, Hot, TeapotShaped, MortarShaped, Openable
import properties as p
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


class FormTemplate(Template):
    class DynamicForm(Form):
        def __init__(self, template_class):
            self.properties = template_class.form_properties

    @classmethod
    @property
    def form(cls):
        return FormTemplate.DynamicForm(cls)


class Apple(Template):
    name = "an apple"
    properties = [Edible, ShrinkOnEat]
    size = Thing.Size.apple


class Barrel(Template):
    name = "A barrel"
    properties = [IsContainer, Openable]
    size = Thing.Size.medium
    material = Wood

    contents = {
        IsContainer: [
            lazy('Apple'),
            lazy('Apple'),
            lazy('Apple')
        ]
    }


class Cat(Template):
    name = "A dozy cat"
    properties = [HasStomach]
    material = Flesh
    size = Thing.Size.dog


class Mortar(Template):
    name = "A mortar & pestle"
    properties = [MortarShaped]
    size = Thing.Size.small
    material = Stone


class Oven(Template):
    name = "An oven"
    properties = [IsContainer, Hot, p.Open]
    material = Metal
    size = Thing.Size.stool


class Player(Template):
    name = "The player"
    properties = [Inventory]
    form = Human
    material = Flesh


class Teapot(Template):
    name = "A teapot"
    size = Thing.Size.small
    properties = [IsContainer, TeapotShaped, p.Open]
    form = None
    material = Metal

    contents = {
        IsContainer: [
            lazy('Water')
        ]
    }


class Water(Template):
    name = "some water"
    size = Thing.Size.small
    properties = [p.Liquid, p.Boilable]

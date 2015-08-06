import sys

from enums import Size
from form import Form
from properties.forms import Human
from properties.location_properties import IsContainer, Inventory, HasStomach
import properties.materials as m
from properties.properties import Edible, ShrinkOnEat, Hot, TeapotShaped, MortarShaped, Openable
from thing import Thing
import properties as p
import properties.location_properties as lp


class LazyTemplate(object):
    def __init__(self, template_name):
        self.template_name = template_name

    def __getattr__(self, key):
        return getattr(getattr(sys.modules[__name__], self.template_name), key)


def lazy(template_name):
    return LazyTemplate(template_name)


def instantiate_template(template):
    thing = Thing()
    thing.name = template.name
    thing.set_form(template.form)
    thing.set_material(template.material)
    thing.size = template.size
    for prop in template.properties:
        thing.become(prop)
    if hasattr(template, 'contents'):
        for prop, contents in template.contents.items():
            for template in contents:
                thing.get_property(prop).add_thing(instantiate_template(template))
    return thing


class Template(object):
    size = Size.medium
    form = None
    material = None


class CustomTemplate(Template):
    def __init__(self, base, **kwargs):
        self.base = base
        self.custom_fields = kwargs

    def __getattr__(self, key):
        if key in self.custom_fields:
            return self.custom_fields[key]
        else:
            return getattr(self.base, key)


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
    properties = [Edible]
    size = Size.apple


class Barrel(Template):
    name = "A barrel"
    properties = [IsContainer, Openable]
    size = Size.medium
    material = m.Wood

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
    material = m.Flesh
    size = Size.dog
    contents = {
        HasStomach: [
            Apple
        ]
    }


class Mortar(Template):
    name = "A mortar & pestle"
    properties = [MortarShaped]
    size = Size.small
    material = m.Stone


class Oven(Template):
    name = "An oven"
    properties = [IsContainer, Hot, p.Open]
    material = m.Metal
    size = Size.stool


class Player(Template):
    name = "The player"
    properties = [Inventory]
    form = Human
    material = m.Flesh


class ShrinkyMushroom(Template):
    name = "Spiteful fungi"
    properties = [ShrinkOnEat]
    material = m.Plant
    size = Size.apple


class Teapot(Template):
    name = "A teapot"
    size = Size.small
    properties = [IsContainer, TeapotShaped, p.Open]
    form = None
    material = m.Metal

    contents = {
        IsContainer: [
            lazy('Water')
        ]
    }


class Table(Template):
    name = "a table"
    size = Size.stool
    properties = [lp.Surface]
    material = m.Wood

    contents = {
        lp.Surface: [
            Teapot
        ]
    }


class Water(Template):
    name = "some water"
    size = Size.small
    properties = [p.Liquid, p.Boilable]

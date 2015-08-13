import sys

from ai import create_ai, AIContext
from enums import Size
from form import Form
from properties.forms import Human
from properties.location_properties import IsContainer, Inventory, HasStomach
from properties.properties import Edible, ShrinkOnEat, Hot, TeapotShaped, MortarShaped, Openable
from thing import Thing
import properties as p
import properties.location_properties as lp
import properties.materials as m


class LazyTemplate(object):
    def __init__(self, template_name):
        self.template_name = template_name

    def __getattr__(self, key):
        return getattr(getattr(sys.modules[__name__], self.template_name), key)

    def __repr__(self):
        return '<LazyTemplate:%s>' % self.template_name


def lazy(template_name):
    return LazyTemplate(template_name)


def instantiate_template(template):
    thing = Thing()
    thing.name = template.name
    thing.set_form(template.form)
    thing.set_material(template.material)
    thing.size = template.size

    if hasattr(template, 'damage'):
        thing.damage = template.damage
    if hasattr(template, 'damage_type'):
        thing.damage_type = template.damage_type

    for prop in template.properties:
        thing.become(prop)
    if hasattr(template, 'contents'):
        for prop, contents in template.contents.items():
            for contained_template in contents:
                thing.get_property(prop).add_thing(instantiate_template(contained_template))
    if template.ai:
        import ais
        ai_program = getattr(ais, template.ai)
        thing.ai_context = AIContext(thing)
        thing.ai = create_ai(ai_program, thing.ai_context)
        thing.ai.begin()
    thing.hp = thing.max_hp
    return thing


class Template(object):
    size = Size.medium
    form = None
    material = None
    ai = None


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


class Bolus(Template):
    name = 'a bolus'
    properties = [p.Soft]


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


class Bucket(Template):
    name = "a bucket"
    properties = [lp.IsContainer, p.Open]
    size = Size.child
    material = m.Wood

    contents = {
        IsContainer: [
            lazy('Water')
        ]
    }


class Cat(Template):
    name = "A dozy cat"
    properties = [HasStomach]
    material = m.Flesh
    size = Size.cat
    damage = 2
    damage_type = 'slash'

    ai = 'cat_ai'


class Knife(Template):
    name = "a knife"
    properties = [p.Bladed]
    size = Size.apple
    material = m.Metal
    damage = 4
    damage_type = 'slash'


class Mortar(Template):
    name = "A mortar & pestle"
    properties = [MortarShaped]
    size = Size.apple
    material = m.Stone


class Mouse(Template):
    name = 'a field mouse'
    properties = [lp.HasStomach]
    size = Size.apple
    material = m.Flesh

    ai = 'mouse_ai'


class NeedleAndThread(Template):
    name = 'a needle and thread'
    properties = [p.Sews]
    size = Size.tiny
    material = m.Metal


class Oven(Template):
    name = "An oven"
    properties = [IsContainer, Hot, p.Open, p.Immobile]
    material = m.Metal
    size = Size.child


class Player(Template):
    name = "The player"
    properties = [Inventory]
    form = Human
    material = m.Flesh


class ShrinkyMushroom(Template):
    name = "spiteful fungi"
    properties = [ShrinkOnEat, Edible, p.Digestible]
    material = m.Plant
    size = Size.apple


class Sponge(Template):
    name = 'a sponge'
    properties = [IsContainer, p.Absorbant]
    size = Size.apple
    material = m.Plant


class TeaKettle(Template):
    name = "a tea kettle"
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
    size = Size.child
    properties = [lp.Surface]
    material = m.Wood

    contents = {
        lp.Surface: [
            TeaKettle
        ]
    }


class Water(Template):
    name = "some water"
    size = Size.small
    properties = [p.Liquid, p.Boilable, p.Digestible]


class Well(Template):
    name = "a well"
    size = Size.medium
    properties = [p.SpringsWater, p.IsContainer, p.Open]
    material = m.Stone
    contents = {
        IsContainer: [
            Water
        ]
    }


class WillowRoot(Template):
    name = "a knotted willow root"
    size = Size.apple
    properties = [p.HealsWounds, p.Digestible]
    material = m.Wood


class Wolf(Template):
    name = "a wolf"
    size = Size.child
    material = m.Flesh
    ai = 'wolf_ai'

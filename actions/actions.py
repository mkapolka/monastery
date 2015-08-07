from action import Action
from location import PropertyLocation
from properties import Immobile, HasStomach, Edible, MortarShaped, Dissolvable, Openable, Open, Liquid
from properties.location_properties import get_accessible_things, get_all_locations, entrances_to_thing
from utils import letter_prompt
import properties as p
import templates as t


class CantMoveException(Exception):
    TooBig = 1
    CantTraverse = 2
    CantContain = 3
    CantHold = 4

    def __init__(self, reason):
        super(CantMoveException, self).__init__()
        self.reason = reason


def _liquid_holdable(holder, thing):
    # Is the liquid contained in something we can hold?
    if isinstance(thing.location, PropertyLocation):
        return can_hold(holder, thing.location.thing)


def can_hold(holder, thing):
    return not thing.is_property(Immobile) and \
        (not thing.is_property(Liquid) or _liquid_holdable(holder, thing)) and \
        thing.size < holder.size


def move_thing(mover, thing, entrance):
    if not can_hold(mover, thing):
        raise CantMoveException(CantMoveException.CantHold)
    if not entrance.can_traverse(thing):
        raise CantMoveException(CantMoveException.CantTraverse)
    if not entrance.to_location.can_contain(thing):
        if entrance.to_location.size < thing.size:
            raise CantMoveException(CantMoveException.TooBig)
        raise CantMoveException(CantMoveException.CantContain)
    else:
        mover.tell("You move %s %s" % (thing.name, entrance.description))
        entrance.to_location.add_thing(thing)


class DrinkAction(Action):
    prereq = Liquid

    @classmethod
    def describe(cls, thing):
        return "Drink %s" % thing.name

    @classmethod
    def can_perform(cls, thing, drinker):
        return True

    @classmethod
    def perform(cls, thing, drinker):
        drinker.tell("You drink %s" % thing.name)
        drinker.get_property(HasStomach).add_thing(thing)


class EatAction(Action):
    prereq = Edible

    @classmethod
    def describe(cls, thing):
        return "Eat %s" % thing.name

    @classmethod
    def can_perform(cls, thing, eater):
        return eater.size > thing.size and eater.is_property(HasStomach)

    @classmethod
    def perform(cls, thing, eater):
        eater.tell("You eat %s" % thing.name)
        eater.get_property(HasStomach).add_thing(thing)


class GrindWithPestleAction(Action):
    prereq = MortarShaped

    @classmethod
    def describe(cls, thing):
        return "Grind something with %s" % thing.name

    @classmethod
    def can_perform(cls, thing, grinder):
        return grinder.size > thing.size

    @classmethod
    def perform(cls, thing, grinder):
        choice = letter_prompt(GrindWithPestleAction.get_applicable_objects(thing, grinder), 'Grind what?', lambda x: x.name)
        if choice:
            if choice.is_property(Liquid):
                grinder.tell("You can't grind a liquid!")
                return

            if choice.size >= thing.size:
                grinder.tell("%s is too big to grind with %s..." % (choice.name, thing.name))
                return

            if choice.size <= thing.size:
                # Grind it
                grinder.tell("You grind %s into a powder." % choice.name)
                for prop in choice.get_properties_of_types(['mechanical']):
                    choice.unbecome(prop.__class__, force=True)
                # Powder properties TODO: abstract these somewhere?
                choice.become(Dissolvable)
                choice.name = 'some powdered %s' % choice.name

    @classmethod
    def get_applicable_objects(cls, thing, grinder):
        return [
            t for t in get_accessible_things(grinder) if t not in [grinder, thing]
        ]


class OpenCloseAction(Action):
    prereq = Openable

    @classmethod
    def describe(cls, thing):
        return 'Close %s' % thing.name if thing.is_property(Open) else 'Open %s' % thing.name

    @classmethod
    def can_perform(cls, thing, opener):
        return True

    @classmethod
    def perform(cls, thing, opener):
        if thing.is_property(Open):
            opener.tell("You close %s" % thing.name)
            thing.unbecome(Open)
        else:
            opener.tell("You open %s" % thing.name)
            thing.become(Open)


class WellAction(Action):
    prereq = p.SpringsWater

    @classmethod
    def describe(cls, thing):
        return 'Fetch water from %s' % thing.name

    @classmethod
    def can_perform(cls, thing, actor):
        return True

    @classmethod
    def perform(cls, thing, opener):
        containers = get_accessible_things(opener)
        container = letter_prompt(containers, 'Fill what?', lambda x: x.name)
        if container:
            if not can_hold(opener, container):
                opener.tell("You can't hold %s" % container.name)
            elif not any(map(lambda x: x.can_access(opener), entrances_to_thing(container))):
                opener.tell("%s can't hold liquids..." % container.name)
            else:
                water = t.instantiate_template(t.Water)
                location = get_all_locations(container)[0]
                location.add_thing(water)
                water.size = location.size
                opener.tell("You fill %s with water." % container.name)

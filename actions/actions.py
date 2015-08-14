import math
import random

from action import Action
from enums import Size
from location import PropertyLocation
from properties import Immobile, HasStomach, Edible, MortarShaped, Dissolvable, Openable, Open, Liquid
from properties.location_properties import get_accessible_things, get_all_locations, entrances_to_thing, get_all_contents
from utils import letter_prompt, flatten_array
import properties as p
import properties.location_properties as lp
from reaction import enqueue_event, Event
import templates as t


def choose_target(performer, prompt, filter_func=None, ignore=None):
    def describe_to_performer(thing):
        if thing.location == performer.location:
            return thing.name
        else:
            return '%s (%s)' % (thing.name, thing.location.name)

    if not filter_func:
        filter_func = lambda x: True
    if not ignore:
        ignore = []
    choices = [t for t in get_accessible_things(performer) if t not in ignore and filter_func(t)]
    return letter_prompt(choices, prompt, describe_to_performer)


class CantMoveReason(object):
    TooBig = 1
    CantTraverse = 2
    CantContain = 3
    CantHold = 4
    CantAccess = 5


def _liquid_holdable(holder, thing):
    # Is the liquid contained in something we can hold?
    if isinstance(thing.location, PropertyLocation):
        return can_hold(holder, thing.location.thing)


def can_hold(holder, thing):
    return not thing.is_property(Immobile) and \
        (not thing.is_property(Liquid) or _liquid_holdable(holder, thing)) and \
        thing.size < holder.size


def why_cant_move(mover, thing, entrance):
    if mover:
        if not can_hold(mover, thing):
            return CantMoveReason.CantHold
        if not entrance.can_access(mover):
            return CantMoveReason.CantAccess
    if not entrance.to_location.can_contain(thing):
        if entrance.to_location.size < thing.size:
            return CantMoveReason.TooBig
        return CantMoveReason.CantContain
    return None


def move_thing(mover, thing, entrance):
    cant_move_reason = why_cant_move(mover, thing, entrance)
    if cant_move_reason:
        mover.tell({
            CantMoveReason.CantHold: "You can't hold %s" % (thing.name),
            CantMoveReason.TooBig: '%s is too big to fit %s' % (thing.name, entrance.to_location.name),
            CantMoveReason.CantTraverse: "%s can't go %s" % (thing.name, entrance.description),
            CantMoveReason.CantAccess: "%s can't access %s" % (mover.name, entrance.description),
            CantMoveReason.CantContain: "%s can't fit in %s" % (thing.name, entrance.to_location.name),
        }[cant_move_reason])
    else:
        mover.tell("You move %s %s" % (thing.name, entrance.description))
        entrance.to_location.add_thing(thing)


def walk_thing(thing, entrance):
    why_cant_walk = why_cant_move(None, thing, entrance)
    if why_cant_walk:
        thing.tell("You can't go there.")
    else:
        thing.tell("You walk %s" % entrance.description)
        thing.tell_room("%s goes %s" % (thing.name, entrance.description))
        entrance.to_location.add_thing(thing)
        thing.tell_room("%s arrives from %s" % (thing.name, entrance.from_location.name))


def attack(attacker, target, weapon=None):
    weapon_damage = weapon.damage if weapon else attacker.damage
    material = weapon.material if weapon else attacker.material
    mat_damage_mod = material.damage_mod if material else 1
    size_mod = attacker.size
    attack_type = weapon.damage_type if weapon else attacker.damage_type

    damage = int(random.randint(1, weapon_damage) * size_mod * mat_damage_mod)

    attacker.tell("You %s %s for %d damage." % (attack_type, target.name, damage))
    attacker.broadcast("%s %ss %s for %d damage." % (attacker.name, attack_type, target.name, damage))
    target.attack(damage, attack_type, attacker)
    enqueue_event(Event(attack_type, target, attacker=attacker, weapon=weapon, damage=damage))


class CutAction(Action):
    prereq = p.Bladed

    @classmethod
    def describe(cls, thing):
        return "Cut something with %s" % thing.name

    @classmethod
    def can_perform(cls, thing, cutter):
        return True

    @classmethod
    def perform(cls, thing, cutter):
        target = choose_target(cutter, 'Cut what?', ignore=[thing])
        if target:
            attack(cutter, target, thing)


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
        # Split the thing into two sizes
        if thing.size <= Size.apple:
            drinker.get_property(HasStomach).add_thing(thing)
            drinker.tell("You drink the rest of %s" % thing.name)
        else:
            bolus = thing.duplicate()
            bolus.size -= 1
            thing.size -= 1
            drinker.get_property(HasStomach).add_thing(bolus)
            drinker.tell("You drink from %s" % thing.name)


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
        eater.broadcast("%s eats %s" % (eater.name, thing.name))
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
        choice = choose_target(grinder, 'Grind what?', ignore=[thing])
        if choice:
            if choice.is_property(Liquid):
                grinder.tell("You can't grind a liquid!")
                return

            if choice.size > thing.size:
                grinder.tell("%s is too big to grind with %s..." % (choice.name, thing.name))
                return

            if choice.size <= thing.size:
                # Grind it
                damage = math.pow(thing.size, 2)
                choice.attack(damage, 'grind')
                grinder.tell("You grind %s for %d points of damage" % (choice.name, damage))
                if choice.health_percentage < .25:
                    grinder.tell("You grind %s into a powder." % choice.name)
                    for prop in choice.get_properties_of_types(['mechanical']):
                        choice.unbecome(prop.__class__, force=True)
                    # Powder properties TODO: abstract these somewhere?
                    choice.become(Dissolvable)
                    choice.name = 'some powdered %s' % choice.name


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


class SewAction(Action):
    prereq = p.Sews

    @classmethod
    def can_perform(cls, thing, performer):
        return True

    @classmethod
    def describe(cls, thing):
        return 'Sew something with %s' % thing.name

    @classmethod
    def perform(cls, thing, performer):
        target = choose_target(performer, 'Sew what?', ignore=[thing])
        if target:
            if not target.is_property(p.Soft):
                performer.tell("%s is too hard to sew up." % target.name)
            elif not target.is_property(p.Open):
                performer.tell("%s doesn't need to be sewn up." % target.name)
            else:
                performer.tell("You sew %s shut." % target.name)
                target.unbecome(Open)


class SopWringAction(Action):
    prereq = p.Absorbant

    @classmethod
    def _contains_liquid(cls, thing):
        return any(map(lambda x: x.is_property(p.Liquid), get_all_contents(thing)))

    @classmethod
    def can_perform(cls, thing, sopper):
        return True

    @classmethod
    def describe(cls, thing):
        return 'Wring out %s' % thing.name if cls._contains_liquid(thing) else 'Sop up liquid with %s' % thing.name

    @classmethod
    def perform(cls, thing, sopper):
        if cls._contains_liquid(thing):
            things = [t for t in get_accessible_things(sopper) if t != thing]
            entrances = flatten_array(entrances_to_thing(t) for t in things)
            entrances = filter(lambda x: x.can_access(sopper), entrances)
            choice = letter_prompt(entrances, 'Wring into what?', lambda x: x.description)
            if choice:
                sopper.tell("You wring out %s %s" % (thing.name, choice.description))
                for content in get_all_contents(thing):
                    choice.to_location.add_thing(content)
        else:
            choice = choose_target(sopper, 'Sop what?', ignore=[thing])
            if choice:
                if choice.is_property(Liquid):
                    sopper.tell("You sop up %s" % choice.name)
                    thing.get_property(lp.IsContainer).add_thing(choice)
                else:
                    sopper.tell("You can't sop that up!")


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
        container = choose_target(opener, 'Fill what?', ignore=[thing])
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

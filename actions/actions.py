from action import Action
from properties import Immobile, Inventory, IsContainer, HasStomach, Edible, MortarShaped, Dissolvable, Openable, Open, Liquid
from properties.location_properties import entrances_to_thing, get_all_contents, get_accessible_things, get_accessible_locations
import ui
from utils import letter_prompt


def can_hold(holder, thing):
    return not thing.is_property(Immobile) and \
        not thing.is_property(Liquid) and \
        thing.size < holder.size


class DrinkContentsAction(Action):
    prereq = IsContainer

    @classmethod
    def describe(cls, thing):
        return "Drink from %s" % thing.name

    @classmethod
    def can_perform(cls, thing, drinker):
        return any(map(lambda x: x.is_property(Liquid), thing.get_property(IsContainer).get_all_things()))

    @classmethod
    def perform(cls, thing, drinker):
        drinker.tell("You drink from %s" % thing.name)
        liquid_things = [t for t in thing.get_property(IsContainer).get_all_things() if t.is_property(Liquid)]
        for liquid_thing in liquid_things:
            drinker.get_property(HasStomach).add_thing(liquid_thing)


class EmptyAction(Action):
    prereq = IsContainer

    @classmethod
    def describe(cls, thing):
        return "Empty the contents of %s" % thing.name

    @classmethod
    def can_perform(cls, thing, emptier):
        return can_hold(emptier, thing)

    @classmethod
    def perform(cls, thing, emptier):
        places = get_accessible_locations(emptier) + ['floor']
        ui.message("Empty where?")
        choice = letter_prompt(places, '>', lambda x: x.name if x != 'floor' else 'Onto the floor')
        if choice:
            if choice == 'floor':
                choice = emptier.location
            ui.message("You empty the contents of %s %s" % (thing.name, choice.name))
            for thing in thing.get_property(IsContainer).get_all_things():
                choice.add_thing(thing)


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
        ui.message("Grind what?")
        choice = letter_prompt(GrindWithPestleAction.get_applicable_objects(thing, grinder), '>', lambda x: x.name)
        if choice:
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
            t for t in get_accessible_things(grinder) if t.size <= thing.size
        ]


class MoveAction(Action):
    @classmethod
    def describe(cls, thing):
        return "Move %s" % thing.name

    @classmethod
    def can_perform(cls, thing, mover):
        return can_hold(mover, thing)

    @classmethod
    def perform(cls, thing, mover):
        cls.prompt_for_places(thing, mover)

    @classmethod
    def prompt_for_places(cls, thing, mover):
        ui.message("Where do you want to put it?")
        places = cls.places_to_put(thing, mover) + ['ground']
        exit = letter_prompt(places, 'Where do you want to put it?', lambda x: x.description if x != 'ground' else 'On the ground')
        if exit:
            if exit == 'ground':
                mover.tell("You drop %s" % thing.name)
                mover.location.add_thing(thing)
            else:
                mover.tell("You put %s %s" % (thing.name, exit.description))
                exit.to_location.add_thing(thing)

    @classmethod
    def places_to_put(cls, thing, mover):
        """ Allow putting on the ground and inside of things (containers) """
        output = []
        for thing2 in mover.location.things:
            for entrance in entrances_to_thing(thing2):
                if entrance.can_traverse(thing) and entrance.to_location.can_contain(thing):
                    output.append(entrance)
        return output


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


class TakeFromAction(Action):
    prereq = IsContainer

    @classmethod
    def describe(cls, thing):
        return "Take something from %s" % thing.name

    @classmethod
    def can_perform(cls, thing, taker):
        return bool(TakeFromAction.grabable_things(thing, taker))

    @classmethod
    def grabable_things(cls, thing, taker):
        return [t for t in get_all_contents(thing) if can_hold(taker, t)]

    @classmethod
    def perform(cls, thing, taker):
        target = letter_prompt(TakeFromAction.grabable_things(thing, taker), "Take what?", lambda x: x.name)
        if target:
            taker.tell("You take %s from %s" % (target.name, thing.name))
            taker.get_property(Inventory).add_thing(target)
        else:
            pass

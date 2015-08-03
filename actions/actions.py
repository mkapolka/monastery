from action import Action
from properties import Holdable, Immobile, Inventory, IsContainer, HasStomach, Edible, MortarShaped, Dissolvable
from properties.location_properties import entrances_to_thing, get_all_contents, get_accessible_things
from utils import number_prompt


def can_hold(holder, thing):
    return thing.is_property(Holdable) and \
        not thing.is_property(Immobile) and \
        thing.size < holder.size and \
        thing.location not in holder.locations


class PickupAction(Action):
    prereq = Holdable

    @classmethod
    def describe(cls, thing):
        return "Take %s" % thing.name

    @classmethod
    def can_perform(self, thing, pick_upper):
        return can_hold(pick_upper, thing)

    @classmethod
    def perform(self, thing, pick_upper):
        pick_upper.tell("You pick up %s" % thing.name)
        pick_upper.get_property(Inventory).add_thing(thing)


class DropAction(Action):
    prereq = Holdable

    @classmethod
    def describe(cls, thing):
        return "Drop %s" % thing.name

    @classmethod
    def can_perform(cls, thing, dropper):
        return thing.location in dropper.locations

    @classmethod
    def perform(cls, thing, dropper):
        cls.prompt_for_places(thing, dropper)

    @classmethod
    def prompt_for_places(cls, thing, dropper):
        print "Where do you want to put it?"
        places = cls.places_to_put(thing, dropper) + ['ground']
        exit = number_prompt(places, 'Where do you want to put it?', lambda x: x.description if x != 'ground' else 'On the ground')
        if exit:
            if exit == 'ground':
                dropper.tell("You drop %s" % thing.name)
                dropper.location.add_thing(thing)
            else:
                dropper.tell("You put %s %s" % (thing.name, exit.description))
                exit.to_location.add_thing(thing)

    @classmethod
    def places_to_put(cls, thing, dropper):
        """ Allow putting on the ground and inside of things (containers) """
        output = []
        for thing2 in dropper.location.things:
            for entrance in entrances_to_thing(thing2):
                if entrance.can_traverse(thing) and entrance.to_location.can_contain(thing):
                    output.append(entrance)
        return output


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
        target = number_prompt(TakeFromAction.grabable_things(thing, taker), "Take what?", lambda x: x.name)
        if target:
            taker.tell("You take %s from %s" % (target.name, thing.name))
            taker.get_property(Inventory).add_thing(target)
        else:
            pass


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
        print "Grind what?"
        choice = number_prompt(GrindWithPestleAction.get_applicable_objects(thing, grinder), '>', lambda x: x.name)
        if choice:
            # Grind it
            grinder.tell("You grind %s into a powder." % choice.name)
            choice.name = 'some powdered %s' % choice.name
            for prop in choice.get_properties_of_types(['mechanical']):
                choice.unbecome(prop.__class__, force=True)
            # Powder properties TODO: abstract these somewhere?
            choice.become(Holdable)
            choice.become(Dissolvable)

    @classmethod
    def get_applicable_objects(cls, thing, grinder):
        return [
            t for t in get_accessible_things(grinder) if t.size <= thing.size
        ]

import math
import random

from enums import Size
from properties.location_properties import HasStomach, get_all_contents, are_touching
from properties.properties import Flammable, ShrinkOnEat, TeapotShaped, Boiling, Hot
from reaction import Reaction, enqueue_event, Event
from thing import destroy_thing, calc_hp
from utils import sentence
from templates import instantiate_template
import properties as p
import properties.spawner as sp
import properties.location_properties as lp


def burst_info_flames(thing):
    thing.broadcast("%s bursts into flames!" % thing.name)
    thing.tell("You burst into flames!")
    thing.become(p.Burning)


class AlightWhenBurned(Reaction):
    predicates = [p.Flammable]
    anti_predicates = [p.Burning]
    event = "burn"

    @classmethod
    def perform(cls, event):
        burst_info_flames(event.target)


class AlightWhenHot(Reaction):
    predicates = [p.Hot, Flammable]
    anti_predicates = [p.Burning]
    event = "tick"

    @classmethod
    def perform(cls, event):
        if random.random() < .25:
            burst_info_flames(event.target)


class BoilBoilable(Reaction):
    predicates = [p.Boilable, Hot, p.Liquid]
    anti_predicates = [Boiling]
    event = "tick"

    @classmethod
    def perform(cls, event):
        if random.random() < .25:
            event.target.broadcast("%s starts boiling!" % event.target.name)
            event.target.become(Boiling)


class BoilOff(Reaction):
    predicates = [Boiling]
    event = "tick"

    @classmethod
    def perform(cls, event):
        event.target.attack(max(event.target.max_hp / 10, 1), 'boil')
        if event.target.hp <= calc_hp(event.target, size=event.target.size - 1):
            if event.target.size > Size.tiny:
                event.target.broadcast("Some of %s boils away" % event.target.name)
                event.target.size -= 1
            else:
                event.target.broadcast("%s boils away to nothing..." % event.target.name)
                destroy_thing(event.target)


class Breathe(Reaction):
    predicates = [p.Breathes]
    event = "tick"

    @classmethod
    def perform(cls, event):
        gassy_things = [t for t in event.target.location.things if t.is_property(p.Gas)]
        if gassy_things:
            for thing in gassy_things:
                enqueue_event(Event("ingest", thing, ingester=event.target))


class BurnNearby(Reaction):
    predicates = [p.Burning]
    event = "tick"

    @classmethod
    def perform(cls, event):
        neighbors = [t for t in event.target.location.things if t != event.target if are_touching(event.target, t)]
        for neighbor in neighbors:
            event.target.broadcast("%s burns %s" % (event.target.name, neighbor.name))


class CutOpen(Reaction):
    anti_predicates = [p.Open, p.Hard]
    event = "slash"

    @classmethod
    def perform(cls, event):
        if event.target.locations:
            thing = event.target
            thing.become(p.Open, custom_description='has been slashed open')
            thing.unbecome(p.Openable)
            event.attacker.tell("You slash open %s!" % thing.name)


class CoolDown(Reaction):
    predicates = [p.Hot]
    anti_predicates = [p.HeatsContents]
    event = "tick"

    @classmethod
    def perform(cls, event):
        if random.random() < .1:
            event.target.unbecome(p.Hot)
            event.target.tell_room("%s cools down." % event.target.name)


class DigestContents(Reaction):
    predicates = [HasStomach]
    event = "tick"

    @classmethod
    def perform(cls, event):
        if event.target.alive:
            contents = event.target.get_property(HasStomach).get_all_things()
            damage = event.target.size * 1
            for thing in contents:
                thing.attack(damage, 'digest')
                enqueue_event(Event("ingest", thing, ingester=event.target))
                if thing.hp <= 0:
                    thing.tell("You are digested into an insubstantial mush")
                    thing.broadcast("%s is digested into an insubstantial mush" % thing.name)
                    destroy_thing(thing)


class DissipateGas(Reaction):
    predicates = [p.Gas]
    event = "tick"

    @classmethod
    def perform(cls, event):
        event.target.hp -= max(event.target.max_hp / 10, 1)
        if event.target.hp <= 0:
            event.target.broadcast("%s dissipates into nothing." % event.target.name)
            event.target.tell("You dissipate into nothing.")
            destroy_thing(event.target)


class DissolveIntoLiquid(Reaction):
    predicates = [p.Dissolvable]
    event = "tick"

    @classmethod
    def perform(cls, event):
        liquid_neighbors = [t for t in event.target.location.things if t.is_property(p.Liquid) and are_touching(event.target, t)]
        if liquid_neighbors:
            into = liquid_neighbors[0]
            event.target.broadcast("%s dissolves into %s" % (event.target.name, into.name))
            liquid_neighbors[0].transfer_properties(event.target, event.target.get_properties_of_types(['chemical']))
            destroy_thing(event.target)


class HeatContents(Reaction):
    predicates = [p.HeatsContents]
    event = "tick"

    @classmethod
    def perform(cls, event):
        for thing in get_all_contents(event.target):
            if not thing.is_property(Hot):
                thing.broadcast("%s heats up." % thing.name)
                thing.become(Hot)


class HealsWoundsRxn(Reaction):
    predicates = [p.HealsWounds]
    event = "ingest"

    @classmethod
    def perform(cls, event):
        if event.ingester.hp < event.ingester.max_hp:
            amount_healed = math.pow(event.target.size, 2) * 4
            event.ingester.hp += amount_healed
            event.ingester.tell("You feel your wounds close up")
            event.ingester.broadcast("%s looks healthier" % event.ingester.name)


class IngestBlade(Reaction):
    predicates = [p.Bladed]
    event = "ingest"

    @classmethod
    def perform(cls, event):
        damage = 10 * event.target.size
        event.ingester.tell("%s slices you up from inside!" % event.target.name)
        event.ingester.attack(damage, 'slash', event.target)
        enqueue_event(Event('slash', event.ingester, attacker=event.target, weapon=event.target, damage=damage))


class IngestPoison(Reaction):
    predicates = [p.Poisonous]
    event = "ingest"

    @classmethod
    def perform(cls, event):
        if not event.ingester.is_property(p.Poisoned) and not event.ingester.is_property(p.PoisonImmune):
            event.ingester.become(p.Poisoned)
            event.ingester.broadcast("%s is poisoned by %s" % (event.ingester.name, event.target.name))
            event.ingester.tell("You are poisoned by %s" % event.target.name)


class IngestAntidote(Reaction):
    predicates = [p.Antidote]
    event = 'ingest'

    @classmethod
    def perform(cls, event):
        if event.ingester.is_property(p.Poisoned):
            event.ingester.unbecome(p.Poisoned)
            event.ingester.tell("%s cures you of your poison." % event.target.name)
            event.ingester.broadcast("%s cures %s of their poison." % (event.target.name, event.ingester.name))


class MergeLiquids(Reaction):
    predicates = [p.Liquid]
    event = "tick"

    @classmethod
    def perform(cls, event):
        if not event.target.destroyed:
            neighbors = [t for t in event.target.location.things if t != event.target
                         and t.is_property(p.Liquid)]
            if neighbors:
                neighbor_names = [name for name in map(lambda x: x.name, neighbors) if name != event.target.name]
                if neighbor_names:
                    event.target.broadcast('%s mixes with %s' % (event.target.name, sentence(neighbor_names)))
                for neighbor in neighbors:
                    event.target.size = max(event.target.size, neighbor.size)
                    event.target.transfer_properties(neighbor, neighbor.get_properties_of_types(['physical', 'chemical']))
                    destroy_thing(neighbor)


class MergeGasses(Reaction):
    predicates = [p.Gas]
    event = "tick"

    @classmethod
    def perform(cls, event):
        if not event.target.destroyed:
            neighbors = [t for t in event.target.location.things if t != event.target
                         and t.is_property(p.Gas)]
            if neighbors:
                neighbor_names = [name for name in map(lambda x: x.name, neighbors) if name != event.target.name]
                if neighbor_names:
                    event.target.broadcast('%s mixes with %s' % (event.target.name, sentence(neighbor_names)))
                for neighbor in neighbors:
                    event.target.size = max(event.target.size, neighbor.size)
                    event.target.transfer_properties(neighbor, neighbor.get_properties_of_types(['physical', 'chemical']))
                    destroy_thing(neighbor)


class Poison(Reaction):
    predicates = [p.Poisoned]
    event = "tick"

    @classmethod
    def perform(cls, event):
        damage = max(event.target.max_hp / 20, 1)
        event.target.tell("The poison damages you for %d damage" % damage)
        event.target.attack(damage, 'poison')


class Rot(Reaction):
    predicates = [p.Decomposable]
    event = "tick"

    @classmethod
    def perform(cls, event):
        if not event.target.alive:
            event.target.hp -= 1
            if event.target.hp <= 0 and random.random() < .1:
                event.target.broadcast("%s decomposes into nothing" % (event.target.name))
                destroy_thing(event.target)


class ShrinkDigestible(Reaction):
    predicates = [ShrinkOnEat]
    event = "ingest"

    @classmethod
    def perform(cls, event):
        if event.ingester.size > Size.small:
            event.target.unbecome(ShrinkOnEat)
            # Get the owner of the stomach digesting this
            event.ingester.tell("The world feels larger somehow...")
            event.ingester.broadcast("%s shrinks!" % event.ingester.name)
            event.ingester.size -= 1
            for thing in get_all_contents(event.ingester):
                thing.size -= 1
                if thing.size < 0:
                    thing.tell_room("%s winks out of existence!" % thing.name)
                    thing.tell("You wink out of existence!")
                    destroy_thing(thing)


class SpawnThings(Reaction):
    predicates = [sp.Spawner]
    event = "tick"

    @classmethod
    def perform(cls, event):
        prop = event.target.get_property(sp.Spawner)
        if random.random() < .25 and len(prop.spawned_things) < prop.max_things:
            created = instantiate_template(prop.template, event.target.location)
            prop.spawned_things.append(created)
            event.target.broadcast(prop.spawn_message % {'thing': created.name, 'me': event.target.name})


class SpringLiquid(Reaction):
    predicates = [sp.SpringsWater]
    event = "tick"

    @classmethod
    def perform(cls, event):
        if event.target.is_property(lp.IsContainer):
            location = event.target.get_property(lp.IsContainer).locations.values()[0]
        else:
            location = event.target.location
        prop = event.target.get_property(sp.SpringsWater)
        # Check for existing liquids
        if not any(t for t in location.things if t.is_property(p.Liquid) and t.size >= location.size):
            thing = instantiate_template(prop.template, location)
            thing.size = location.size
            event.target.broadcast("%s fills up with %s" % (event.target.name, thing.name))
            event.target.tell("You fill up with %s" % thing.name)


class Thickens(Reaction):
    predicates = [p.Thickens, p.Liquid]
    event = 'tick'

    @classmethod
    def perform(cls, event):
        event.target.broadcast("%s thickens" % event.target.name)
        event.target.unbecome(p.Liquid)
        event.target.become(p.Slatherable)


class WhistleyTeapot(Reaction):
    predicates = [TeapotShaped]
    event = "tick"

    @classmethod
    def perform(cls, event):
        for thing in get_all_contents(event.target):
            if thing.is_property(Boiling):
                event.target.broadcast("%s whistles!" % event.target.name)

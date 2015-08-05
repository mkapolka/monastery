import sys
import logging

from actions import actions_for_thing
from enums import Size
from properties.location_properties import Inventory, get_accessible_things, get_all_locations
from reaction import process_event_queue, process_tick_events
from templates.templates import Player, instantiate_template
from utils import number_prompt
from world import World

player = instantiate_template(Player)
player.is_player = True
world = World()
world.locations['monastery_kitchen'].add_thing(player)


def action_prompt_v1():
    def describe_to_player(action_tuple):
        thing, action = action_tuple
        if thing.location == player.location:
            return action.describe(thing)
        else:
            return "%s (%s)" % (action.describe(thing), thing.location.name)

    actions = []
    for thing in get_accessible_things(player):
        for action in actions_for_thing(thing):
            if action.can_perform(thing, player):
                actions.append((thing, action))

    which_action = number_prompt(actions, "Do what?", describe_to_player)
    if which_action:
        thing, action = which_action
        action.perform(thing, player)


def action_prompt_v2():
    def describe_to_player(thing):
        if thing.location == player.location:
            return thing.name
        else:
            return "%s (%s)" % (thing.name, thing.location.name)

    things = [t for t in get_accessible_things(player) if actions_for_thing(t)]
    print "Use what?"
    which_thing = number_prompt(things, ">", describe_to_player)
    if which_thing:
        actions = [a for a in actions_for_thing(which_thing) if a.can_perform(which_thing, player)]
        print "Do what?"
        which_action = number_prompt(actions, ">", lambda x: x.describe(which_thing))
        if which_action:
            which_action.perform(which_thing, player)


def examine_thing(thing):
    print thing.name
    print "=" * len(thing.name)
    print ''
    print '%s...' % thing.name
    for location in get_all_locations(thing):
        if location.things:
            print '  %s you find...' % location.name
            for thing in location.things:
                print '    %s' % thing.name
    for prop in thing.properties.values():
        if prop.description:
            print '  %s' % prop.description
    # print size
    sizes = {
        Size.seed: 'about the size of a seed',
        Size.apple: 'about the size of an apple',
        Size.teapot: 'about the size of an teapot',
        Size.dog: 'about the size of a dog',
        Size.stool: 'about the size of a stool',
        Size.person: 'about the size of a person',
        Size.armoire: 'about the size of a armoire',
    }
    if thing.size in sizes.keys():
        print '  is %s' % sizes[thing.size]
    if thing.material is not None and thing.material.name:
        print '  is made of %s' % thing.material.name

    print ''


def describe_location(location):
    print location.name
    print "=" * len(location.name)
    print "You see here..."
    accessible_things = [a for a in get_accessible_things(player)]
    nearest_things = [t for t in accessible_things if t.location == player.location]
    for thing in nearest_things:
        contained_things = [t for t in accessible_things if t.location in thing.locations]
        print '  * %s' % thing.name
        for contained_thing in contained_things:
            print '    * %s (%s)' % (contained_thing.name, contained_thing.location.name)

    print "There are exits to..."
    for exit in location.exits:
        print '   > %s' % exit.to_location.name
    print ''


def thing_name_with_location(thing):
    if thing.location == player.location:
        return thing.name
    else:
        return "%s (%s)" % (thing.name, thing.location.name)


def tick_world():
    process_tick_events(world)
    process_event_queue(world)


def iterate():
    print "[g]o somewhere? [d]o something? [l]ook around? [e]xamine something? [w]ait? [i]nventory?"
    action = raw_input('>')
    print '------'
    if action == 'g':
        print "Go where?"
        all_exits = player.location.get_all_exits()
        # filter out exits that can't be accessed
        all_exits = [
            e for e in all_exits if e.can_traverse(player) and e.to_location.can_contain(player)
        ]
        which_exit = number_prompt(all_exits, ">", lambda x: x.description)
        if which_exit:
            print ""
            player.tell("You go %s...\n" % which_exit.description)
            which_exit.to_location.add_thing(player)
            describe_location(player.location)
    elif action == 'd':
        # action_prompt_v1()
        action_prompt_v2()
    elif action == 'e':
        print 'Examine what?'
        accessible_things = [t for t in get_accessible_things(player)]
        choice = number_prompt(accessible_things, '>', thing_name_with_location)
        if choice:
            print ''
            examine_thing(choice)
    elif action == 'i':
        describe_location(player.get_property(Inventory).locations.values()[0])
    elif action == 'l':
        describe_location(player.location)
    elif action == 'w':
        print "time passes..."
    elif action == 'pdb':
        import pdb
        pdb.set_trace()
    elif action == 'q':
        sys.exit()
    else:
        print "nevermind..."
    tick_world()


def game_loop():
    describe_location(player.location)
    while True:
        try:
            iterate()
        except Exception:
            logging.exception("Problemo!")

if __name__ == "__main__":
    game_loop()

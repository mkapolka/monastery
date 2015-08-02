import sys
import logging

from action import actions_for_thing
from properties.location_properties import Inventory
from templates.templates import Player, Teapot
from reaction import process_event_queue, process_tick_events
from utils import number_prompt
from world import World

player = Player.instantiate()
player.is_player = True
world = World()
world.locations['monastery_kitchen'].add_thing(player)
player.locations[0].add_thing(Teapot.instantiate())

def examine_thing(thing):
    print thing.name
    print "=" * len(thing.name)
    print ''
    print '%s...' % thing.name
    for prop in thing.properties.values():
        if prop.description:
            print '\t%s' % prop.description
    # print size
    sizes = {
        0: 'tiny',
        1: 'small',
        2: 'medium sized',
        3: 'large'
    }
    if thing.size in sizes.keys():
        print '\tis %s' % sizes[thing.size]
    print ''

def describe_location(location):
    print location.name
    print "=" * len(location.name)
    print "You see here..."
    for thing in location.things:
        print '   * %s' % thing.name

    print "There are exits to..."
    for exit in location.exits:
        print '   > %s' % exit.to_location.name
    print ''

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
    elif action =='d':
        print 'do to what?'
        actions = []
        for thing in player.location.things:
            for action in actions_for_thing(thing):
                if action.can_perform(thing, player):
                    actions.append((thing, action))

        for thing in player.get_property(Inventory).get_all_things():
            for action in actions_for_thing(thing):
                if action.can_perform(thing, player):
                    actions.append((thing, action))

        which_action = number_prompt(actions, "Do what?", lambda x: x[1].describe(x[0]))
        if which_action:
            thing, action = which_action
            action.perform(thing, player)
    elif action == 'e':
        things = player.location.things
        print 'Examine what?'
        choice = number_prompt(things, '>', lambda x: x.name)
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
        import pdb; pdb.set_trace()
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
        except Exception as e:
            logging.exception("Problemo!")

if __name__ == "__main__":
    game_loop()

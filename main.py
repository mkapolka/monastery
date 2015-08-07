import sys
import curses

from actions import actions_for_thing, CantMoveException, move_thing, can_hold
from enums import Size
from properties.location_properties import Inventory, get_accessible_things, get_all_locations, entrances_to_thing
from reaction import process_event_queue, process_tick_events
from templates.templates import Player, instantiate_template
import ui
from utils import letter_prompt
from world import World

player = instantiate_template(Player)
player.is_player = True
world = World()
world.locations['monastery_kitchen'].add_thing(player)


def describe_thing_to_player(thing):
    if thing.location == player.location:
        return thing.name
    else:
        return "%s (%s)" % (thing.name, thing.location.name)


def describe_action_to_player(action_tuple):
    thing, action = action_tuple
    if thing.location == player.location:
        return action.describe(thing)
    else:
        return "%s (%s)" % (action.describe(thing), thing.location.name)


def action_prompt_v1():
    actions = []
    for thing in get_accessible_things(player):
        for action in actions_for_thing(thing):
            if action.can_perform(thing, player):
                actions.append((thing, action))

    if not actions:
        ui.message("Can't use anything here.")
    which_action = letter_prompt(actions, "Do what?", describe_action_to_player)
    if which_action:
        thing, action = which_action
        action.perform(thing, player)


def doable_actions_for_thing(thing):
    return filter(lambda a: a.can_perform(thing, player), actions_for_thing(thing))


def action_prompt_v2():
    things = [t for t in get_accessible_things(player) if doable_actions_for_thing(t)]
    which_thing = letter_prompt(things, "Use what?", describe_action_to_player)
    if which_thing:
        actions = [a for a in actions_for_thing(which_thing) if a.can_perform(which_thing, player)]
        which_action = letter_prompt(actions, "Do what?", lambda x: x.describe(which_thing))
        if which_action:
            which_action.perform(which_thing, player)


def move_prompt():
    things = [t for t in get_accessible_things(player)]
    thing_to_move = letter_prompt(things, 'Move what?', describe_thing_to_player)
    if thing_to_move:
        if not can_hold(player, thing_to_move):
            ui.message("You can't hold that!")
            return
        places = []
        good_places = [t for t in player.location.things if t not in [player, thing_to_move]]
        for thing2 in good_places:
            for entrance in entrances_to_thing(thing2):
                if entrance.to_location != thing_to_move.location:
                    places.append(entrance)
        if thing_to_move.location != player.location:
            places.append('ground')
        places.append(player.get_property(Inventory).entrances[0])
        target_location = letter_prompt(places, 'Move where?', lambda x: x.description if x != 'ground' else 'Onto the ground')
        if target_location:
            if target_location == 'ground':
                ui.message("You put %s on the floor" % thing_to_move.name)
                player.location.add_thing(thing_to_move)
                return

            try:
                move_thing(player, thing_to_move, target_location)
            except CantMoveException as e:
                if e.reason == CantMoveException.TooBig:
                    ui.message("%s won't fit %s!" % (thing_to_move.name, target_location.description))
                    return
                if e.reason == CantMoveException.CantTraverse:
                    ui.message("%s can't go %s..." % (thing_to_move.name, target_location.description))
                    return
                if e.reason == CantMoveException.CantContain:
                    ui.message("%s can't contain %s." % (target_location.description, thing_to_move.name))
                    return
                ui.message("Can't move %s to %s" % (thing_to_move.name, target_location.description))


def examine_thing(thing):
    ui.message(thing.name)
    ui.message("=" * len(thing.name))
    ui.message('')
    ui.message('%s...' % thing.name)
    for location in get_all_locations(thing):
        if location.things:
            ui.message('  %s you find...' % location.name)
            for content in location.things:
                ui.message('    %s' % content.name)
    for prop in thing.properties.values():
        if prop.description:
            ui.message('  %s' % prop.description)
    # ui.message(size)
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
        ui.message('  is %s' % sizes[thing.size])
    if thing.material is not None and thing.material.name:
        ui.message('  is made of %s' % thing.material.name)

    ui.message('')


def describe_location(location):
    ui.message(location.name)
    ui.message("=" * len(location.name))
    ui.message("You see here...")
    accessible_things = [a for a in get_accessible_things(player)]
    nearest_things = [t for t in accessible_things if t.location == player.location]
    for thing in nearest_things:
        contained_things = [t for t in accessible_things if t.location in thing.locations]
        ui.message('  * %s' % thing.name)
        for contained_thing in contained_things:
            ui.message('    * %s (%s)' % (contained_thing.name, contained_thing.location.name))

    ui.message("There are exits to...")
    for exit in location.exits:
        ui.message('   > %s' % exit.to_location.name)
    ui.message('')


def thing_name_with_location(thing):
    if thing.location == player.location:
        return thing.name
    else:
        return "%s (%s)" % (thing.name, thing.location.name)


def tick_world():
    process_tick_events(world)
    process_event_queue(world)


def iterate():
    ui.refresh()
    action = ui.get_char()
    if action == 'g':
        all_exits = player.location.get_all_exits()
        # filter out exits that can't be accessed
        all_exits = [
            e for e in all_exits if e.can_traverse(player) and e.to_location.can_contain(player)
        ]
        which_exit = letter_prompt(all_exits, "Go where?", lambda x: x.description)
        if which_exit:
            ui.message("")
            player.tell("You go %s...\n" % which_exit.description)
            which_exit.to_location.add_thing(player)
            describe_location(player.location)
    elif action == 'd':
        action_prompt_v1()
        # action_prompt_v2()
    elif action == 'm':
        move_prompt()
    elif action == 'e':
        accessible_things = [t for t in get_accessible_things(player)]
        choice = letter_prompt(accessible_things, 'Examine what?', thing_name_with_location)
        if choice:
            ui.message('')
            examine_thing(choice)
    elif action == 'i':
        describe_location(player.get_property(Inventory).locations.values()[0])
    elif action == 'l':
        describe_location(player.location)
    elif action == 'w':
        ui.message("time passes...")
    elif action == 'pdb':
        import pdb
        pdb.set_trace()
    elif action == 'ESC':
        response = ui.prompt("Really quit?", [('y', 'Yes', True), ('n', 'No', False)])
        if response:
            sys.exit()
    tick_world()


def game_loop(scr):
    ui.init(scr)
    describe_location(player.location)
    while True:
        try:
            iterate()
        except Exception as e:
            import traceback
            ui.message("EXCEPTION: %s" % traceback.format_exc(e))


if __name__ == "__main__":
    curses.wrapper(game_loop)

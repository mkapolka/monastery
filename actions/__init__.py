from actions import *

import sys
import inspect
sys.modules[__name__]

actions = []
for name, obj in inspect.getmembers(sys.modules[__name__]):
    if inspect.isclass(obj) and issubclass(obj, Action) and obj != Action:
        actions.append(obj)


def actions_for_thing(thing):
    output = []
    for action in actions:
        if not action.prereq or thing.is_property(action.prereq):
            output.append(action)
    return output

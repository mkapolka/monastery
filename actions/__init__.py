from actions import *
from collections import defaultdict

import sys
import inspect
sys.modules[__name__]

action_table = defaultdict(list)
for name, obj in inspect.getmembers(sys.modules[__name__]):
    if inspect.isclass(obj) and issubclass(obj, Action) and obj != Action:
        action_table[obj.prereq].append(obj)


def actions_for_thing(thing):
    output = []
    for prop in thing.properties.values():
        output.extend(action_table.get(prop.__class__, []))

    return output

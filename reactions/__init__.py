from reactions import *

import sys, inspect
sys.modules[__name__]

reaction_table = []
for name, obj in inspect.getmembers(sys.modules[__name__]):
    if inspect.isclass(obj) and issubclass(obj, Reaction) and obj != Reaction:
        reaction_table.append(obj)

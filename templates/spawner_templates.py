from enums import Size
from templates import Template
import properties.spawner as sp
import properties.materials as m


class MouseHole(Template):
    name = 'a mouse nest'
    properties = [sp.SpawnsMice]
    size = Size.small
    material = m.Plant

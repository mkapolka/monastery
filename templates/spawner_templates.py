from enums import Size
from templates import Template
import properties.spawner as sp
import properties.materials as m
import properties.location_properties as lp


class MouseHole(Template):
    name = 'a mouse nest'
    properties = [sp.SpawnsMice]
    size = Size.small
    material = m.Wood


class RabbitHole(Template):
    name = 'a rabbit den'
    properties = [sp.SpawnsRabbits, lp.IsContainer, lp.Open]
    size = Size.small
    material = m.Plant

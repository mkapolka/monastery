from enums import Size
from templates import Template
import templates as t
import properties.spawner as sp
import properties.materials as m
import properties.location_properties as lp
import properties as p


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


class Well(Template):
    name = "a well"
    size = Size.medium
    properties = [sp.SpringsWater, p.IsContainer, p.Open]
    material = m.Stone
    contents = {
        lp.IsContainer: [
            t.Water
        ]
    }

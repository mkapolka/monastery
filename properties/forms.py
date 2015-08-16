from form import Form
import properties as p
import location_properties as lp


class Creature(Form):
    properties = [lp.HasStomach, p.Breathes]


class Shrub(Form):
    properties = [p.Pinchable, p.Immobile]

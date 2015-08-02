from properties import *
from location_properties import *
from form import Form

class Teapot(Form):
    properties = [IsContainer, Openable]

class Human(Form):
    properties = [HasStomach]

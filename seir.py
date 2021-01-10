import enum


class Seir(enum.Enum):
    """Enum representing agent infection status according to SEIR model"""
    SUSCEPTIBLE, EXPOSED, INFECTED, RECOVERED = range(4)

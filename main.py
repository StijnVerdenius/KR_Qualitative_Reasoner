from copy import deepcopy
from itertools import product, combinations
import numpy as np
import math
from graphviz import Digraph

from model.QualitativeReasoner import QualatitiveReasoning
from model.classes import *
from data.constants import *


def main():
    tap = Entity("tap")
    container = Entity("container")
    sink = Entity("sink")
    entities = [tap, container, sink]

    er1 = EntityRelation("Above of", tap, container)
    er2 = EntityRelation("In bottom of", sink, container)

    inflow = Quantity("inflow", NULL, (NULL, POS))
    outflow = Quantity("outflow", NULL, (NULL, POS, MAX))
    volume = Quantity("volume", NULL, (NULL, POS, MAX))
    quantities = [inflow, volume, outflow]

    i1 = Influence(False, outflow, volume)
    i2 = Influence(True, inflow, volume)
    p1 = Proportional(True, volume, outflow)

    value_constraint = ValueConstraint(True, volume, outflow)

    outflow.set_outgoing_quantity_relation(i1)
    outflow.set_incoming_quantity_relation(p1)
    inflow.set_outgoing_quantity_relation(i2)
    volume.set_incoming_quantity_relation(i1)
    volume.set_incoming_quantity_relation(i2)

    system = QualatitiveReasoning(entities, quantities, [value_constraint])
    system.solve()





if __name__ == "__main__":
    main()

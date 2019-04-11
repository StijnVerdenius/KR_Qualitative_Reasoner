from copy import deepcopy
from itertools import product, combinations
import numpy as np
import math
from graphviz import Digraph

from model.QualitativeReasoner import QualatitiveReasoning
from model.classes import *
from data.constants import *
import json
import sys

from trace import Trace

def load_system(filename):

    """
    loads sysemt from file

    :return:
    """

    problem = json.loads(open(f"./data/{filename}.json", "r").read())

    entities = []
    quantities = []
    value_constraints = []
    entity_relations = []
    quantity_relations = []

    entities_lookup = {}
    quantities_lookup = {}
    value_constraints_lookup = {}
    entity_relations_lookup = {}
    quantity_relations_lookup = {}

    for entity_def in problem["entities"]:
        entity = Entity(entity_def["name"])
        entities.append(entity)
        entities_lookup[entity.name] = entity

    for entity_relation_def in problem["entity_relations"]:
        entity_relation = EntityRelation(entity_relation_def["name"], entities_lookup[entity_relation_def["from"]],
                                         entities_lookup[entity_relation_def["to"]])
        entity_relations.append(entity_relation)
        entity_relations_lookup[entity_relation.name] = entity_relation

    for quantity_def in problem["quantities"]:
        quantity = Quantity(quantity_def["name"], readout_constants(quantity_def["possible_magnitudes"]),
                            randomized=quantity_def["random_allowed"])
        quantities.append(quantity)
        quantities_lookup[quantity.name] = quantity

    for value_constraint_def in problem["value_constraints"]:
        value_constraint = ValueConstraint(value_constraint_def["sign"],
                                           quantities_lookup[value_constraint_def["from"]],
                                           quantities_lookup[value_constraint_def["to"]])
        value_constraints.append(value_constraint)
        value_constraints_lookup[
            value_constraint.quantity_from.name + "_" + value_constraint.quantity_to.name] = value_constraint

    for relation_def in problem["relations"]:
        relation = None
        if (relation_def["type"] == "Influence"):
            relation = Influence(relation_def["sign"], quantities_lookup[relation_def["from"]],
                                 quantities_lookup[relation_def["to"]])
        elif (relation_def["type"] == "Proportion"):
            relation = Proportional(relation_def["sign"], quantities_lookup[relation_def["from"]],
                                    quantities_lookup[relation_def["to"]])
        else:
            raise Exception("unknown relationtype: " + relation_def["type"])

        quantity_relations.append(relation)
        quantity_relations_lookup[relation.quantity_from.name + "_" + relation.quantity_to.name] = relation
        quantities_lookup[relation.quantity_from.name].set_outgoing_quantity_relation(relation)
        quantities_lookup[relation.quantity_to.name].set_incoming_quantity_relation(relation)

    return QualatitiveReasoning(entities, quantities, value_constraints)


def main():

    print("If you wish to change the problem being solved, please alter the json-files in the data folder")

    try:
        filename = sys.argv[1]
    except:
        filename = "sink_problem"

    try:
        use_path = sys.argv[2]
    except:
        use_path = False

    system = load_system(filename)
    graph, all_states, states_ordered = system.solve()

    start = {key : tuple(value) for key, value in json.loads(open("./data/start_state.json", "r").read()).items()}
    target = {key : tuple(value) for key, value in json.loads(open("./data/target_state.json", "r").read()).items()}

    random_state = states_ordered[0]

    start_graph_node = tuple([start[key] for key in random_state.key_order])
    target_graph_node = tuple([target[key] for key in random_state.key_order])

    tracer = Trace(start_graph_node, target_graph_node, graph)
    trace_path = tracer.a_star()

    if (trace_path is False):
        print("No path found between start and target")
        use_path = False

    # Visualize the resulting graph.
    system.visualize(graph, all_states, states_ordered, trace_path, use_path, start_graph_node, target_graph_node)

    sys.exit(0)





if __name__ == "__main__":
    main()

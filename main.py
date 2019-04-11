from copy import deepcopy
from itertools import product, combinations
import numpy as np
import math
from graphviz import Digraph

from model.QualitativeReasoner import QualatitiveReasoning
from model.classes import *
from data.constants import *
import json


def main():

    print("If you wish to change the problem being solved, please alter the json-files in the data folder")

    problem = json.loads(open("./data/sink_problem.json", "r").read()) #todo : via commandline

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
        entity_relation = EntityRelation(entity_relation_def["name"], entities_lookup[entity_relation_def["from"]], entities_lookup[entity_relation_def["to"]])
        entity_relations.append(entity_relation)
        entity_relations_lookup[entity_relation.name] = entity_relation

    for quantity_def in problem["quantities"]:
        quantity = Quantity(quantity_def["name"], readout_constants(quantity_def["possible_magnitudes"]), randomized=quantity_def["random_allowed"])
        quantities.append(quantity)
        quantities_lookup[quantity.name] = quantity

    for value_constraint_def in problem["value_constraints"]:
        value_constraint = ValueConstraint(value_constraint_def["sign"], quantities_lookup[value_constraint_def["from"]], quantities_lookup[value_constraint_def["to"]])
        value_constraints.append(value_constraint)
        value_constraints_lookup[value_constraint.quantity_from.name+"_"+value_constraint.quantity_to.name] = value_constraint

    for relation_def in problem["relations"]:
        relation = None
        if (relation_def["type"] == "Influence"):
            relation = Influence(relation_def["sign"], quantities_lookup[relation_def["from"]], quantities_lookup[relation_def["to"]])
        elif (relation_def["type"] == "Proportion"):
            relation = Proportional(relation_def["sign"], quantities_lookup[relation_def["from"]], quantities_lookup[relation_def["to"]])
        else:
            raise Exception("unknown relationtype: "+ relation_def["type"])

        quantity_relations.append(relation)
        quantity_relations_lookup[relation.quantity_from.name + "_" + relation.quantity_to.name] = relation
        quantities_lookup[relation.quantity_from.name].set_outgoing_quantity_relation(relation)
        quantities_lookup[relation.quantity_to.name].set_incoming_quantity_relation(relation)


    system = QualatitiveReasoning(entities, quantities, value_constraints)
    graph, all_states, states_ordered = system.solve()

    start = json.loads(open("./data/start_state.json", "r").read())
    target = json.loads(open("./data/target_state.json", "r").read())





if __name__ == "__main__":
    main()

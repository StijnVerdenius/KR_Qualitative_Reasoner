from typing import List, Tuple, Dict, Any
from copy import deepcopy
from itertools import product, combinations
import numpy as np
import math
from graphviz import Digraph

MIN, NEG, NULL, POS, MAX = -2, -1, 0, 1, 2


def main():
    tap = Entity("tap")
    container = Entity("container")
    sink = Entity("sink")
    entities = [tap, container, sink]

    er1 = EntityRelation("Above of", tap, container)
    er2 = EntityRelation("In bottom of", sink, container)
    entity_relations = [er1, er2]

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

    quantity_relations = [i1, i2, p1]

    system = QualatitiveReasoning(entities, entity_relations, quantities, quantity_relations, [value_constraint])
    system.solve()




class Entity:
    def __init__(self, name: str):
        self.name = name


class EntityRelation:
    def __init__(self, name: str, entity_from: Entity, entity_to: Entity):
        self.name = name
        self.entity_from = entity_from
        self.entity_to = entity_to


class QuantityRelation:
    def __init__(self, sign: bool, q_from: 'Quantity', q_to: 'Quantity'):
        self.sign = -(not int(sign)) + int(sign)
        self.quantity_from = q_from
        self.quantity_to = q_to


class Quantity:

    outgoing_quantity_relations: List[QuantityRelation]
    incoming_quantity_relations: List[QuantityRelation]

    def __init__(self, name: str, initial_value: int, possible_values: Tuple = (NULL), initial_derivative: int = NULL, possible_derivatives: Tuple = (NEG, NULL, POS)):
        self.possible_magnitudes = possible_values
        self.initial_value = initial_value
        self.possible_derivatives = possible_derivatives
        self.initial_derivative = initial_derivative
        self.derivative = 0
        self.name = name
        self.incoming_quantity_relations = []
        self.outgoing_quantity_relations = []

    def set_outgoing_quantity_relation(self, quantiy_relation: QuantityRelation):
        self.outgoing_quantity_relations.append((quantiy_relation, quantiy_relation.quantity_to))

    def set_incoming_quantity_relation(self, quantiy_relation: QuantityRelation):
        self.incoming_quantity_relations.append((quantiy_relation, quantiy_relation.quantity_from))

    def get_current_value_and_derivative(self):
        return (self.initial_value, self.initial_derivative)

class State:

    def __init__(self, quantities: List[Quantity], values: List[Tuple[int, int]]):
        self.id = tuple(values)
        self.values = {quantity.name: values[i] for i, quantity in enumerate(quantities)}
        self.key_order = [quantity.name for quantity in quantities]

    def reload_id(self):
        self.id = tuple(self.values[name] for name in self.key_order)

    def __repr__(self):
        return str({a: b for a,b in zip (self.key_order, self.id)})

    def equals(self, state: 'State') -> bool:
        return self.id == state.id

    def visual(self):
        builder = ""
        for i, element in enumerate(self.id):
            builder += self.key_order[i] + " " + (str(element)+"\n")
        return builder



class ValueConstraint(QuantityRelation):

    def __init__(self, sign: bool, q_from: 'Quantity', q_to: 'Quantity'):
        super().__init__(sign, q_from, q_to)



class Influence(QuantityRelation):


    def __init__(self, sign: bool, q_from: 'Quantity', q_to: 'Quantity'):
        super().__init__(sign, q_from, q_to)





class Proportional(QuantityRelation):
    def __init__(self, sign: bool, q_from: 'Quantity', q_to: 'Quantity'):
        super().__init__(sign, q_from, q_to)




class QualatitiveReasoning:

    entities: List[Entity]
    entity_relations: List[EntityRelation]
    quantities: List[Quantity]
    quantity_relations: List[QuantityRelation]

    def __init__(self,
                 entities: List[Entity],
                 entity_relations: List[EntityRelation],
                 quantities: List[Quantity],
                 quantity_relations: List[QuantityRelation],
                 value_constraints : List[ValueConstraint]
                 ):

        self.entities = entities
        self.entity_relations = entity_relations
        self.quantities = quantities
        self.quantity_relations = quantity_relations
        self.value_constraints = value_constraints

    def solve(self):

        possible_values = set()

        for quantity in self.quantities:

            magnitudes = quantity.possible_magnitudes
            derivatives = quantity.possible_derivatives

            possible_values.update(magnitudes)
            possible_values.update(derivatives)

        big_matrix = list(product(possible_values, repeat=2*len(self.quantities)))

        print(np.array(big_matrix).shape)

        transfer_matrix = []

        for entry in big_matrix:

            if (self.is_valid(entry)):
                transfer_matrix.append(entry)

        states = []

        for state in transfer_matrix:
            states.append(State(self.quantities, [tuple((state[i*2], state[i*2 + 1])) for i in range(len(self.quantities))]))

        for st in states:
            print(st)

        graaf, all_states = self.generate_graph(states)

        for grap in graaf:

            print(grap, "\t\t:\t\t",  graaf[grap])

        self.visualize(graaf, all_states)






    def is_valid(self, entry):

        for i, number in enumerate(entry):

            # only look at pairs
            is_magnitude = (i %2 == 0)
            if (not is_magnitude):
                continue

            # find relevant values
            quantity = self.quantities[math.floor(i/2)]
            comparison_magnitudes = quantity.possible_magnitudes
            comparison_derivatives = quantity.possible_derivatives
            derivative = entry[i + 1]
            magnitude = number

            # wrong value assignments to columns in matrix
            if ((not derivative in comparison_derivatives) or (not magnitude in comparison_magnitudes)):
                return False

            # max or min situations
            index_derivative = quantity.possible_derivatives.index(derivative)
            index_magnitude = quantity.possible_magnitudes.index(magnitude)
            try:
                index_middle_derivative = quantity.possible_derivatives.index(0) # find the 'nothings happening' derivative
            except ValueError:
                index_middle_derivative = int(len(quantity.possible_derivatives)/2) # estimation

            # magnitude is max and derivative is still positive
            if (magnitude == MAX and index_derivative > index_middle_derivative):
                return False
            # magnitude is min and derivative is still negative
            elif (index_magnitude == 0 and index_derivative < index_middle_derivative):
                return False

            # value constraints
            for value_constraint in self.value_constraints:
                constraint_names = {q.name : q for q in [value_constraint.quantity_from, value_constraint.quantity_to]}
                if (quantity.name in constraint_names):

                    del constraint_names[quantity.name]

                    other_quantity = next(iter(constraint_names.values()))

                    other_quantity_index = self.quantities.index(other_quantity)

                    magnitude_other = entry[other_quantity_index*2]

                    if (not magnitude == magnitude_other):
                        return False

            # influences and proportionals
            relations = quantity.incoming_quantity_relations
            signs = set()
            for r, quantity_from in relations:
                quant_index = self.quantities.index(r.quantity_from)
                magnitude_from = entry[quant_index * 2]
                derivative_from = entry[quant_index * 2 + 1]
                if isinstance(r, Influence):
                    signs.add(r.sign * int(magnitude_from != 0))
                else:
                    signs.add(r.sign * derivative_from)

            # If ambugity
            if -1 in signs and 1 in signs: # (0 could also be in it)
                continue
            elif -1 in signs and derivative != -1:
                return False
            elif 1 in signs and derivative != 1:
                return False
            elif 0 in signs and len(signs) == 1 and derivative != 0:
                return False



        return True

    def apply_derivatives(self, state, quantity_names):
        """
        Applies derivatives to current magnitudes

        :param state:
        :return:
        """

        for quantity_name in quantity_names:

            derivative = state.values[quantity_name][1]
            magnitue = state.values[quantity_name][0]

            corresponidng_quantity = None

            for q in self.quantities:
                if q.name==quantity_name:
                    corresponidng_quantity = q
                    break

            possible = corresponidng_quantity.possible_magnitudes

            index_now = possible.index(magnitue)

            index_new = index_now + derivative

            if index_new >= len(possible):

                index_new = len(possible)-1

            elif (index_new < 0):

                index_new = 0

            new_tuple = (possible[index_new], derivative)

            state.values[quantity_name] = new_tuple

            state.reload_id()



    def generate_graph(self, states):
        existing_states = {state.id :  state for state in states}
        graph = {state.id : set() for state in states}

        added_new_connection = True

        name_product = [combi for z in range(1, 4) for combi in combinations([q.name for q in self.quantities], z)]

        while (added_new_connection):

            added_new_connection = False

            for state in states:

                inflow_derivative = state.values["inflow"][1]

                possibilities_inflow = [x for x in range(-1, 2) if abs(x - inflow_derivative) < 2]

                for name_combi in name_product:
                    for possible_inflow in possibilities_inflow:

                        new_state = deepcopy(state)

                        self.apply_derivatives(new_state, name_combi)

                        self.appy_relations(new_state)

                        if ("inflow" in name_combi):

                            new_state.values["inflow"] = (new_state.values["inflow"][0], possible_inflow)

                            new_state.reload_id()

                        if ((new_state.id not in existing_states)): continue
                        if ((new_state.id in graph[state.id])): continue
                        if ((state.id == new_state.id)): continue

                        graph[state.id].add(new_state.id)

                        added_new_connection = True

        return graph, existing_states

    def visualize(self, graph_, all_states):

        graph = Digraph(comment='The Qualitative Model')
        graph.node_attr.update(color='lightblue2', style='filled')

        for i, (state, connect_to) in enumerate(graph_.items()):

            graph.node(str(all_states[state].visual()), label=str(i)+"\n\n"+str(all_states[state].visual()))

            for connection_state in connect_to:

                graph.edge(str(all_states[state].visual()), str(all_states[connection_state].visual()))

        graph.view()

        return True

    def appy_relations(self, new_state):

        for quantity_name, (magnitude, derivative) in new_state.values.items():

            corresponidng_quantity = None

            for q in self.quantities:
                if q.name == quantity_name:
                    corresponidng_quantity = q
                    break

            # influences and proportionals
            relations = corresponidng_quantity.incoming_quantity_relations
            signs = set()
            for r, quantity_from in relations:

                magnitude_from, derivative_from = new_state.values[quantity_from.name]

                if isinstance(r, Influence):
                    signs.add(r.sign * int(magnitude_from != 0))
                else:
                    signs.add(r.sign * derivative_from)

            new_derivative = None

            # If ambugity
            if -1 in signs and 1 in signs:  # (0 could also be in it)
                continue
            elif -1 in signs and derivative != -1:
                new_derivative = -1
            elif 1 in signs and derivative != 1:
                new_derivative = 1
            elif 0 in signs and len(signs) == 1 and derivative != 0:
                new_derivative = 0
            else:
                continue

            new_tuple = (magnitude, new_derivative)

            new_state.values[quantity_name] = new_tuple

        new_state.reload_id()


if __name__ == "__main__":
    main()

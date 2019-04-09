from typing import List, Tuple, Dict
from copy import deepcopy
from itertools import product
import numpy as np
import math


def main():
    tap = Entity("tap")
    container = Entity("container")
    sink = Entity("sink")
    entities = [tap, container, sink]

    er1 = EntityRelation("Above of", tap, container)
    er2 = EntityRelation("In bottom of", sink, container)
    entity_relations = [er1, er2]

    inflow = Quantity("inflow", 0, (0, "+"))
    outflow = Quantity("outflow", 0, (0, "+", "max"))
    volume = Quantity("volume", 0, (0,"+", "max"))
    quantities = [inflow, volume, outflow]

    i1 = Influence(False, outflow, volume)
    i2 = Influence(True, inflow, volume)
    p1 = Proportional(True, volume, outflow)

    value_constraint = ValueConstraint(True, volume, outflow)

    # TODO: Maybe refactor to do this automatically
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

    def __init__(self, name: str, initial_value: int, possible_values: Tuple = (0), initial_derivative: int = 0, possible_derivatives: Tuple = (-1, 0, 1)):
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
            print(state)
            states.append(State(self.quantities, [tuple((state[i*2], state[i*2 + 1])) for i in range(len(self.quantities))]))

        for st in states:
            print(st.id)

        print(np.array(states).shape)





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
            if (index_magnitude == len(quantity.possible_magnitudes)-1 and index_derivative > index_middle_derivative):
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
        return True


if __name__ == "__main__":
    main()

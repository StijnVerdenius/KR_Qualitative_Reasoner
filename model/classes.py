from typing import List, Tuple, Union
from data.constants import *


class Entity:
    """ Class representing a entity in the domain. """
    name: str

    def __init__(self, name: str):
        self.name = name


class EntityRelation:
    """ A relation between two entities """
    entity_to: Entity
    entity_from: Entity
    name: str

    def __init__(self, name: str, entity_from: Entity, entity_to: Entity):
        self.name = name
        self.entity_from = entity_from
        self.entity_to = entity_to


class QuantityRelation:
    """ A quantity relation between two quantities"""
    quantity_to: 'Quantity'
    quantity_from: 'Quantity'
    sign: int

    def __init__(self, sign: bool, q_from: 'Quantity', q_to: 'Quantity'):
        self.sign = -(not int(sign)) + int(sign)
        self.quantity_from = q_from
        self.quantity_to = q_to


class Influence(QuantityRelation):
    """ Influence Quantity Relation"""

    def __init__(self, sign: bool, q_from: 'Quantity', q_to: 'Quantity'):
        super().__init__(sign, q_from, q_to)


class Proportional(QuantityRelation):
    """ Proportional Quantity Relation"""

    def __init__(self, sign: bool, q_from: 'Quantity', q_to: 'Quantity'):
        super().__init__(sign, q_from, q_to)


class ValueConstraint(QuantityRelation):
    """ A Value constraint that constraints the values between two quantities"""

    def __init__(self, sign: bool, q_from: 'Quantity', q_to: 'Quantity'):
        super().__init__(sign, q_from, q_to)


class Quantity:
    """ Quantity class
    contains a name, possible_values, possible_derivatives and relations ingoing and outgoing
    """
    outgoing_quantity_relations: List[Tuple[QuantityRelation, 'Quantity']]
    incoming_quantity_relations: List[Tuple[QuantityRelation, 'Quantity']]

    def __init__(self, name: str, possible_values: Tuple = (NULL), initial_derivative: int = NULL, possible_derivatives: Tuple = (NEG, NULL, POS)):
        self.possible_magnitudes = possible_values
        self.possible_derivatives = possible_derivatives
        self.initial_derivative = initial_derivative
        self.name = name
        self.incoming_quantity_relations = []
        self.outgoing_quantity_relations = []

    def set_outgoing_quantity_relation(self, quantiy_relation: QuantityRelation):
        self.outgoing_quantity_relations.append((quantiy_relation, quantiy_relation.quantity_to))

    def set_incoming_quantity_relation(self, quantiy_relation: QuantityRelation):
        self.incoming_quantity_relations.append((quantiy_relation, quantiy_relation.quantity_from))


class State:
    """ Class that represents a current state in the Qualitatitve Reasoning engine """

    def __init__(self, quantities: List[Quantity], values: List[Tuple[int, int]]):
        self.id = tuple(values)
        self.values = {quantity.name: values[i] for i, quantity in enumerate(quantities)}
        self.key_order = [quantity.name for quantity in quantities]

    def reload_id(self):
        self.id = tuple(self.values[name] for name in self.key_order)

    def __repr__(self):
        return str({a: b for a, b in zip(self.key_order, self.id)})

    def equals(self, state: 'State') -> bool:
        return self.id == state.id

    def visual(self):
        builder = ""
        for i, element in enumerate(self.id):
            builder += self.key_order[i] + " " + (str(element) + "\n")
        return builder

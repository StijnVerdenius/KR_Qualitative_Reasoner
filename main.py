from typing import List


def main():
    tap = Entity("tap")
    container = Entity("container")
    sink = Entity("sink")
    entities = [tap, container, sink]

    er1 = EntityRelation("Above of", tap, container)
    er2 = EntityRelation("In bottom of", sink, container)
    ers = [er1, er2]

    outflow = Quantity("outflow", 0, [0, 1])
    inflow = RandomQuantity("inflow", 0, [0, 1])
    volume = Quantity("volume", 0, [-1, 0, 1])
    quantities = [outflow, inflow, volume]

    i1 = Influence(False, outflow, volume)
    i2 = Influence(True, inflow, volume)
    p1 = Proportional(True, volume, outflow)

    # TODO: Maybe refactor to do this automatically
    outflow.set_outgoing_quantity_relation(i1)
    outflow.set_incoming_quantity_relation(p1)
    inflow.set_outgoing_quantity_relation(i2)
    volume.set_incoming_quantity_relation(i1)
    volume.set_incoming_quantity_relation(i2)

    quantity_relations = [i1, i2, p1]

    system = QualatitiveReasoning(entities, ers, quantities, quantity_relations)
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
        self.sign = sign
        self.quantity_from = q_from
        self.quantity_to = q_to


class Quantity:
    def __init__(self, name: str, initial_value: int, possible_values: List = [-1, 0, 1]):
        self.possible_values = possible_values
        self.initial_value = initial_value
        self.derivative = 0
        self.name = name
        self.incoming_quantity_relations = []
        self.outgoing_quantity_relations = []

    def set_outgoing_quantity_relation(self, quantiy_relation: QuantityRelation):
        self.outgoing_quantity_relations.append((quantiy_relation, quantiy_relation.quantity_to))

    def set_incoming_quantity_relation(self, quantiy_relation: QuantityRelation):
        self.incoming_quantity_relations.append((quantiy_relation, quantiy_relation.quantity_from))


class RandomQuantity(Quantity):
    pass

class Influence(QuantityRelation):
    pass


class Proportional(QuantityRelation):
    pass


class QualatitiveReasoning:
    entities: List[Entity]
    entity_relations: List[EntityRelation]
    quantities: List[Quantity]
    quantity_relations: List[QuantityRelation]

    def __init__(self, entities: List[Entity], entity_relations: List[EntityRelation], quantities: List[Quantity], quantity_relations: List[QuantityRelation]):
        self.entities = entities
        self.entity_relations = entity_relations
        self.quantities = quantities
        self.quantity_relations = quantity_relations

    def solve(self):
        unique_states = {}
        state_transitions = {}

        current_state = 1

        # TODO: Implement deze shit
        for quantity in self.quantities:
            # Determine quantity value in current state:
            for quantity_relation in self.quantity_relations:
                pass










if __name__ == "__main__":
    main()

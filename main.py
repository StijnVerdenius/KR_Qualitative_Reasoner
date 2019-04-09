from typing import List, Tuple, Dict
from copy import deepcopy


def main():
    tap = Entity("tap")
    container = Entity("container")
    sink = Entity("sink")
    entities = [tap, container, sink]

    er1 = EntityRelation("Above of", tap, container)
    er2 = EntityRelation("In bottom of", sink, container)
    entity_relations = [er1, er2]

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

    system = QualatitiveReasoning(entities, entity_relations, quantities, quantity_relations)
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

    def impose_relation(self, state):
        pass

class Quantity:

    def __init__(self, name: str, initial_value: int, possible_values: Tuple =(-1, 0, 1), initial_derivative: int = -1, possible_derivatives: Tuple = (-1, 0, 1)):
        self.possible_values = possible_values
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





class RandomQuantity(Quantity):
    pass

class Influence(QuantityRelation):


    def __init__(self, sign: bool, q_from: 'Quantity', q_to: 'Quantity'):
        super().__init__(sign, q_from, q_to)

    def impose_relation(self, state: State):

        direction = state.values[self.quantity_from.name][0]*self.sign

        derivative_now = state.values[self.quantity_to.name][1]

        magnitude_now = state.values[self.quantity_to.name][0]

        possible = self.quantity_to.possible_derivatives

        index_now = possible.index(derivative_now)

        index_new = index_now + direction

        if index_new >= len(possible):

            index_new = len(possible)

        elif (index_new < 0):

            index_new = 0

        new_tuple = (magnitude_now, possible[index_new])

        state.values[self.quantity_to] = new_tuple

        state.reload_id()

        return (not index_new == index_now)



class Proportional(QuantityRelation):
    def __init__(self, sign: bool, q_from: 'Quantity', q_to: 'Quantity'):
        super().__init__(sign, q_from, q_to)

    def impose_relation(self, state: State):

        direction = state.values[self.quantity_from.name][1]*self.sign

        derivative_now = state.values[self.quantity_to.name][1]
        magnitude_now = state.values[self.quantity_to.name][0]

        possible = self.quantity_to.possible_derivatives

        index_now = possible.index(derivative_now)

        index_new = index_now + direction

        if index_new >= len(possible):

            index_new = len(possible)

        elif (index_new < 0):

            index_new = 0

        new_tuple = (magnitude_now, possible[index_new])

        state.values[self.quantity_to] = new_tuple

        state.reload_id()

        return (not index_new == index_now)


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
                 ):

        self.entities = entities
        self.entity_relations = entity_relations
        self.quantities = quantities
        self.quantity_relations = quantity_relations

    def solve(self):

        current_state = State(self.quantities, [x.get_current_value_and_derivative() for x in self.quantities])

        unique_states = {current_state.id : current_state}
        state_transitions = {}

        stack = [current_state]

        while(len(stack) > 0):

            current_state = stack.pop()

            state_transitions[current_state.id] = set()

            for new_state in self.generate_possibilities(current_state).values():

                if new_state.id == current_state.id:
                    continue

                state_transitions[current_state.id].add(new_state.id)

                if (not new_state.id in unique_states):
                    unique_states[new_state.id] = new_state
                    stack.append(new_state)

        print(unique_states)
        print(state_transitions)



    def generate_possibilities(self, current_state):


        temp_state = deepcopy(current_state)

        self.apply_derivatives(temp_state)

        return self.ensure_consistencies(temp_state)


    def ensure_consistencies(self, state):
        """
        applies relations and finds inconsistencies

        :param state:
        :return:
        """

        output = {}

        for relation in self.quantity_relations:

            new_state = deepcopy(state)

            changed = relation.impose_relation(new_state)

            if (changed):
                output[new_state.id] = new_state

        return self.merge(output, state)

    def merge(self, changed, state):
        """
        merges possible states

        :param changed:
        :param state:
        :return:
        """

        if (len(changed) == 0):
            return {state.id : state}

        possibilities = {} # HIER ZIT IK EEN BEETJE VAST

        return changed

        return possibilities


    def apply_derivatives(self, state):
        """
        Applies derivatives to current magnitudes

        :param state:
        :return:
        """

        for quantity_name in state.values:

            derivative = state.values[quantity_name][1]
            magnitue = state.values[quantity_name][0]

            corresponidng_quantity =None

            for q in self.quantities:
                if q.name==quantity_name:
                    corresponidng_quantity = q
                    break

            possible = corresponidng_quantity.possible_values

            index_now = possible.index(magnitue)

            index_new = index_now + derivative

            if index_new >= len(possible):
                index_new = len(possible)

            elif (index_new < 0):

                index_new = 0

            new_tuple= (possible[index_new], derivative)

            state.values[quantity_name] = new_tuple

            state.reload_id()


if __name__ == "__main__":
    main()

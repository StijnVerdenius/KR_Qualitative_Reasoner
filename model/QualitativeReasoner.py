from copy import deepcopy
from itertools import product, combinations
import numpy as np
import math
from graphviz import Digraph
from model.classes import *
from data.constants import *


class QualitativeReasoning:
    """ Qualitative Reasoning engine """
    entities: List[Entity]
    quantities: List[Quantity]

    def __init__(self, entities: List[Entity], quantities: List[Quantity], value_constraints: List[ValueConstraint]):

        self.entities = entities
        self.quantities = quantities
        self.value_constraints = value_constraints
        self.random_variables = []

        # keep track of which variables kan change derivative randomly
        for quantity in quantities:
            if (quantity.randomized):
                self.random_variables.append(quantity.name)

    def solve(self):
        """
        solves the QR system

        :return:
        """

        # Get all possible values defined as all possible values for magnitudes/derivatives in the program
        possible_values = set()
        for quantity in self.quantities:
            magnitudes = quantity.possible_magnitudes
            derivatives = quantity.possible_derivatives

            possible_values.update(magnitudes)
            possible_values.update(derivatives)

        # Build all possible states with all possible values they could potentially take
        # This is done by taking every possibility and then filtering out the non-sense ones.
        possibilities_matrix = list(product(possible_values, repeat=2 * len(self.quantities)))
        transfer_matrix = []
        for entry in possibilities_matrix:
            if (self.is_valid(entry)):
                transfer_matrix.append(entry)

        # Append these states from the transfer_matrix to a state list.
        states_ordered = []
        for state in transfer_matrix:
            states_ordered.append(State(self.quantities, [tuple((state[i * 2], state[i * 2 + 1])) for i in range(len(self.quantities))]))

        # Generate a graph from the remaining valid states.
        graph, all_states = self.generate_graph(states_ordered)

        return graph, all_states, states_ordered



    def is_valid(self, entry) -> bool:
        """
        Returns whether this is a valid 'entry' (a possible state)
        :rtype: bool
        """
        for i, number in enumerate(entry):

            # only look at pairs
            is_magnitude = (i % 2 == 0)
            if not is_magnitude:
                continue

            # find relevant values
            quantity = self.quantities[math.floor(i / 2)]
            comparison_magnitudes = quantity.possible_magnitudes
            comparison_derivatives = quantity.possible_derivatives
            derivative = entry[i + 1]
            magnitude = number

            # wrong value assignments to columns in matrix
            if (not derivative in comparison_derivatives) or (not magnitude in comparison_magnitudes):
                return False

            # max or min situations
            index_derivative = quantity.possible_derivatives.index(derivative)
            index_magnitude = quantity.possible_magnitudes.index(magnitude)
            try:
                index_middle_derivative = quantity.possible_derivatives.index(0)  # find the 'nothings happening' derivative
            except ValueError:
                index_middle_derivative = int(len(quantity.possible_derivatives) / 2)  # estimation

            # magnitude is max and derivative is still positive
            if magnitude == MAX and index_derivative > index_middle_derivative:
                return False
            # magnitude is min and derivative is still negative
            elif index_magnitude == 0 and index_derivative < index_middle_derivative:
                return False

            # value constraints
            for value_constraint in self.value_constraints:
                constraint_names = {q.name: q for q in [value_constraint.quantity_from, value_constraint.quantity_to]}
                if (quantity.name in constraint_names):

                    del constraint_names[quantity.name]

                    other_quantity = next(iter(constraint_names.values()))

                    other_quantity_index = self.quantities.index(other_quantity)

                    magnitude_other = entry[other_quantity_index * 2]

                    if not magnitude == magnitude_other:
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

            # If ambiguity
            if -1 in signs and 1 in signs:  # (0 could also be in it)
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
                if q.name == quantity_name:
                    corresponidng_quantity = q
                    break

            possible = corresponidng_quantity.possible_magnitudes

            index_now = possible.index(magnitue)

            index_new = index_now + derivative

            if index_new >= len(possible):

                index_new = len(possible) - 1

            elif (index_new < 0):

                index_new = 0

            new_tuple = (possible[index_new], derivative)

            state.values[quantity_name] = new_tuple

            state.reload_id()

    def generate_graph(self, states):
        """
        Returns a dictionary of state ids and as values the states it is connected to.
        Secondly returns another dictionary containing all states, with their ids as key
        :rtype: Tuple(graph, existing_states)
        """
        existing_states = {state.id: state for state in states}
        graph = {state.id: set() for state in states}

        added_new_connection = True

        name_product = [combi for z in range(1, 4) for combi in combinations([q.name for q in self.quantities], z)]

        # follow connections untill there are none to be made
        while added_new_connection:

            added_new_connection = False

            for state in states:

                # follow random derivatives
                for name in self.random_variables:

                    name_current_derivative = state.values[name][1]

                    possibilities_name = [x for x in range(-1, 2) if abs(x - name_current_derivative) < 2]

                    for name_combi in name_product:

                        for possibility_name in possibilities_name:

                            new_state = deepcopy(state)

                            # apply derivative
                            self.apply_derivatives(new_state, name_combi)

                            # apply relations once
                            self.appy_relations(new_state)

                            # see if random variables apply
                            if name in name_combi:
                                new_state.values[name] = (new_state.values[name][0], possibility_name)
                                new_state.reload_id()

                            # see if valid edge
                            if new_state.id not in existing_states: continue
                            if new_state.id in graph[state.id]: continue
                            if state.id == new_state.id: continue

                            # add edge
                            graph[state.id].add(new_state.id)

                            added_new_connection = True

        return graph, existing_states

    def visualize(self, graph_, all_states, ordered_states_list, trace_path, use_path, start, target):
        """
        Visualizes state graph using graphviz
        """
        graph = Digraph(comment='The Qualitative Model')
        graph.node_attr.update(color='lightblue2', style='filled')

        for i, state_object in enumerate(ordered_states_list):
            state_id = state_object.id
            connect_to = graph_[state_id]
            graph.node(str(all_states[state_id].visual()), label=str(i) + "\n\n" + str(all_states[state_id].visual()))

            for connection_state in connect_to:
                colour = "black"
                if (use_path):
                    for key, value in trace_path.items():
                        if (value == state_id and key == connection_state):
                            colour = "red"
                            break

                graph.edge(str(all_states[state_id].visual()), str(all_states[connection_state].visual()), color=colour)

        graph.view("./results/result")

        return True

    def appy_relations(self, new_state: State):
        """
        Applies relations in the state and propagates any Influence or Proportional changes/relations to derivatives.
        """
        for quantity_name, (magnitude, derivative) in new_state.values.items():

            corresponding_quantity = None

            for q in self.quantities:
                if q.name == quantity_name:
                    corresponding_quantity = q
                    break

            # Influences and proportional relations
            relations = corresponding_quantity.incoming_quantity_relations
            signs = set()
            for r, quantity_from in relations:

                magnitude_from, derivative_from = new_state.values[quantity_from.name]

                if isinstance(r, Influence):
                    signs.add(r.sign * int(magnitude_from != 0))
                else:
                    signs.add(r.sign * derivative_from)

            # If ambiguity
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

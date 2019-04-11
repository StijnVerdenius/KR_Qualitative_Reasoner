from model.classes import *

class Trace:

    def __init__(self, incoming_state, target_state, graph):

        self.incoming_state = incoming_state
        self.target_state = target_state

        if (incoming_state == target_state):
            raise Exception("Target state cannot be start state")

        self.graph = graph
        self.result = {}

    def a_star(self):
        """ does a*Star algorithm to find shortest path between start and finish state"""

        found_paths = {}

        found = False

        stack = {self.distance_heur(self.incoming_state, self.target_state)+0 : [(self.incoming_state, 0)]}

        cyclefree = set()

        while(not found):

            # get next element
            stack_keys_minimum = min(stack.keys())
            current_element = stack[stack_keys_minimum].pop()
            if (len(stack[stack_keys_minimum]) == 0):
                del stack[stack_keys_minimum]

            # if solution, return
            if (current_element == self.target_state):
                return self.retrace(found_paths)

            cyclefree.add(current_element[0])

            # follow arrows
            for possible_next in self.graph[current_element[0]]:

                if (possible_next in cyclefree):
                    continue

                found_paths[possible_next] = current_element[0]

                step_cost = current_element[1] + 1

                heuristic_cost = self.distance_heur(possible_next, self.target_state)

                # if solution, return
                if (possible_next == self.target_state):
                    return self.retrace(found_paths)

                total_cost = step_cost + heuristic_cost

                if (total_cost not in stack):
                    stack[total_cost] = []

                stack[total_cost].append( (possible_next, step_cost))

        return False



    def distance_heur(self, a, b):
        """ calculates some manhattan distance metric"""

        cost = 0
        for el_a, el_b in zip(a, b):
            cost += abs(el_a[0] -el_b[0]) + abs(el_a[1] -el_b[1])
        return cost

    def retrace(self, found_paths):
        """
        extracts the path from start to end

        :param found_paths:
        :return:
        """


        transfer_dict = {}
        reached = False

        current = self.target_state

        while (not reached):

            temp = found_paths[current]

            transfer_dict[current] = temp

            current = temp

            if (current == self.incoming_state):
                reached = True


        return transfer_dict


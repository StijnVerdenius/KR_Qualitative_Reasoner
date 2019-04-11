from model.classes import *

class Trace:

    def __init__(self, incoming_state : State, target_state: State, graph):

        self.incoming_state = incoming_state
        self.target_state = target_state
        self.graph = graph
        self.result = {}

    def solve(self):
        pass

    def visualize(self):
        pass


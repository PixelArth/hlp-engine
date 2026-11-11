"""
Board solver 1.0. Can Solve any board that is known to be solvable.

Solving strategy :

1. Compute each possible movement in the current state and add it to the list of all movement in queue.
2. Choose a random movement to execute that has not been done yet.
3. Link the state before the movement and after the movement with the network graph dictionnary
4. If the goal is reached, stop. Else if the state reached is a new state, go back to step 1. Else go back to step 2.

"""




import random
import copy
import hashlib
import json
import time
from collections import defaultdict

import networkx as nx

from board import Board
from controller import Controller
from board_elements import MovableBoardElement

class BoardSolver:


    def __init__(self, controller : Controller, objective_map : dict[ int,list[list[int]] ]):
        self.objective_block_ids = MovableBoardElement.get_objective_block_ids()

        for k,v in objective_map.items():
            objective_map[k] = sorted(v)
        
        self.objective_map = objective_map # block_id -> Positions
        self.controller = controller
        self.board_states = {} # state_id -> board state (MovableBoardElement -> coordinates of the block)
        self.state_graph = defaultdict(list) # Adjacency matrix (state_id -> list of other state_ids that are only 1 move away)


    # ============================= #
    # Solver and explorer functions #
    # ============================= #

    def explore(self):
        """
        Explore every single state of the board.

        Returns True the objective is reached else False.
        """
        print("Discovering all possible states, might take a while...")

        board = self.controller.board

        self.controller.update_state() # Make sure the board is updated

        block_list: list[MovableBoardElement] = list(MovableBoardElement.registry.values())

        move_queues = {} # move_queue for each board_state
        start_state_id = self.state_to_id(board.board_state)
        move_queues[start_state_id] = (self.fill_move_queue(board=board, block_list=block_list))
        
        if move_queues[start_state_id] == []:
            print("No block can move in the board. The board cannot be solved, please check the board.")
            return

        self.board_states[start_state_id] = board.board_state
        solved_state_ids = []

        while move_queues != {} or current_state_id not in self.board_states:
            # Compute all moves if it's a new state
            current_state_id = self.state_to_id(board.board_state)
            if current_state_id not in self.board_states:
                move_queues[current_state_id] = (self.fill_move_queue(board=board, block_list=block_list))
                self.board_states[current_state_id] = board.board_state

            # Choose a random move to execute (state and move)
            chosen_state_id = random.choice(list(move_queues.keys()))
            chosen_move = random.choice(move_queues[chosen_state_id])

            # Remove move choice from list and state from list if all moves have been chosen
            move_queues[chosen_state_id].remove(chosen_move)
            if move_queues[chosen_state_id] == []:
                move_queues.pop(chosen_state_id)

            # Set the board in the desired state
            # (1. update coords of the block,
            #  2.Update the grid --> Inside the coord update,
            #  3.update the board_state attribute
            # )
            # and execute move
            chosen_board_state = copy.deepcopy(self.board_states[chosen_state_id]) # Get state
            self.controller.update_coords(new_board_state=chosen_board_state) # 1. and 2.
            board.board_state = chosen_board_state # 3.

            block_id, direction, leading_components, trailing_components = chosen_move
            block = MovableBoardElement.registry[block_id]

            self.controller.move_block(block = block, direction=direction,
                                       leading_components=leading_components, trailing_components=trailing_components) # board is updated inside the function
            solved = self.is_objective_reached()

            new_state_id = self.state_to_id(board.board_state)
            if new_state_id not in self.state_graph[chosen_state_id]:
                self.state_graph[chosen_state_id].append(new_state_id)
            if chosen_state_id not in self.state_graph[new_state_id]:
                self.state_graph[new_state_id].append(chosen_state_id)

            if solved:
                solved_state_ids.append(new_state_id)

        self.board_states[new_state_id] = board.board_state

        if solved_state_ids != [] :
            print("Exploration finished.")

            optimal_path, optimal_length = \
                self.find_optimal_solution(start_state_id=start_state_id, solved_state_ids=solved_state_ids)
            self.build_solution_boards(shortest_path=optimal_path)

            print(f"Explored all possible states. \nThere are {len(self.board_states)} states.")
            print(f"There are {len(solved_state_ids)} solved states.")
            print(f"Optimal path length is {optimal_length}")
            return optimal_path

        print(f"Explored all possible states !\nThere are {len(self.board_states)} states !")
        print("There are no existing state where the objective is reached. The board is unsolvable.")
        return False

    def solve(self):
        """
        Solve the given board by exploring randomly new states and the possible
        movements of the blocks in the board.
        
        This is the recommended operation when trying to know if the board is solvable,
        it's much faster than the explore function (which explores EVERY possible state)
        
        Returns True if the board is solvable, False otherwise.
        """
        self.controller.update_state() # Make sure the board is updated
        self.start_state_id = self.state_to_id(self.controller.board.board_state)

        print(f"First state : {self.start_state_id}")
        print(f"\nSolving the board... it might take some time !")

        solved = False
        block_list: list[MovableBoardElement] = list(MovableBoardElement.registry.values())
        move_queues = {} # move_queue for each board_state

        while not solved:

            current_state_id = self.state_to_id(self.controller.board.board_state)
            # Compute all moves if it's a brand new state of the board
            if current_state_id not in self.board_states:
                move_queues[current_state_id] = (self.fill_move_queue(board=self.controller.board, block_list=block_list))
                self.board_states[current_state_id] = self.controller.board.board_state

            if move_queues == {}:
                return False

            # Choose a random move to execute (state and move)
            chosen_state_id = random.choice(list(move_queues.keys()))
            chosen_move = random.choice(move_queues[chosen_state_id])

            # Remove move choice from list and state from list if all moves have been chosen
            move_queues[chosen_state_id].remove(chosen_move)
            if move_queues[chosen_state_id] == []:
                move_queues.pop(chosen_state_id)

            # Set the board in the desired state
            # (1. update coords of the block,
            #  2.Update the grid --> Inside the coord update,
            #  3.update the board_state attribute )
            chosen_board_state = copy.deepcopy(self.board_states[chosen_state_id]) # Get state
            self.controller.update_coords(new_board_state=chosen_board_state) # 1. , 2. and 3.

            block_id, direction, leading_components, trailing_components = chosen_move
            block = MovableBoardElement.registry[block_id]

            # Move
            self.controller.move_block(block = block, direction=direction,
                                       leading_components=leading_components, trailing_components=trailing_components) # board is updated inside the function

            solved = self.is_objective_reached()

            new_state_id = self.state_to_id(self.controller.board.board_state)
            if new_state_id not in self.state_graph[chosen_state_id]:
                self.state_graph[chosen_state_id].append(new_state_id)
            if chosen_state_id not in self.state_graph[new_state_id]:
                self.state_graph[new_state_id].append(chosen_state_id)

        self.board_states[new_state_id] = self.controller.board.board_state
        self.end_state_id = new_state_id
        print("Board Solved !")
        print(f"Solved state is {self.end_state_id}")

        self.print_solution(start_state_id=self.start_state_id, end_state_id=self.end_state_id)
        return True

    def print_solution(self, start_state_id, end_state_id):
        graph = nx.from_dict_of_lists(self.state_graph)
        shortest_path = nx.shortest_path(graph, source=start_state_id, target=end_state_id)

        print(f"Solution path length : {len(shortest_path)}")

        solution_boards = self.build_solution_boards(shortest_path)
        for board in solution_boards:
            b = Board(size=len(board))
            b.grid = board
            print(b)

        print("Done.")

    def build_solution_boards(self, shortest_path):
        """
            Build the list containing all steps to complete the puzzle from the given shortest_path

            returns the list of each board
        """
        self.solution_boards = []
        for board_state in shortest_path:
            self.controller.update_coords(new_board_state=board_state)
            self.solution_boards.append(self.controller.board.grid)

        return self.solution_boards

    def find_optimal_solution(self, start_state_id, solved_state_ids : list) \
        -> tuple[list[ dict[int, list[list[int]]] ], int]:
        """
        Finds the optimal solution to go from start_state_id to the closest id from the solved_state_ids list
        
        Returns :
        - optimal_path : list of the board state from the start to the finish
        - length : length of the path
        """
        graph = nx.from_dict_of_lists(self.state_graph)
        
        print("Searching optimal solution")
        t0 = time.time()
        length, path = nx.multi_source_dijkstra(G=graph, sources = solved_state_ids, target = start_state_id )
        print(f"Computed all solutions in {(time.time() - t0):.0f}s")
        
        optimal_path = [self.board_states[state_id] for state_id in path]
        optimal_path = list(reversed(optimal_path))
        

        return (optimal_path, length)



    # ===================================== #
    # Solver and explorer helping functions #
    # ===================================== #

    def fill_move_queue(self, board : Board, block_list : list[MovableBoardElement]):
        """
        Fill a list with the necessary information to start a move

        returns : list of tuple, one tuple corresponds to an ALLOWED movement on the board for a specific block in a specific direction

        --> id, direction, leading_components, trailing_components
        """
        queue = []
        for block in block_list:
            up,down,left,right, up_components,down_components,left_components,right_components = block.check_legal_moves(board)
            if up:
                queue.append((block.id, "UP", up_components, down_components))
            if down:
                queue.append((block.id, "DOWN", down_components, up_components))
            if left:
                queue.append((block.id, "LEFT", left_components, right_components))
            if right:
                queue.append((block.id, "RIGHT", right_components, left_components))

        return queue

    def state_to_id(self, board_state : dict) :
        """
        Converts a state of the board into a supposedly unique identifier,
        the order of the keys must not matter, only values (coords of blocks).

        hash function is sha1 because consistency between different runtime is preferred and it's fast.
        """
        board_state = {block_id : sorted(coords) for block_id,coords in board_state.items()} # Sort values of the state to have a consistent representation

        hashed = hashlib.sha1(repr(json.dumps(board_state, sort_keys=True)).encode())
        val = hashed.digest()
        return val

    def is_objective_reached(self):
            """
                returns True if the coordinates of the objective block and the position of the objective are equals.
            """
            objective_block_list = [MovableBoardElement.registry[block_id] for block_id in self.objective_block_ids]
            return all([sorted(block.coords) == self.objective_map[str(block.id)] for block in objective_block_list])

    def state_exists(self, board_state):
        state_id = self.state_to_id(board_state)
        return state_id in self.board_states.keys()

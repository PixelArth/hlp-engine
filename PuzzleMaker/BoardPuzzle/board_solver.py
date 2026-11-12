"""
Board solver v1.3

Solving strategy : BFS

Can solve any board with one or multiple objectives to achieve
- solve function : returns True as soon as a solution if found
- explore function : executes every single moves possible to create the full graph of the board (substentially longer)
"""

import hashlib
import json
from collections import defaultdict

import networkx as nx

from board import Board
from controller import Controller
from board_elements import MovableBoardElement

OPPOSITE_DIRECTION = {"UP":"DOWN", "DOWN":"UP", "RIGHT" : "LEFT", "LEFT":"RIGHT"}

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
        print("Discovering all possible states \n(can be long, if you want to see if a solution exists, use solve instead)")

        new_state_id = None
        solved = False
        registry = MovableBoardElement.registry
        block_list: list[MovableBoardElement] = list(registry.values())
        block_ids = list(registry.keys())
        move_queues = {} 
        board = self.controller.board
        
        self.controller.update_state()
        start_state_id = self.state_to_id_fast(self.controller.board.board_state, block_ids)
        
        print(f"First state : {start_state_id}")
        print(f"\nSolving the board... it might take some time !")
        
        move_queues[start_state_id] = (self.fill_move_queue(self.controller.board, block_list))
        self.board_states[start_state_id] = board.board_state
        if move_queues[start_state_id] == []:
            print("No block can move in the board. The board cannot be solved, please check the board.")
            return False

        new_state_id = None
        solved_state_ids = set()

        while move_queues != {} :
            # Take next move
            chosen_state_id = next(iter(move_queues.keys()))
            queue = move_queues[chosen_state_id]
            chosen_move = queue.pop(0)
            if not queue:
                del move_queues[chosen_state_id]
                
            # Set into the right state
            chosen_board_state = {block_id: list(coords) for block_id, coords in self.board_states[chosen_state_id].items()}
            self.controller.update_coords(chosen_board_state)
        
            # Execute move and check for objective
            block_id, direction, leading_components, trailing_components = chosen_move
            block = registry[block_id]
            self.controller.move_block(block, direction,
                                       leading_components, trailing_components)
            solved = self.is_objective_reached()
            
            new_state_id = self.state_to_id_fast(board.board_state, block_ids)
            
            # Update graph
            if new_state_id not in self.state_graph[chosen_state_id]:
                self.state_graph[chosen_state_id].append(new_state_id)
            if chosen_state_id not in self.state_graph[new_state_id]:
                self.state_graph[new_state_id].append(chosen_state_id)


            if new_state_id not in self.board_states:
                self.board_states[new_state_id] = board.board_state
                board.update_grid()  # Only update the grid layout when new moves need to be computed
                new_moves = self.fill_move_queue(board, block_list)
                new_moves = [move for move in new_moves if not(move[0] == block_id and move[1] == OPPOSITE_DIRECTION[direction])]
                if new_moves: move_queues[new_state_id] = new_moves
            elif new_state_id in move_queues:
                new_moves = [move for move in move_queues[new_state_id] if not(move[0] == block_id and move[1] == OPPOSITE_DIRECTION[direction])]
                if new_moves: move_queues[new_state_id] = new_moves
                else: del move_queues[new_state_id]

            if solved :
                solved_state_ids.add(new_state_id)
                
        self.board_states[new_state_id] = board.board_state

        if solved_state_ids :
            print("Exploration finished.")

            optimal_path, optimal_length = \
                self.find_optimal_solution(start_state_id=start_state_id, solved_state_ids=solved_state_ids)
            self.build_solution_boards(shortest_path=optimal_path)

            self.print_puzzle_metrics(solved=True, path_length=optimal_length)
            print(f"There are {len(solved_state_ids)} solved states.")
            return optimal_path

        self.print_puzzle_metrics()
        return False

    def solve(self):
        """
        Solves the board puzzle using a BFS algorithm.
        Stops as soon as a solution is found.
        
        In case the board is unsolvable, this is equivalent at optimized_explore() as it
        will explore every state
        
        Returns True if a solution exists, False otherwise.
        """
        new_state_id = None
        solved = False
        registry = MovableBoardElement.registry
        block_list: list[MovableBoardElement] = list(registry.values())
        block_ids = list(registry.keys())
        move_queues = {} 
        board = self.controller.board
        
        self.controller.update_state() # Make sure the board is updated
        start_state_id = self.state_to_id_fast(board.board_state, block_ids)
        
        print(f"First state : {start_state_id}")
        print(f"\nSolving the board... it might take some time !")
        
        move_queues[start_state_id] = (self.fill_move_queue(board, block_list))
        self.board_states[start_state_id] = board.board_state
        if move_queues[start_state_id] == []:
            print("No block can move in the board. The board cannot be solved, please check the board.")
            return False
        
        while not solved:
            # Take next move
            chosen_state_id = next(iter(move_queues.keys()))
            queue = move_queues[chosen_state_id]
            chosen_move = queue.pop(0)
            if not queue:
                del move_queues[chosen_state_id]
                
            # Set into the right state
            chosen_board_state = {block_id: list(coords) for block_id, coords in self.board_states[chosen_state_id].items()}
            self.controller.update_coords(chosen_board_state)

            # Execute move and check for objective
            block_id, direction, leading_components, trailing_components = chosen_move
            block = registry[block_id]
            self.controller.move_block(block, direction,
                                       leading_components, trailing_components)
            solved = self.is_objective_reached()
            
            new_state_id = self.state_to_id_fast(board.board_state, block_ids)
            
            # Update graph
            if new_state_id not in self.state_graph[chosen_state_id]:
                self.state_graph[chosen_state_id].append(new_state_id)
            if chosen_state_id not in self.state_graph[new_state_id]:
                self.state_graph[new_state_id].append(chosen_state_id)
            
            # Add new moves strategically without adding the symetric move performed on this step
            if new_state_id not in self.board_states:
                self.board_states[new_state_id] = board.board_state
                board.update_grid()  # Only update the grid layout when new moves need to be computed
                new_moves = self.fill_move_queue(board, block_list)
                new_moves = [move for move in new_moves if not(move[0] == block_id and move[1] == OPPOSITE_DIRECTION[direction])]
                if new_moves: move_queues[new_state_id] = new_moves
            elif new_state_id in move_queues:
                new_moves = [move for move in move_queues[new_state_id] if not(move[0] == block_id and move[1] == OPPOSITE_DIRECTION[direction])]
                if new_moves: move_queues[new_state_id] = new_moves
                else: del move_queues[new_state_id]

            if move_queues == {}:
                self.print_puzzle_metrics(solved)
                return False
            
    
        self.board_states[new_state_id] = board.board_state
    
        path_length = self.print_solution(start_state_id=start_state_id, end_state_id=new_state_id)
        self.print_puzzle_metrics(solved, path_length)
        return True
        

    def print_solution(self, start_state_id, end_state_id) -> int:
        """
        Prints solution in terminal
        
        Returns path length
        """
        
        graph = nx.from_dict_of_lists(self.state_graph)
        path = nx.shortest_path(graph, source=start_state_id, target=end_state_id)

        path = [self.board_states[state_id] for state_id in path]

        solution_boards = self.build_solution_boards(path)
        for board in solution_boards:
            b = Board(size=len(board))
            b.grid = board
            print(b)

        return len(path)

    def print_puzzle_metrics(self, solved : bool | None = False, path_length : int | None = -1):
            n_edges = sum([len(v) for v in self.state_graph.values()])
            
            if solved: 
                print("Board is solved")
                print(f"Path length : {path_length} states ({path_length - 1} moves)")
            else: print("Board in unsolvable")
            
            print(f"There are {len(self.board_states)} states.")
            print(f"There are {len(self.state_graph)} nodes.")
            print(f"There are {n_edges} edges.")

    def find_optimal_solution(self, start_state_id, solved_state_ids : list) \
        -> tuple[list[ dict[int, list[list[int]]] ], int]:
        """
        Finds the optimal solution to go from start_state_id to the closest id from the solved_state_ids list
        
        Returns :
        - optimal_path : list of the board state from the start to the finish
        - length : length of the path
        """
        graph = nx.from_dict_of_lists(self.state_graph)
        
        print("Searching optimal solution...")
        length, path = nx.multi_source_dijkstra(G=graph, sources = solved_state_ids, target = start_state_id )
        
        optimal_path = [self.board_states[state_id] for state_id in path]
        optimal_path = list(reversed(optimal_path))
        
        return (optimal_path, length)

    def build_solution_boards(self, shortest_path):
            """
                Build the list containing all steps to complete the puzzle from the given shortest_path

                returns the list of each board
            """
            self.solution_boards = []
            
            for board_state in shortest_path:
                self.controller.update_coords(new_board_state=board_state, update_grid=True)
                self.solution_boards.append(self.controller.board.grid)

            return self.solution_boards

    

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

    def state_to_id_fast(self, board_state : dict, block_ids) -> tuple[tuple]:
        """
        New IDs for each state :
            
            - Each element coordinates is transformed into a unique number 
            computed with : row << 8 | col
            - Creates a tuple using these numbers, each tuple 
            - Each tuple is the representation of a block in the grid
            - The tuple of all tuple of all blocks gives a unique ID for board_state
        """
        
        return tuple([tuple(sorted([row << 8 | col for row, col in board_state[block_id]])) for block_id in block_ids])

    def is_objective_reached(self):
            """
                returns True if the coordinates of the objective block and the position of the objective are equals.
            """
            objective_block_list = [MovableBoardElement.registry[block_id] for block_id in self.objective_block_ids]
            return all([sorted(block.coords) == self.objective_map[str(block.id)] for block in objective_block_list])

    def state_exists(self, board_state):
        state_id = self.state_to_id(board_state)
        return state_id in self.board_states.keys()

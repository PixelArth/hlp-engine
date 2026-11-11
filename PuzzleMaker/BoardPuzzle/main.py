# Solve this :
# | ‾ ‾ ‾ ‾ ‾ ‾ ‾ ‾ |
# | X X X X X X X X |
# | X X X X X X X X |
# | X 4 4 2 2 6 6 X |
# | X 4 5 2 2 7 6 X |
# | X 5 5 3 3 7 7 X |
# | 0 0 0 3 3 0 0 0 |
# | X 1 1 X X 0 0 X |
# | X 1 1 X X 0 0 X |
# | _ _ _ _ _ _ _ _ |
#
#
# Objective : Bring block 1 to the bottom right of the shape
# Code objective : board[7][6] = 1, board[7][7] = 1 , board[8][6] = 1 , board[8][7] = 1
#
# "X", "|" , "_" , "‾" are blocked space
# 0 is free space
# positive integers are blocks that can only move up right down left


from board import Board
from board_elements import MovableBoardElement
from controller import Controller
from board_solver import BoardSolver
from board_viewer import show_solution_path
from utils import *

import time

board = Board(size = 8)


board.block_rows([1,2])
board.block_columns([1,8])

# Empty
board.place_element(coords = [[6,1],[6,8]], element_type="Empty")
# Immovable
board.place_element(coords = [[7,4],[7,5],[8,4],[8,5]], element_type="Immovable")
# Movable
board.place_element(coords = [[7,2], [7,3],
                           [8,2], [8,3] ],
                      element_type="Movable",
                      is_objective=True)
board.place_element(coords = [[3,4],[3,5],[4,4],[4,5]], element_type="Movable")
board.place_element(coords = [[5,4],[5,5],[6,4],[6,5]], element_type="Movable")

board.place_element(coords = [[3,2],[3,3],[4,2]], element_type="Movable")
board.place_element(coords = [[4,3],[5,2],[5,3]], element_type="Movable")

board.place_element(coords = [[3,6],[3,7],[4,7]], element_type="Movable")
board.place_element(coords = [[5,6],[5,7],[4,6]], element_type="Movable")

# Objective
objective_coords = [[7,6],[7,7],[8,6],[8,7]]

# Controller and Solver objects
controller = Controller(board=board)
controller.update_state()
solver = BoardSolver(controller = controller, objective_map={"1" : objective_coords})

# Solve
print(board)

start_time = time.time()
solver.solve()
elapsed = time.time()-start_time
print(f"Solved in {elapsed}")


# Display the solution path in a window
show_solution_path(solver.solution_boards, objective_coords)

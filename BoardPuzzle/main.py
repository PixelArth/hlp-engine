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
from blocks import MovableBlock
from controller import Controller
from board_solver import BoardSolver
from board_viewer import showSolutionPath
from utils import *

import time as t

board = Board(size = 8)


board.blockRows([1,2])
board.blockColumns([1,8])

# Air
board.placeBlock(coords = [[6,1],[6,8]], block_type="Air")
# Immovable
board.placeBlock(coords = [[7,4],[7,5],[8,4],[8,5]], block_type="Immovable")
# Movable
board.placeBlock(coords = [[7,2], [7,3],
                                [8,2], [8,3] ],
                      block_type="Movable",
                      isObjective=True)
board.placeBlock(coords = [[3,4],[3,5],[4,4],[4,5]], block_type="Movable")
board.placeBlock(coords = [[5,4],[5,5],[6,4],[6,5]], block_type="Movable")

board.placeBlock(coords = [[3,2],[3,3],[4,2]], block_type="Movable")
board.placeBlock(coords = [[4,3],[5,2],[5,3]], block_type="Movable")

board.placeBlock(coords = [[3,6],[3,7],[4,7]], block_type="Movable")
board.placeBlock(coords = [[5,6],[5,7],[4,6]], block_type="Movable")

# Objective
objective = [[7,6],[7,7],[8,6],[8,7]]

# Controller and Solver objects
controller = Controller(objectivePosition = objective)
controller.updateState(board=board)
solver = BoardSolver(controller = controller)

# Solve
print(board)

t0 = t.time()

solver.solve(board=board)

tf = t.time()-t0
print(f"Solved in {tf}")

# Display the solution path in a window
showSolutionPath(solver.solutionLayouts, objective)
from pathlib import Path
from controller import Controller
from board_solver import BoardSolver
from board_viewer import show_solution_path

path = "boards/ferris_wheel.json"
path = "boards/ufo.json"

controller, objective_map  = Controller.make_controller_from_json(path = Path(path))
controller.update_state()
solver = BoardSolver(controller=controller, objective_map=objective_map)


objective_coords = set()
for v in list(objective_map.values()):
    for row,col in v:
        objective_coords.add((row,col))

solved = solver.solve()
if solved: 
    show_solution_path(boards = solver.solution_boards, objective_coords=objective_coords)
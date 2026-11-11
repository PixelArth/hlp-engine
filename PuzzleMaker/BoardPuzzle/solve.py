from pathlib import Path
from controller import Controller
from board_solver import BoardSolver

path = "boards/ufo.json"

controller, objective_map  = Controller.make_controller_from_json(path = Path(path))
controller.update_state()
solver = BoardSolver(controller=controller, objective_map=objective_map)
solver.solve()

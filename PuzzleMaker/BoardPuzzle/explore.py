from pathlib import Path
import time


from controller import Controller
from board_solver import BoardSolver
from board_viewer import show_solution_path

path = "boards/ufo.json"

controller, objective_map  = Controller.make_controller_from_json(path = Path(path))
controller.update_state()
solver = BoardSolver(controller=controller, objective_map=objective_map)

objective_coords = set()
for v in list(objective_map.values()):
    for row,col in v:
        objective_coords.add((row,col))

start_time = time.time()
optimal_path = solver.explore()
elapsed = time.time() - start_time
print(f"Explored everything in {elapsed}s")


if optimal_path:
    show_solution_path(solver.solution_boards, objective_coords)
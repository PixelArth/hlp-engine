from typing import Literal
import json
from pathlib import Path

from board_elements import MovableBoardElement
from board import Board

class Controller:
    """
    Controller class holding the objective block and positions.

    These are not linked to the board class itself so a board can hold multiple controllers with multiple objectives.
    """
    def __init__(self, board : Board ):
        self.board = board


    @staticmethod
    def make_controller_from_json(path : Path) :
        """
        Creates a new controller based on the JSON of the path argument.

        returns :
        - a new controller for the desired board
        - the map of block_id -> Position objectives
        """

        with open(path, mode="r", encoding="utf-8") as f:
            data = json.load(f)

        new_board = Board(size=data["size"])

        new_board.place_element(data["air"]["coords"], element_type="Empty")
        new_board.place_element(data["immovable"]["coords"], element_type="Immovable")
        for _, val in data["movable"].items():
            new_board.place_element(val["coords"], element_type="Movable", is_objective=val["is_objective"])

        new_controller = Controller(board = new_board)
        return new_controller, data["objective"]


    def update_state(self, update_grid=False) -> None:
        """
            Updates the current board state (mapping movable blocks to their coordinates) based on the coordinates of each block.

            Then updates the current board grid (the view)
        """
        registry = MovableBoardElement.registry
        for (block_id,block) in registry.items():
            self.board.board_state[block_id] = block.coords
            
        if update_grid : self.board.update_grid()

    def update_coords(self, new_board_state, update_grid=False) -> None :
        """
        Updates the coordinates when switching between boards states
        """
        MovableBoardElement.update_coords(new_board_state)
        self.board.board_state = new_board_state # VERY IMPORTANT TO UPDATE THE BOARD STATE, OTHERWISE THE GRID WILL BE WRONG
        if update_grid: self.board.update_grid()


    def move_block(self, block : MovableBoardElement,
                  direction : Literal["UP","DOWN","RIGHT","LEFT"],
                  leading_components : dict, trailing_components : dict):
        """
            1. Change the coordinates of the moved block depending on the movement
            2. Update the board_state with the new coordinates of the block
            3. Update the view (grid attribute), totally controlled by the board_state

            if any block_state has been made while using directly the block.coords attribute
            of the block passed in argument, the block_state will automatically be updated.

            Returns True when the Objective block reach its objective position
        """
        coordinates = block.coords

        # Remove old coordinates
        if direction == "UP" or direction == "DOWN":
            for col,row in trailing_components.items():
                coordinates.remove([row,col])
        else:
            for row,col in trailing_components.items():
                coordinates.remove([row,col])


        # Add new coordinates
        if direction == "UP":
            for col,row in leading_components.items():
                coordinates.append([row-1,col])
        elif direction == "DOWN":
            for col,row in leading_components.items():
                coordinates.append([row+1,col])
        elif direction == "LEFT":
            for row,col in leading_components.items():
                coordinates.append([row,col-1])
        else:
            for row,col in leading_components.items():
                coordinates.append([row,col+1])

from __future__ import annotations
from typing import TYPE_CHECKING, Literal

from utils import find_up_components, find_down_components, find_left_components, find_right_components
from board_puzzle_exception import BoardPuzzleException
if TYPE_CHECKING:
    from board import Board


class BoardElement:
    def __init__(self, char : str,):
        self.char = char

    def __str__(self):
        return self.char

class EmptyBoardElement(BoardElement):
    """
    Empty space in the grid, a physical block can move to this place
    """

    def __init__(self, char : str | None = "0"):
        super().__init__(char=char)

class ImmovableBoardElement(BoardElement):
    """
    Solid and Immovable blocks (borders and other obstacles)
    """
    def __init__(self, char : str):
        super().__init__(char=char)

class MovableBoardElement(BoardElement):
    """
    Block that can move in EmptyBoardElements. We keep track of their coordinates and every type of this block on the board with a registry
    """
    registry : dict[int,MovableBoardElement] = {}
    next_id = 0

    def __init__(self, coords: list[list[int,int]],  is_objective : bool):
        # Registry
        MovableBoardElement.next_id += 1
        self.id = MovableBoardElement.next_id
        MovableBoardElement.registry[self.id] = self

        # Attributes
        self.char = str(self.id)
        self.is_objective = is_objective # Objective -> block to move somewhere
        self.coords = coords

    # Class functions
    @staticmethod
    def update_coords(board_state : dict) -> None:
        """
        Update coords of the blocks based on a given board_state
        """
        for block_id, coords in board_state.items():
            MovableBoardElement.registry[block_id].coords = coords

    @staticmethod
    def get_objective_block_ids() -> list[int]:
        objective_block_ids = []
        for block in list(MovableBoardElement.registry.values()):
            if block.is_objective: objective_block_ids.append(block.id)

        if objective_block_ids == []:
            raise BoardPuzzleException("No objective block found")

        return objective_block_ids


    # Instance function
    def check_legal_moves(self, board : Board) -> tuple[bool,bool,bool,bool,dict[int,int],dict[int,int],dict[int,int],dict[int,int]]:
        """
        Checks for all the legal moves for the block on the given board
        Returns
            1 boolean for each direction (up,down,left,right) indicating if the movement is legal or not
            1 dict giving the coordinates of the components of the block in every direction, used to make the actual move.
        """

        up, up_components = self.check_up_move(board = board)
        down, down_components = self.check_down_move(board = board)
        left, left_components = self.check_left_move(board = board)
        right, right_components = self.check_right_move(board = board)

        return up, down, left, right, up_components, down_components, left_components, right_components

    def check_up_move(self, board : Board) -> tuple[bool,dict[int,int]]:
        """
        returns : tuple[Bool,dict]
            True if a upward movement is possible, False otherwise.

        """
        up_components = find_up_components(self)

        for row,col in self.coords:  # Check if block is on top and find all topmost blocks in each column
            if row == 1:
                return False, up_components

        for col,row in up_components.items(): # Check EmptyBoardElement above each up component of the block
            if not isinstance(board.grid[row-1][col], EmptyBoardElement):
                return False, up_components
        return True, up_components

    def check_down_move(self, board : Board) -> tuple:
        """
        Returns True if a downward movement is possible, False otherwise.
        """
        full_size = board.full_size
        down_components = find_down_components(self)

        for row,col in self.coords:
            if row == full_size-2:
                return False, down_components



        for col,row in down_components.items():
            if not isinstance(board.grid[row+1][col], EmptyBoardElement):
                return False, down_components
        return True, down_components

    def check_left_move(self, board : Board) -> tuple:
        """
        Returns True if a left movement is possible, False otherwise.
        """
        left_components = find_left_components(self)

        for row,col in self.coords:
            if col == 1:
                return False, left_components



        for row,col in left_components.items():
            if not isinstance(board.grid[row][col-1], EmptyBoardElement):
                return False, left_components
        return True, left_components

    def check_right_move(self, board : Board) -> tuple:
        """
        Returns True if a right movement is possible, False otherwise.
        """
        full_size = board.full_size
        right_components = find_right_components(self)

        for row,col in self.coords:
            if col == full_size-2:
                return False, right_components



        for row,col in right_components.items():
            if not isinstance(board.grid[row][col+1], EmptyBoardElement):
                return False, right_components
        return True, right_components

ELEMENT_TYPES = {
    "Empty" : EmptyBoardElement,
    "Immovable" : ImmovableBoardElement,
    "Movable" : MovableBoardElement,
}

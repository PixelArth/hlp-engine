
from board_elements import BoardElement, ImmovableBoardElement, EmptyBoardElement, MovableBoardElement
from typing import Literal

from board_puzzle_exception import BoardPuzzleException

class Board:
    """
    Squared-shape board made of BoardElement object.
    """
    def __init__(self, size: int):
        if size < 1:
            raise ValueError("board size is too small")

        # Board setup
        self.full_size = size
        self.grid = self.blank_grid()
        self.board_state = {} # State of the board mapping the movable blocks of the board and their coordinates

    def __str__(self):
        return "\n".join(" ".join("".join([element.char for element in row])) for row in self.grid) + "\n"


    # =========== #
    # Grid update #
    # =========== #
    def update_grid(self):
        """
        updates the grid based on the board state (only updates the movable blocks)
        """
        new_grid = self.copy_without_movable() # Same grid as old one but all MovableBoardElements are EmptyBoardElement instead

        for block_id, coord_list in self.board_state.items():
            for coords in coord_list:
                row, col = coords[0], coords[1]
                new_grid[row][col] = MovableBoardElement.registry[block_id]
        self.grid = new_grid




    # ================================= #
    # Helping functions to create board #
    # ================================= #
    def block_rows(self, rows: list[int]):
        """
        rows : list of row indexes to fill with Immovable elements

        rows = [0] blocks self.grid[0][0:self.full_size]
        """
        self.check_row_or_column_out_of_range(rows)
        for row in rows:
            for col in range(0,self.full_size):
                self.grid[row][col] = ImmovableBoardElement(char="X")

    def block_columns(self, columns: list[int]):
        """
        columns : list of column indexes to fill with Immovable elements

        columns = [0] blocks self.grid[0:self.full_size][0]
        """
        self.check_row_or_column_out_of_range(columns)
        for col in columns:
            for row in range(0,self.full_size):
                self.grid[row][col] = ImmovableBoardElement(char="X")

    def place_element(self, coords : list[list[int,int]],
                   element_type : Literal["Movable", "Immovable", "Empty"],
                   is_objective : bool | None = False):
        """
        coords : list of (row,col) values, all coords must corresponds to EmptyBoardElements (no overlapping MovableBoardElements)
        """
        if      element_type == "Movable"  :
            self.check_block_overlap_error(coords)
            new_element = MovableBoardElement(coords=coords, is_objective = is_objective)
        elif    element_type == "Immovable": new_element = ImmovableBoardElement(char='X')
        elif    element_type == "Empty"    : new_element = EmptyBoardElement(char="0")
        else:
            raise Exception("Wrong element type to place")
        
        for row,col in coords:
            self.grid[row][col] = new_element

    def blank_grid(self) -> list[list[BoardElement]]:
        """
        Returns a blank grid of size self.full_size with 1 additionnal row and column of Immovable elements
        """
        grid = [ [EmptyBoardElement() for _ in range(self.full_size)] for _ in range(self.full_size) ]
        return grid

    def copy_without_movable(self):
        """
        returns a deepcopy of the board without the movable blocks
        """
        new_grid = []
        for row in self.grid:
            new_row = []
            for element in row:
                if isinstance(element, MovableBoardElement): new_row.append(EmptyBoardElement())
                else: new_row.append(element)
            new_grid.append(new_row)
        return new_grid







    # ============ #
    # Error checks #
    # ============ #
    def check_row_or_column_out_of_range(self, row_or_column):
        for value in row_or_column:
            if not 0<=value<=self.full_size:
                raise BoardPuzzleException(f"all rows/columns must be between 0 and {self.full_size-1}")

    def check_block_overlap_error(self, coords : list[list[int,int]]):
        for row,col in coords:
            if not isinstance(self.grid[row][col], EmptyBoardElement):
                raise BoardPuzzleException(f"A non-empty element is already placed at coords ({row},{col})")

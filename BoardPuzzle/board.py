from blocks import ImmovableBlock, AirBlock, MovableBlock
from typing import Literal

class Board:
    """
    Squared-shape board with Immovable borders.
    
    Immovable borders allows for better comprehension and better coordinate manipulation,
    up-left corner has coords (1,1) and down-right corner has (size,size).
    """
    def __init__(self, size: int):
        if size < 1:
            raise ValueError("board size is too small")
        
        # Board setup
        self.size = size + 2 # Add 2 to size for the borders
        self.board = self.blankBoard()

        self.boardState = {} # State of the board mapping the movable blocks of the board and their coordinates

    def __str__(self):
        return "\n".join(" ".join("".join([blocks.char for blocks in row])) for row in self.board) + "\n"
    
    # ============= #
    # Layout update #
    # ============= #
    

    def updateBoard(self):
        """
        updates the layout based on the board state (only updates the movable blocks)
        """
        newBoard = self.copyWithoutMovable() # Same board as old one but all MovableBlocks are AirBlock instead
        
        for id, coordList in self.boardState.items():
            for coords in coordList:
                row, col = coords[0], coords[1]
                newBoard[row][col] = MovableBlock.registry[id]
        self.board = newBoard

    # ================================= #
    # Helping functions to create board #
    # ================================= #
    def blockRows(self, rows: list[int]):
        """
        rows [1] blocks self.board[1][1:self.size] (because of borders)
        """
        self.rowOrColumnOutOfRange(rows)
        for row in rows:
            for col in range(1,self.size-1):
                self.board[row][col] = ImmovableBlock(char="X")
    
    def blockColumns(self, columns: list[int]):
        """
        columns [1] blocks self.board[1:self.size][1] (because of borders)
        """
        self.rowOrColumnOutOfRange(columns)
        for col in columns:
            for row in range(1,self.size-1):
                self.board[row][col] = ImmovableBlock(char="X")
    
    def placeBlock(self, coords : list[list[int,int]], 
                   block_type : Literal["Movable", "Immovable", "Air"],
                   isObjective : bool | None = False):
        """
        coords : list of (row,col) values, all coords must corresponds to AirBlocks (no overlapping MovableBlocks)
        """
        
        
        if      block_type == "Movable"  : 
            self.checkBlockOverlapError(coords)
            newBlock = MovableBlock(coords=coords, isObjective = isObjective)
        elif    block_type == "Immovable": newBlock = ImmovableBlock(char='X')
        elif    block_type == "Air"      : newBlock = AirBlock(char="0")
        
        for row,col in coords:
            self.board[row][col] = newBlock
    
    def blankBoard(self):
        board = [ [AirBlock() for col in range(self.size)] for row in range(self.size) ]
        for row in range(self.size):
            for col in range(self.size):
                if row == 0 or row == self.size-1 :
                    board[row][col] = ImmovableBlock(char="‾")
                if row == self.size-1:
                    board[row][col] = ImmovableBlock(char="_")
                if col == 0 or col == self.size-1 :
                    board[row][col] = ImmovableBlock(char="|")
        return board

    def copyWithoutMovable(self):
        newBoard = []
        for row in self.board:
            L = []
            for element in row:
                if isinstance(element, MovableBlock): L.append(AirBlock())
                else: L.append(element)
            newBoard.append(L)
        return newBoard

    # Error checks
    def rowOrColumnOutOfRange(self, rowOrColumn):
        for value in rowOrColumn:
            if not 1<=value<=self.size-2:
                raise ValueError(f"all rows must be between 1 and {self.size-2}")
    
    def checkBlockOverlapError(self, coords : list[list[int,int]]):
        for row,col in coords:
            if not isinstance(self.board[row][col], AirBlock):
                raise TypeError(f"A non-airblock block is already placed at coords ({row},{col})")
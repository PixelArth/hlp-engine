from __future__ import annotations
from typing import TYPE_CHECKING, Literal

from utils import findTopComponents, findDownComponents, findLeftComponents, findRightComponents

if TYPE_CHECKING:
    from board import Board
    

class Block:
    def __init__(self, char : str,):
        self.char = char
        
    def __str__(self):
        return self.char

class AirBlock(Block):
    """
    Empty space in the grid, a physical block can move to this place 
    """
    
    def __init__(self, char : str | None = "0"):
        super().__init__(char=char)

class ImmovableBlock(Block):
    """
    Solid and Immovable blocks (borders and other obstacles)
    """
    def __init__(self, char : str):
        super().__init__(char=char)
    
class MovableBlock(Block):
    """
    Block that can move in AirBlocks. We keep track of their coordinates and every type of this block on the board with a registry
    """
    registry = {}
    nextid = 0
    
    def __init__(self, coords: list[list[int,int]],  isObjective : bool):
        # Registry
        MovableBlock.nextid += 1
        self.id = MovableBlock.nextid
        MovableBlock.registry[self.id] = self
        
        # Attributes
        self.char = str(self.id)        
        self.isObjective = isObjective # Objective -> block to move somewhere
        self.coords = coords
    
    # Class functions
    def updateCoords(boardState : dict) -> None:
        """
        Update coords of the blocks based on a given boardState
        """
        for id, coords in boardState.items():
            MovableBlock.registry[id].coords = coords

    def getObjectiveBlockID() -> MovableBlock:
        for block in list(MovableBlock.registry.values()):
            if block.isObjective:
                return block.id
        raise Exception("No objective block found")
    
    # Instance function
    def checkPossibleMovevement(self, board : Board):
        up, topComp = self.checkUpMove(board = board)
        down, bottomComp = self.checkDownMove(board = board)
        left, leftComp = self.checkLeftMove(board = board)
        right, rightComp = self.checkRightMove(board = board)
        
        return up,down,left,right, topComp, bottomComp, leftComp, rightComp
              
    def checkUpMove(self, board : Board) -> tuple:
        """
        Returns True if a upward movement is possible, False otherwise.
        """

        
        topComponents = findTopComponents(self)# map of the top component in each column of the block (all must have air above them)
        
        for row,col in self.coords:  # Check if block is on top and find all topmost blocks in each column
            if row == 1:
                return False, topComponents
        
        for col,row in topComponents.items(): # Check Air above each top component of the block
            if not isinstance(board.board[row-1][col], AirBlock):
                return False, topComponents
        return True, topComponents
        
    def checkDownMove(self, board : Board) -> tuple:
        """
        Returns True if a downward movement is possible, False otherwise.
        """
        size = board.size
        bottomComponents = findDownComponents(self)
        
        for row,col in self.coords:
            if row == size-2:
                return False, bottomComponents
        
        
        
        for col,row in bottomComponents.items():
            if not isinstance(board.board[row+1][col], AirBlock):
                return False, bottomComponents
        return True, bottomComponents
    
    def checkLeftMove(self, board : Board) -> tuple:
        """
        Returns True if a downward movement is possible, False otherwise.
        """
        leftComponents = findLeftComponents(self)
        
        for row,col in self.coords:
            if col == 1:
                return False, leftComponents
        
        
        
        for row,col in leftComponents.items():
            if not isinstance(board.board[row][col-1], AirBlock):
                return False, leftComponents
        return True, leftComponents
    
    def checkRightMove(self, board : Board) -> tuple:
        size = board.size
        rightComponents = findRightComponents(self)

        for row,col in self.coords:
            if col == size-2:
                return False, rightComponents

        

        for row,col in rightComponents.items():
            if not isinstance(board.board[row][col+1], AirBlock):
                return False, rightComponents
        return True, rightComponents

    


BLOCK_TYPES = {
        "Air" : AirBlock,
        "Immovable" : ImmovableBlock,
        "Movable" : MovableBlock,
}
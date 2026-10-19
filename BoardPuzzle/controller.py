from blocks import MovableBlock
from board import Board

from typing import Literal


class Controller:
    
    def __init__(self, objectivePosition):
        self.objectiveBlockID = MovableBlock.getObjectiveBlockID()
        self.objectivePosition = objectivePosition

    def updateState(self, board : Board):
            """
            updates the current board state (mapping movable blocks to their coordinates) based on coords
            and then updates also the current board layout (the view)
            In-place operation
            """
            registry = MovableBlock.registry
            for (id,block) in registry.items():
                board.boardState[id] = block.coords
            board.updateBoard()
            
    def updateCoords(self, oldBoard : Board, newBoardState) :
        """
        Updates the coords when changing of state without any "move" order (i.e : when solving the board)
        In-place operation
        """
        MovableBlock.updateCoords(newBoardState)
        oldBoard.boardState = newBoardState # VERY IMPORTANT TO UPDATE THE BOARD STATE, OTHERWISE THE LAYOUT WILL BE WRONG
        oldBoard.updateBoard()
    
    def moveBlock(self, block : MovableBlock, 
                  board : Board, 
                  direction : Literal["UP","DOWN","RIGHT","LEFT"], 
                  component : dict, othersideComponent : dict):
        """
        1. Change the coordinates of the moved block depending on the movement
        2. Update the boardState with the new coordinates of the block
        3. Update the view (board attribute), totally controlled by the boardState
        
        Returns True when the Objective block reach its objective position
        """
        
        # Remove old coordinates
        if direction == "UP" or direction == "DOWN":
            for col,row in othersideComponent.items():
                block.coords.remove([row,col])
        else:
            for row,col in othersideComponent.items():
                block.coords.remove([row,col])

        # Add new coordinates
        if direction == "UP":
            for col,row in component.items():
                block.coords.append([row-1,col])
        elif direction == "DOWN":
            for col,row in component.items():
                block.coords.append([row+1,col])
        elif direction == "LEFT":
            for row,col in component.items():
                block.coords.append([row,col-1])
        else:
            for row,col in component.items():
                block.coords.append([row,col+1])
        
        # Update
        self.updateState(board=board)
        
        # Check for end
        objectiveBlock = MovableBlock.registry[self.objectiveBlockID]
        return not self.checkObjective(blockObjective = objectiveBlock, 
                                   objectivePosition=self.objectivePosition)

    def checkObjective(self, blockObjective : MovableBlock, objectivePosition : list[list[int,int]]):
        return sorted(blockObjective.coords) == sorted(objectivePosition)
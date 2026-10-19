"""
Board solver 1.0. Can Solve any board that is known to be solvable.

Solving strategy : 

1. Compute each possible movement in the current state and add it to the list of all movement in queue.
2. Choose a random movement to execute that has not been done yet.
3. Link the state before the movement and after the movement with the network graph dictionnary
4. If the goal is reached, stop. Else if the state reached is a new state, go back to step 1. Else go back to step 2.

TODO : Add a failsafe in case all possible states have been reached without reaching the goal
"""


from board import Board
from controller import Controller
from blocks import MovableBlock

import random as r
import copy
import hashlib
import json
from collections import defaultdict

import networkx as nx

class BoardSolver:
    
    
    def __init__(self, controller : Controller):
        self.controller = controller
        
        self.boardStates = {} # id -> board state (MovableBlock -> coordinates of the block)
        self.stateGraph = defaultdict(list) # mapping of board states id -> id  , a mapping between 2 states means only one movement separates both states 

    def explore(self, board:Board):
        """
        Explore every single state of the board
        """
        self.controller.updateState(board=board) # Make sure the board is updated
    
        blockList: list[MovableBlock] = list(MovableBlock.registry.values())
        moveQueues = {} # moveQueue for each boardState
        currentID = self.stateToID(board.boardState)
        moveQueues[currentID] = (self.fillMoveQueue(board=board, blockList=blockList))
        self.boardStates[currentID] = board.boardState
        
        while moveQueues != {}:
            # Compute all moves if it's a new state
            currentID = self.stateToID(board.boardState)
            if currentID not in self.boardStates:
                moveQueues[currentID] = (self.fillMoveQueue(board=board, blockList=blockList))
                self.boardStates[currentID] = board.boardState
            
            # Choose a random move to execute (state and move)
            stateIDChoice = r.choice(list(moveQueues.keys()))
            moveChoice = r.choice(moveQueues[stateIDChoice])
    
            # Remove move choice from list and state from list if all moves have been chosen
            moveQueues[stateIDChoice].remove(moveChoice)
            if moveQueues[stateIDChoice] == []:
                moveQueues.pop(stateIDChoice)
            
            # Set the board in the desired state 
            # (1. update coords of the block, 
            #  2.Update the layout --> Inside the coord update,
            #  3.update the boardState attribute 
            # ) 
            # and execute move
            boardStateChoice = copy.deepcopy(self.boardStates[stateIDChoice]) # Get state
            self.controller.updateCoords(oldBoard=board, newBoardState=boardStateChoice) # 1. and 2.
            board.boardState = boardStateChoice # 3.
            
            blockID, direction, comp, othersideComp = moveChoice
            block = MovableBlock.registry[blockID]
            _ = self.controller.moveBlock(block = block, board=board, direction=direction, 
                                                  component=comp, othersideComponent=othersideComp) # board is updated inside the function
        
            newID = self.stateToID(board.boardState)
            if newID not in self.stateGraph[stateIDChoice]:
                self.stateGraph[stateIDChoice].append(newID)
            if stateIDChoice not in self.stateGraph[newID]:
                self.stateGraph[newID].append(stateIDChoice)
        
        self.boardStates = board.boardState
        print("Explored all possible states !")
        print(f"There are {len(self.boardStates)} states !")

    
    def solve(self, board : Board):
        """
        Solve the given board by exploring every possible state of the board by testing every movement that creates
        an unseen state.
        """
        self.controller.updateState(board=board) # Make sure the board is updated
        self.startID = self.stateToID(board.boardState)
        
        print(f"First state : {self.startID}")
        print(f"\nSolving the board... (might take a minute or two, because of randomness)")
        
        notSolved = True
        blockList: list[MovableBlock] = list(MovableBlock.registry.values())
        moveQueues = {} # moveQueue for each boardState
        
        while notSolved:
            
            # Compute all moves if it's a new state 
            # CurrentID is only useful now, after, we choose a random known stateID to make the next move
            currentID = self.stateToID(board.boardState)
            if currentID not in self.boardStates:
                moveQueues[currentID] = (self.fillMoveQueue(board=board, blockList=blockList))
                self.boardStates[currentID] = board.boardState
            
            # Choose a random move to execute (state and move)
            stateIDChoice = r.choice(list(moveQueues.keys()))
            moveChoice = r.choice(moveQueues[stateIDChoice])

            # Remove move choice from list and state from list if all moves have been chosen
            moveQueues[stateIDChoice].remove(moveChoice)
            if moveQueues[stateIDChoice] == []:
                moveQueues.pop(stateIDChoice)
            
            # Set the board in the desired state 
            # (1. update coords of the block, 
            #  2.Update the layout --> Inside the coord update,
            #  3.update the boardState attribute )
            boardStateChoice = copy.deepcopy(self.boardStates[stateIDChoice]) # Get state
            self.controller.updateCoords(oldBoard=board, newBoardState=boardStateChoice) # 1. , 2. and 3.
            
            blockID, direction, comp, othersideComp = moveChoice
            block = MovableBlock.registry[blockID]
            
            # Move
            notSolved = self.controller.moveBlock(block = block, board=board, direction=direction, 
                                                  component=comp, othersideComponent=othersideComp) # board is updated inside the function
    
            newID = self.stateToID(board.boardState)
            if newID not in self.stateGraph[stateIDChoice]:
                self.stateGraph[stateIDChoice].append(newID)
            if stateIDChoice not in self.stateGraph[newID]:
                self.stateGraph[newID].append(stateIDChoice)
            
        self.boardStates[newID] = board.boardState
        self.endID = newID
        print("Board Solved !")
        print(f"Solved state is {self.endID}")
        

        self.printSolution(board=board, startID=self.startID, endID=self.endID)
    
    def printSolution(self, board : Board, startID, endID):
        G = nx.from_dict_of_lists(self.stateGraph)

        shortest_path = nx.shortest_path(G, source=startID, target=endID)
        print(f"Found Shortest path ({len(shortest_path)} moves)")
        
        self.solutionLayouts = [] # board.board of every state of the path (updateBoard builds a new list each time, so no copy needed)
        for node in shortest_path:
            board_state = self.boardStates[node]
            self.controller.updateCoords(oldBoard=board, newBoardState=board_state)
            self.solutionLayouts.append(board.board)
            print(board)
        
        print("Done.")
        
        
        
    
    def fillMoveQueue(self, board : Board, blockList : list[MovableBlock]):
        """
        Fill a list with the necessary information to start a move 
        --> id, direction, comp, othersideComp
        """
        queue = []
        for block in blockList:
            up,down,left,right, topComp,botComp,leftComp,rightComp = block.checkPossibleMovevement(board)
            if up:
                queue.append((block.id, "UP", topComp, botComp))
            if down:
                queue.append((block.id, "DOWN", botComp, topComp))
            if left:
                queue.append((block.id, "LEFT", leftComp, rightComp))
            if right:
                queue.append((block.id, "RIGHT", rightComp, leftComp))
        
        return queue
    
    def stateToID(self, state : dict) :
        """
        Converts a state of the board into a supposedly unique identifier, 
        the order of the keys must not matter, only values (coords of blocks).
        
        hash function is sha1 because consistency between different runtime is preferred and it's fast.
        """
        state = {id : sorted(coords) for id,coords in state.items()} # Sort values of the state to have a consistent representation
        
        hashed = hashlib.sha1(repr(json.dumps(state, sort_keys=True)).encode()) 
        val = hashed.digest()
        return val
    
    def stateExists(self, state):
        id = self.stateToID(state)
        return id in self.boardStates.keys()
def findTopComponents(block) -> dict:
    topComponents = {}
    
    for row,col in block.coords:
        if not col in topComponents.keys() or (col in topComponents.keys() and row < topComponents[col]):
            topComponents[col] = row
    
    return topComponents

def findDownComponents(block) -> dict:
    bottomComponents = {}
    
    for row,col in block.coords:
        if not col in bottomComponents.keys() or (col in bottomComponents.keys() and row > bottomComponents[col]):
            bottomComponents[col] = row
        
    return bottomComponents
    
def findLeftComponents(block) -> dict:
    leftComponents = {}
    
    for row,col in block.coords:
        if not row in leftComponents.keys() or (row in leftComponents.keys() and col < leftComponents[row]):
            leftComponents[row] = col
    
    return leftComponents
    
def findRightComponents(block) -> dict:
    rightComponents = {}
    for row,col in block.coords:
        if not row in rightComponents.keys() or (row in rightComponents.keys() and col > rightComponents[row]):
            rightComponents[row] = col
    return rightComponents
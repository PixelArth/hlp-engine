def find_up_components(block) -> dict[int,int]:
    """
        Returns the coordinates of the components which are the highest for each COLUMNS of given block

        example :
        X are the components of the block
        [[0, 0, 0, 0, 0, 0]
        [0, 0, 0, 0, X, 0]
        [0, 0, 0, X, X, X]
        [0, 0, 0, X, X, 0]]

        would return the following dict :

        {
            3 : 2,
            4 : 1,
            5 : 2
        }
        keys are the COLUMNS and the values associated are the ROWS
    """
    up_components = {}

    for row,col in block.coords:
        if not col in up_components.keys() or (col in up_components.keys() and row < up_components[col]):
            up_components[col] = row

    return up_components

def find_down_components(block) -> dict[int,int]:
    """
        Returns the coordinates of the components which are the lowest for each COLUMNS of given block

        example :
        X are the components of the block
        [[0, 0, 0, 0, 0, 0]
        [0, 0, 0, 0, X, 0]
        [0, 0, 0, X, X, X]
        [0, 0, 0, X, X, 0]]

        would return the following dict :

        {
            3 : 3,
            4 : 3,
            5 : 2
        }
        keys are the COLUMNS and the values associated are the ROWS
    """
    down_components = {}

    for row,col in block.coords:
        if not col in down_components.keys() or (col in down_components.keys() and row > down_components[col]):
            down_components[col] = row

    return down_components

def find_left_components(block) -> dict[int,int]:
    """
        Returns the coordinates of the leftmost components for each ROWS of the given block

        example :
        X are the components of the block
        [[0, 0, 0, 0, 0, 0]
        [0, 0, 0, 0, X, 0]
        [0, 0, 0, X, X, X]
        [0, 0, 0, X, X, 0]]

        would return the following dict :

        {
            2 : 4,
            3 : 3,
            4 : 3
        }
        keys are the ROWS and the values associated are the COLUMNS
    """
    left_components = {}

    for row,col in block.coords:
        if not row in left_components.keys() or (row in left_components.keys() and col < left_components[row]):
            left_components[row] = col

    return left_components

def find_right_components(block) -> dict[int,int]:
    """
        Returns the coordinates of the rightmost components for each ROWS of the given block

        example :
        X are the components of the block
        [[0, 0, 0, 0, 0, 0]
        [0, 0, 0, 0, X, 0]
        [0, 0, 0, X, X, X]
        [0, 0, 0, X, X, 0]]

        would return the following dict :

        {
            2 : 4,
            3 : 5,
            4 : 4
        }
        keys are the ROWS and the values associated are the COLUMNS
    """
    right_components = {}
    for row,col in block.coords:
        if not row in right_components.keys() or (row in right_components.keys() and col > right_components[row]):
            right_components[row] = col
    return right_components

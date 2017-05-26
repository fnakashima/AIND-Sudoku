assignments = []
def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# Add diagonals to the unitlist below to include them in the units and peers
diagonal1 = [rows[i]+cols[i] for i in range(9)]
diagonal2 = [rows[i]+cols[8-i] for i in range(9)]
diagonal_units = [diagonal1, diagonal2]

unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    This is necessary to be done only when you want to display the game by Pygame.
    https://discussions.udacity.com/t/pygame-visualization/221951/2
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all boxes having two digits value
    two_values_boxes = {key: value for key, value in values.items() if len(value) == 2}
    #print('two_values_boxes=', two_values_boxes)
    for key, value in two_values_boxes.items():
        #print(key, value)
        # Get the relevant units of selected box
        target_units = units[key]
        for target_unit in target_units:
            #print('target_unit=', target_unit)
            twins = {k: v for k, v in values.items() if k in target_unit and key != k and value == v}
            #print('twins=', twins)
            # Find naked twins
            if(len(twins) == 1):
                # Make a list of values
                target_values = list(value)
                # Find any peers having more than two digits but not the same value as naked twins in the same unit 
                target_peers = {k: v for k, v in values.items() if k in target_unit and len(v) >= 2 and value != v}
                for pk, pv in target_peers.items():
                    for tv in target_values:
                        # If any value in naked twins is found, remove it from the box  
                        if tv in pv:
                            #print('Removing ', tv, ' from ', pk)
                            #values[pk] = pv.replace(tv,'')
                            assign_value(values, pk, pv.replace(tv,''))
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    keys = cross(rows, cols)
    values = [box if box != '.' else '123456789' for box in grid ]
    return dict(zip(keys, values))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    # Find already assigned boxes
    assigned_boxes = {key: value for key, value in values.items() if len(value) == 1}
    # Find unassigned boxes and its keys
    unassigned_boxes = {key: value for key, value in values.items() if len(value) != 1}
    unassigned_boxes_keys = unassigned_boxes.keys()
    #print('assigned_boxes=', assigned_boxes)
    #print('unassigned_boxes=', unassigned_boxes)
    
    for key, value in assigned_boxes.items():
        # Get peers of assigned box
        target_peers = peers[key]
        #print('target_box=', key, ', peers=', target_peers)
        for pkey in target_peers:
            #print('replacing key:', pkey)
            # Remove assigned value from peers
            #values[pkey] = values[pkey].replace(value,'')
            assign_value(values, pkey, values[pkey].replace(value,''))
    
    #print(values)
    return values

def only_choice(values):
    #print('unitlist=', unitlist)
    for unit in unitlist:
        #print('unit=', unit)
        for digit in '123456789':
            target_keys = [key for key in unit if digit in values[key]]
            #print('target_keys=', target_keys)
            # If any value is found in only box in the same unit, set the value to the box 
            if len(target_keys) == 1:
                #values[target_keys[0]] = digit
                assign_value(values, target_keys[0], digit)
    return values

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Use the Eliminate Strategy
        values = eliminate(values)

        # Use the Only Choice Strategy
        value = only_choice(values)

        # Use the Naked Twins Strategy
        value = naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, try all possible values."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
#     print('n=',n)
#     print('s=',s)
    
    for value in values[s]:
        #print('value=',value)
        # Create new sudoku by copying current sudoku for further search
        new_sudoku = values.copy()
        # Set possible value
        new_sudoku[s] = value
        # Use recurrence to solve each one of the resulting sudokus 
        attempt = search(new_sudoku)
        #print(n,s,value, attempt)
        # If any solution is found, return the result
        if attempt:
            return attempt
    #print("no solution")

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    # Convert grid(string) to dictionary 
    values = grid_values(grid)
    # Search and return the result
    return search(values)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')

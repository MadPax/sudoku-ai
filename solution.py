assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [ s+t for s in A for t in B ]

def dot(A,B):
    """
    Dot product of elements in A and elements in B.
    We use this function to create the 2 diagonal units  "A1, B2, C3,...I9" and "A9, B8, C7,...I1"
    """
    return [ A[i]+B[i] for i in range(0,9) ]

cols = '123456789'
rows = 'ABCDEFGHI'

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
# Compute the two lists of diagonal units "A1, B2..." and "A9, B8,..."
diagonal_units = [dot(rows, cols), dot(rows, cols[::-1])]
# Add the diagonal units to the global list of units from which we determine peers
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)

peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def grid_values(grid):
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def display(values):
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print

def eliminate(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit, ''))
    return values

def only_choice(values):
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
    return values

def reduce_puzzle(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    "Using depth-first search and propagation, try all possible values."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all(len(values[s]) == 1 for s in boxes):
        return values
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    return search(grid_values(grid))

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

def naked_twins(values):
    """
    Remove naked twins' values from fellow boxes in their unit
    """
    twins = dict()
    for unit_i in range(0, len(unitlist)):
        #for each unit, compute the values of all twins present in the unit
        twins[unit_i] = compute_twins(unitlist[unit_i], values)
    for unit_i in range(0, len(unitlist)):
        values = remove_naked_twins(twins[unit_i], unitlist[unit_i], values)
    return values

def compute_twins(unit, values):
    seen_values = []
    twin_values = []
    for box in unit:
        if len(values[box]) == 2:
            #If a value of length has already been "seen" in the unit, it's a twin!
            if values[box] in seen_values:
                twin_values.append(values[box])
            else:
                seen_values.append(values[box])
    return twin_values

def remove_naked_twins(twins, unit, values):
    """
    Method that removes naked twins from other values in the unit.
    The code is a bit ugly here and I'm open to suggestions to improve it!
    """
    for box in unit:
        for twin in twins:
            # The next check makes sure that we don't remove twins from the boxes that actually contain them
            if twin is not values[box]:
                # We now pick each digit from the twin to remove it from the box
                for c in twin:
                    if c in values[box]:
                        values[box] = values[box].replace(c, "")
    return values



from collections import defaultdict
assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

diagonals = []


def get_diagonals(rows, cols):
    cols_reverse = cols[::-1]
    d_one = []
    d_two = []
    for (row, col) in zip(rows, cols):
        d_one.append(row + col)
    for (row_, col_) in zip(rows, cols_reverse):
        d_two.append(row_ + col_)
    diagonals.append(d_one)
    diagonals.append(d_two)
    return diagonals

# this is needed to create all boxes in the sudoku


def cross(A, B):
    return [s + t for s in A for t in B]


boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
# Element example:
# row_units[0] = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9']
# This is the top most row.

column_units = [cross(rows, c) for c in cols]
# Element example:
# column_units[0] = ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'I1']
# This is the left most column.

square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI')
                for cs in ('123', '456', '789')]
# Element example:
# square_units[0] = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']
# This is the top left square.
diagonal_units = get_diagonals(rows, cols)

unitlist = row_units + column_units + square_units + diagonal_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)


def create_create_diagonal_boxes(rows, cols):
    for row, col in zip(rows, cols):
        print (row[row], cols[col])


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    # Don't waste memory appending actions that don't actually change any
    # values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
       If two cells in a group contain an identical pair of candidates and only those two candidates, then no other cells in that group could be those values.
        These 2 candidates can be excluded from other cells in the group.

    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # step one: find naked twins in rowunits, columnunits or squareunits
    for unit in unitlist:
        two_chars = {}
        for box in unit:
            # find boxes with two values:
            if len(values[box]) == 2:
                two_chars[box] = values[box]
        # iterate over pairs and find twins
        twins = defaultdict(list)
        for key, value in two_chars.items():
            twins[value].append(key)
        naked_twins = {}
        for key, value in twins.items():
            if len(value) == 2:
                naked_twins[key] = value
        if len(naked_twins) == 0:
            pass
        # step two: find boxes containing elements from the twin pairs
        else:
            # key is the twin value, the values are the box numbers
            for key, value in naked_twins.items():
                for box in unit:
                    if values[box] != key:
                        for element in key:
                            # step three: remove elements
                            if element in values[box]:
                                values[box] = values[box].replace(element, '')
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
    # transform string represantion to a dictionary
    # create the keys for the sudoku boxes
    # set up the sudoku grid
    grid_dict = dict(zip(boxes, grid))
    for key, value in grid_dict.items():
        if value == '.':
            grid_dict[key] = '123456789'
    return grid_dict


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """

    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF':
            print(line)
    return


def eliminate(values):
    # iterate over peers and remove number that is already solved
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit, '')
    return values


def only_choice(values):
    # remove all other possible values if there is only one choice for the unit
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
        return values


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len(
            [box for box in values.keys() if len(values[box]) == 1])
        eliminate(values)
        naked_twins(values)
        # only_choice(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len(
            [box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available
        # values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all(len(values[s]) == 1 for s in boxes):
        # solved
        return values
    # Choose one of the unfilled squares with the fewest possibilities
    n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    search(grid_values(grid))


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

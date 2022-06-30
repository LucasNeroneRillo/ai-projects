"""
Tic Tac Toe Player
"""

import math
import copy


X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    # Count number of cells marked on the board
    counter = 0
    for row in board:
        for cell in row:
            if not cell == EMPTY:
                counter += 1

    # Check who's turn it is
    if counter % 2 == 0:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    # Create and return a list of tuples with empty cells
    empty_cells = []
    for i in range(3):
        for j in range(3):
            cell = board[i][j]
            if cell == EMPTY:
                empty_cells.append((i, j))
    return empty_cells


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    # You'll only want to modify the board's copy
    board_copy = copy.deepcopy(board)

    # Variables i and j to simplify references
    i = action[0]
    j = action[1]

    # Check if action is valid
    if not board[i][j] == EMPTY:
        raise Exception("Invalid action")

    # Find out who's turn it is and update board's copy
    current_player = player(board_copy)
    board_copy[i][j] = current_player

    # Return updated board's copy
    return board_copy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # Check for horizontal winner
    for i in range(3):
        if board[i][0] != EMPTY and board[i][0] == board[i][1] == board[i][2]:
            return board[i][0]

    # Check for vertical winner
    for j in range(3):
        if board[0][j] != EMPTY and board[0][j] == board[1][j] == board[2][j]:
            return board[0][j]

    # Check for diagonal winner
    if not board[1][1] == EMPTY:
        if board[0][0] == board[1][1] == board[2][2]:
            return board[1][1]
        elif board[0][2] == board[1][1] == board[2][0]:
            return board[1][1]

    # If function has not returned yet, there is no winner
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # If actions list is empty, return True
    if not actions(board):
        return True
    elif winner(board) is not None:
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def min_value(board, alfa, beta):
    """
    Recursive function to get min_value
    """
    if terminal(board):
        return utility(board)

    v = 2
    for action in actions(board):
        w = max_value(result(board, action), alfa, beta)
        if w < v:
            v = w
        if w <= alfa:
            return v
        if w < beta:
            beta = w
    return v


def max_value(board, alfa, beta):
    """
    Recursive function to get max-value
    """
    if terminal(board):
        return utility(board)

    v = -2
    for action in actions(board):
        w = min_value(result(board, action), alfa, beta)
        if w > v:
            v = w
        if w >= beta:
            return v
        if w > alfa:
            alfa = w
    return v


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    # Check if board is not entirely filled
    if terminal(board):
        return None

    # Initialize variables
    current_player = player(board)
    move = None

    if current_player == X:
        # Get highest min_value possible and return the move that originates it
        v = -2
        for action in actions(board):

            current_result = result(board, action)
            alfa = - 2
            beta = 2

            if min_value(current_result, alfa, beta) > v:
                v = min_value(current_result, alfa, beta)
                move = action
        return move

    else:
        # Get smallest max_value possible and return the move that originates it
        v = 2
        for action in actions(board):

            current_result = result(board, action)
            alfa = - 2
            beta = 2

            if max_value(current_result, alfa, beta) < v:
                v = max_value(current_result, alfa, beta)
                move = action
        return move
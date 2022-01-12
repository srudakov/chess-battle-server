from enum import Enum, IntEnum
import logging

logger = logging.getLogger(__name__)
MAX_ROW = 7

class Color(Enum):
    WHITE = 1, 'white'
    BLACK = 2, 'black'
    def __init__(self, code, key_name):
        self.code = code
        self.key_name = key_name
    def get_start_row(self, offset):
        return offset if self == Color.WHITE else MAX_ROW - offset
    def next_to_move(self):
        return Color.BLACK if self == Color.WHITE else Color.WHITE

class CellKey(IntEnum):
    ROW = 0
    COLUMN = 1

class Column(Enum):
    A = 0, "A"
    B = 1, "B"
    C = 2, "C"
    D = 3, "D"
    E = 4, "E"
    F = 5, "F"
    G = 6, "G"
    H = 7, "H"
    def __init__(self, index, name):
        self.index = index
        self.code_name = name

class PieceType(Enum):
    PAWN = 0, "pawn", range(MAX_ROW + 1), 1
    KING = 1, "king", [Column.E], 0
    QUEEN = 2, "queen", [Column.D], 0
    ROOK = 3, "rook", [Column.A, Column.H], 0
    BISHOP = 4, "bishop", [Column.C, Column.F], 0
    KNIGHT = 5, "knight", [Column.B, Column.G], 0
    def __init__(self, index, name, start_columns, start_row_offset):
        self.index = index
        self.full_name = name
        self.start_columns = start_columns
        self.start_row_offset = start_row_offset

class PieceProperty(Enum):
    TYPE = 0
    COLOR = 1
    MOVED = 2

#Cell = tuple(int, Column)
#Piece = {PieceProperty: property_value}
#Board = {Cell: Piece}

def get_all_colors():
    return (Color.WHITE, Color.BLACK)

def get_color(color_name):
    for color in get_all_colors():
        if color.fullname == color_name:
            return color
    return None

def init_board():
    board = {}
    for piece_type in PieceType:
        for color in Color:
            row = color.get_start_row(piece_type.start_row_offset)
            for column in piece_type.start_columns:
                board[(row, column)] = {PieceProperty.TYPE: piece_type, PieceProperty.COLOR: color, PieceProperty.MOVED: False}
    return board

BOARD = {}
COLOR_TO_MOVE = None
LAST_MOVE = None

def start():
    logger.debug("new game requested")
    global BOARD, COLOR_TO_MOVE, LAST_MOVE
    BOARD = init_board()
    COLOR_TO_MOVE = Color.WHITE
    LAST_MOVE = None

def get_color_to_move():
    return COLOR_TO_MOVE

WINNER_KEY = "winner"
REASON_KEY = "reason"
FROM_KEY = "from"
TO_KEY = "to"

def check_move(move):
    return None

def make_move(move):
    result = check_move(move)
    if result is None:
        global COLOR_TO_MOVE, LAST_MOVE
        LAST_MOVE = move
        COLOR_TO_MOVE = COLOR_TO_MOVE.next_to_move()
    return result

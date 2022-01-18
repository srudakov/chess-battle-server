from enum import Enum, IntEnum
import logging
import re

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

class CellKey(Enum):
    ROW = 0
    COLUMN = 1

#Cell = {CellKey: row/column}
#Piece = {PieceProperty: property_value}
#Board = {Cell: Piece}
#Move = tuple(Cell, Cell)

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

def parse_cell(cell_str):
    found_column_key = re.search(r'[A-Z]', cell_str.upper())
    if found_column_key is None:
        return "no column in {}".format(cell_str)
    column_key = found_column_key.group(0)
    column = None
    for col in Column:
        if col.code_name == column_key:
            column = col
    if column is None:
        return "no column in {}".format(cell_str)
    found_row = re.search(r'\d', cell_str)
    if found_row is None:
        return "no row in {}".format(cell_str)
    try:
        row = int(found_row.group(0))
        if (row < 0) or (row > MAX_ROW):
            return "incorrect row: ".format(cell_str)
        return {CellKey.ROW: row, CellKey.COLUMN: column}
    except:
        return "no row in {}".format(cell_str)

def parse_move(move):
    from_cell = parse_move(move[FROM_KEY])
    to_cell = parse_move(move[TO_KEY])
    if isinstance(from_cell, str):
        return from_cell
    if isinstance(to_cell, str):
        return to_cell
    return {FROM_KEY: from_cell, TO_KEY: to_cell}
    

def check_move(move):
    if isinstance(move, str):
        return move
    return None

def make_move(move):
    parsed_move = parse_move(move)
    result = check_move(parsed_move)
    if result is None:
        global COLOR_TO_MOVE, LAST_MOVE
        LAST_MOVE = parsed_move
        COLOR_TO_MOVE = COLOR_TO_MOVE.next_to_move()
    return result

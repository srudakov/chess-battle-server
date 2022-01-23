from enum import Enum
import logging
import re
import chess

logger = logging.getLogger(__name__)
MIN_ROW = 1
MAX_ROW = 8
BOARD: chess.Board = None

MESSAGE_KEY = "message"
WINNER_KEY = "winner"
REASON_KEY = "reason"
FROM_KEY = "from"
TO_KEY = "to"

class Color(Enum):
    WHITE = 1, 'white'
    BLACK = 2, 'black'
    def __init__(self, code, key_name):
        self.code = code
        self.key_name = key_name
    def next_to_move(self):
        return Color.BLACK if self == Color.WHITE else Color.WHITE

def get_all_colors():
    return (Color.WHITE, Color.BLACK)

def start():
    logger.debug("new game requested")
    global BOARD
    BOARD = chess.Board()

def choose_color(is_white):
    return Color.WHITE if is_white else Color.BLACK

def game_exists():
    return BOARD is not None and BOARD.outcome() is None

def get_color_to_move():
    return choose_color(BOARD.turn) if game_exists() else None


def parse_cell(cell_str):
    found_column_key = re.search(r'[a-h]', cell_str.lower())
    if found_column_key is None:
        logger.error("no column in {}".format(cell_str))
        return None
    column = found_column_key.group(0)

    found_row = re.search(r'\d', cell_str)
    if found_row is None:
        logger.error("no row in {}".format(cell_str))
        return None
    try:
        row = int(found_row.group(0))
        if (row < MIN_ROW) or (row > MAX_ROW):
            logger.error("incorrect row: ".format(cell_str))
            return None
        return column + found_row.group(0)
    except:
        logger.error("no valid row in {}".format(cell_str))
        return None

def parse_move(move):
    from_cell = parse_cell(move[FROM_KEY])
    to_cell = parse_cell(move[TO_KEY])
    if from_cell is None or to_cell is None:
        return None
    trans = move.get("transform", "").lower()
    trans_postfix = "" if len(trans) == 0 else trans[0]
    trans_postfix = "n" if trans_postfix == "k" else trans_postfix
    return from_cell + to_cell + trans_postfix
    

def check_move(move):
    return chess.Move.from_uci(move) in BOARD.legal_moves


def get_finish_reason(reason):
    if reason == chess.Termination.CHECKMATE:
        return "мат"
    if reason == chess.Termination.STALEMATE:
        return "пат"
    if reason == chess.Termination.INSUFFICIENT_MATERIAL:
        return "недостаток материала"
    if reason == chess.Termination.FIVEFOLD_REPETITION or reason == chess.Termination.THREEFOLD_REPETITION:
        return "повторение"
    return reason


def make_move(move):
    color = get_color_to_move()
    parsed_move = parse_move(move)
    if parsed_move is None:
        return {WINNER_KEY: color.next_to_move().key_name, REASON_KEY: "incorrect move format"}
    if not check_move(parsed_move):
        logger.debug("incorrect move: {}".format(parsed_move))
        return {WINNER_KEY: color.next_to_move().key_name, REASON_KEY: "incorrect move"}
    BOARD.push_san(parsed_move)
    result = BOARD.outcome()
    if result is None:
        return None
    winner_color = "draw" if result.winner is None else choose_color(result.winner).key_name
    reason = get_finish_reason(result.termination)
    return {WINNER_KEY: winner_color, REASON_KEY: reason, MESSAGE_KEY: "end_game"}

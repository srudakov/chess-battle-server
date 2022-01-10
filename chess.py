from enum import Enum
import logging

logger = logging.getLogger(__name__)

class Color(Enum):
    WHITE = 1
    BLACK = 2

    def to_str(self):
        if self == Color.WHITE:
            return "white"
        if self == Color.BLACK:
            return "black"
        return ""

def get_all_colors():
    return (Color.WHITE, Color.BLACK)

def get_color(color_name):
    for color in get_all_colors():
        if color.to_str() == color_name:
            return color
    return None

def start():
    logger.debug("new game requested")

def get_color_to_move():
    return Color.WHITE

WINNER_KEY = "winner"
REASON_KEY = "reason"
FROM_KEY = "from"
TO_KEY = "to"

def check_move(move):
    return None
    

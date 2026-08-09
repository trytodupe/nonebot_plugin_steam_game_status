from enum import Enum


class GameTransition(Enum):
    SAME = "same"
    START = "start"
    SWITCH = "switch"
    STOP = "stop"
    BACKFILL = "backfill"


def classify_game_transition(
    previous_game_name: str,
    previous_game_id: str,
    current_game_id: str,
) -> GameTransition:
    if not current_game_id:
        return GameTransition.STOP if previous_game_name else GameTransition.SAME
    if not previous_game_name:
        return GameTransition.START
    if not previous_game_id:
        return GameTransition.BACKFILL
    if previous_game_id == current_game_id:
        return GameTransition.SAME
    return GameTransition.SWITCH

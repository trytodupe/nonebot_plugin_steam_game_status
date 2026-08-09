import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


status_path = Path(__file__).parents[1] / "nonebot_plugin_steam_game_status" / "status.py"
status_spec = spec_from_file_location("steam_game_status", status_path)
assert status_spec and status_spec.loader
status_module = module_from_spec(status_spec)
status_spec.loader.exec_module(status_module)

GameTransition = status_module.GameTransition
classify_game_transition = status_module.classify_game_transition


class ClassifyGameTransitionTest(unittest.TestCase):
    def test_localized_name_change_is_not_a_game_change(self):
        transition = classify_game_transition(
            previous_game_name="战地风云™ 6",
            previous_game_id="2807960",
            current_game_id="2807960",
        )

        self.assertEqual(transition, GameTransition.SAME)

    def test_different_game_id_is_a_game_change(self):
        transition = classify_game_transition(
            previous_game_name="战地风云™ 6",
            previous_game_id="2807960",
            current_game_id="730",
        )

        self.assertEqual(transition, GameTransition.SWITCH)

    def test_legacy_playing_state_is_backfilled_without_a_transition(self):
        transition = classify_game_transition(
            previous_game_name="战地风云™ 6",
            previous_game_id="",
            current_game_id="2807960",
        )

        self.assertEqual(transition, GameTransition.BACKFILL)

    def test_start_and_stop_are_detected(self):
        self.assertEqual(
            classify_game_transition("", "", "2807960"),
            GameTransition.START,
        )
        self.assertEqual(
            classify_game_transition("战地风云™ 6", "2807960", ""),
            GameTransition.STOP,
        )


if __name__ == "__main__":
    unittest.main()

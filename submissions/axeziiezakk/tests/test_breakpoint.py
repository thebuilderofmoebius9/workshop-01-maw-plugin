import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "breakpoint.py"
SPEC = importlib.util.spec_from_file_location("breakpoint", MODULE_PATH)
breakpoint = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(breakpoint)


class BreakpointOracleTests(unittest.TestCase):
    def test_start_creates_json_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"

            output = breakpoint.run(["start"], path=state_path, now=1000.0)

            self.assertIn("started", output)
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["active_session"]["started_epoch"], 1000.0)
            self.assertEqual(state["total_breaks"], 0)

    def test_check_reaches_break_point_after_25_minutes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            breakpoint.run(["start"], path=state_path, now=1000.0)

            output = breakpoint.run(["check"], path=state_path, now=2500.0)

            self.assertIn("Break point", output)
            self.assertIn("25m", output)

    def test_cheers_logs_break_and_restarts_timer(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            breakpoint.run(["start"], path=state_path, now=1000.0)

            output = breakpoint.run(["cheers"], path=state_path, now=1600.0)

            self.assertIn("Cheers, Axe", output)
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["total_breaks"], 1)
            self.assertEqual(state["completed_sessions"], 1)
            self.assertEqual(state["total_work_seconds"], 600.0)
            self.assertEqual(state["active_session"]["started_epoch"], 1600.0)

    def test_stats_includes_active_time_and_philosophy(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            breakpoint.run(["start"], path=state_path, now=1000.0)

            output = breakpoint.run(["stats"], path=state_path, now=1065.0)

            self.assertIn("Tracked court time: 1m 5s", output)
            self.assertIn("Keep the Human Human", output)


if __name__ == "__main__":
    unittest.main()

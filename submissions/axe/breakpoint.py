#!/usr/bin/env python3
"""Breakpoint Oracle: a gentle tennis-themed break coach."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_STATE_PATH = Path(__file__).with_name(".breakpoint_oracle_state.json")
STATE_ENV_VAR = "BREAKPOINT_ORACLE_STATE"

BREAKPOINT_SECONDS = 25 * 60
DEUCE_SECONDS = 45 * 60
MATCH_POINT_SECONDS = 60 * 60


def now_iso(now: float | None = None) -> str:
    timestamp = time.time() if now is None else now
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()


def format_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def empty_state(now: float | None = None) -> dict[str, Any]:
    stamp = now_iso(now)
    return {
        "created_at": stamp,
        "updated_at": stamp,
        "active_session": None,
        "completed_sessions": 0,
        "total_work_seconds": 0,
        "total_breaks": 0,
        "last_break_at": None,
    }


def state_path() -> Path:
    configured = os.environ.get(STATE_ENV_VAR)
    return Path(configured).expanduser() if configured else DEFAULT_STATE_PATH


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return empty_state()

    try:
        with path.open("r", encoding="utf-8") as handle:
            state = json.load(handle)
    except (OSError, json.JSONDecodeError):
        state = empty_state()

    base = empty_state()
    base.update(state)
    return base


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp_path.replace(path)


def active_elapsed_seconds(state: dict[str, Any], now: float | None = None) -> float:
    active = state.get("active_session")
    if not active:
        return 0
    current = time.time() if now is None else now
    return max(0, current - float(active["started_epoch"]))


def reminder_for(elapsed_seconds: float) -> tuple[str, str]:
    if elapsed_seconds >= MATCH_POINT_SECONDS:
        return (
            "Match point",
            "Axe, the pattern says this rally has gone long. A beer/rest break is available when you choose it.",
        )
    if elapsed_seconds >= DEUCE_SECONDS:
        return (
            "Deuce",
            "Long exchange with the machines. Consider resetting the breath before the next point.",
        )
    if elapsed_seconds >= BREAKPOINT_SECONDS:
        return (
            "Break point",
            "A useful opening for a pause: water, beer, stretch, or simply eyes off the AI for a minute.",
        )
    return (
        "Warm-up rally",
        "You are still moving well. Keep the human human; check the body before the scoreboard.",
    )


def command_start(path: Path, now: float | None = None) -> str:
    current = time.time() if now is None else now
    state = load_state(path)
    state["active_session"] = {
        "started_at": now_iso(current),
        "started_epoch": current,
    }
    state["updated_at"] = now_iso(current)
    save_state(path, state)
    return "Breakpoint Oracle started a new rally for Axe. Gentle reminders are now tracking the pattern."


def command_check(path: Path, now: float | None = None) -> str:
    current = time.time() if now is None else now
    state = load_state(path)
    if not state.get("active_session"):
        return "No active rally yet. Run `start` when Axe begins a focused work session."

    elapsed = active_elapsed_seconds(state, current)
    label, reminder = reminder_for(elapsed)
    return f"{label}: {format_duration(elapsed)} on court. {reminder}"


def command_cheers(path: Path, now: float | None = None) -> str:
    current = time.time() if now is None else now
    state = load_state(path)
    elapsed = active_elapsed_seconds(state, current)

    if state.get("active_session"):
        state["total_work_seconds"] = float(state.get("total_work_seconds", 0)) + elapsed
        state["completed_sessions"] = int(state.get("completed_sessions", 0)) + 1

    state["total_breaks"] = int(state.get("total_breaks", 0)) + 1
    state["last_break_at"] = now_iso(current)
    state["updated_at"] = now_iso(current)
    state["active_session"] = {
        "started_at": now_iso(current),
        "started_epoch": current,
    }
    save_state(path, state)

    if elapsed:
        duration = format_duration(elapsed)
        return f"Cheers, Axe. Logged a break after {duration}; new rally starts when you are ready."
    return "Cheers, Axe. Break logged; the next rally starts from here."


def command_stats(path: Path, now: float | None = None) -> str:
    current = time.time() if now is None else now
    state = load_state(path)
    active = active_elapsed_seconds(state, current)
    total = float(state.get("total_work_seconds", 0)) + active
    active_line = f"Active rally: {format_duration(active)}" if active else "Active rally: none"
    return "\n".join(
        [
            "Breakpoint Oracle stats",
            f"Completed rallies: {int(state.get('completed_sessions', 0))}",
            f"Beer/rest breaks: {int(state.get('total_breaks', 0))}",
            f"Tracked court time: {format_duration(total)}",
            active_line,
            "Philosophy: Keep the Human Human. The Oracle notices patterns; Axe decides.",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="breakpoint.py",
        description="Breakpoint Oracle: a tennis-themed break coach for Axe.",
    )
    parser.add_argument("command", choices=("start", "check", "cheers", "stats"))
    return parser


def run(argv: list[str] | None = None, path: Path | None = None, now: float | None = None) -> str:
    parser = build_parser()
    args = parser.parse_args(argv)
    resolved_path = state_path() if path is None else path

    handlers = {
        "start": command_start,
        "check": command_check,
        "cheers": command_cheers,
        "stats": command_stats,
    }
    return handlers[args.command](resolved_path, now)


def main(argv: list[str] | None = None) -> int:
    print(run(argv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

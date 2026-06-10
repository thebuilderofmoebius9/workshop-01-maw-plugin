# Breakpoint Oracle

Breakpoint Oracle is a small Python CLI for Axe: tennis coach, heavy AI user, and human who still needs real breaks.

The idea is simple: long AI work sessions can blur into one endless rally. Breakpoint Oracle keeps a local JSON state file, checks how long the current session has been running, and uses tennis language to offer gentle break cues:

- `Warm-up rally`: early session, keep checking the body.
- `Break point`: a useful opening for water, a beer, a stretch, or eyes off the screen.
- `Deuce`: the exchange is getting long; reset before the next point.
- `Match point`: the session has gone long enough that rest is strongly worth considering.

It follows the Oracle philosophy: **Keep the Human Human**. The tool does not command Axe. It notices patterns and reminds gently; the human decides.

## Usage

Run from the workspace root:

```bash
python3 quiz-beer-oracle/breakpoint.py start
python3 quiz-beer-oracle/breakpoint.py check
python3 quiz-beer-oracle/breakpoint.py cheers
python3 quiz-beer-oracle/breakpoint.py stats
```

## Commands

- `start`: starts or restarts the active work rally.
- `check`: shows the current tennis-state reminder.
- `cheers`: logs a beer/rest break and starts a fresh rally timer.
- `stats`: prints completed rallies, breaks, tracked court time, and the active rally.

## State

By default, state is stored at:

```text
quiz-beer-oracle/.breakpoint_oracle_state.json
```

For tests or alternate local use, set:

```bash
BREAKPOINT_ORACLE_STATE=/tmp/breakpoint-state.json python3 quiz-beer-oracle/breakpoint.py start
```

Only Python standard library modules are used; no pip install is required.

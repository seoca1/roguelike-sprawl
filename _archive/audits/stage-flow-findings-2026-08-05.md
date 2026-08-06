# Stage Flow Data Findings (2026-08-05)

> **For user decision** — stage structure data fix requires ADR per AGENTS.md §3.2.
> Discovered during cycle 7+ audit. Two non-terminal stages lack outgoing transitions.

## Issue 1: black_market & ghost_encounter missing transitions

### Current state (`design/systems/stage_structure.json`)

Two non-terminal stages have `next_stage` defined but no entry in the `transitions` array:

| Stage | next_stage | Has transition? |
|---|---|---|
| `black_market` | `pending` | ❌ No |
| `ghost_encounter` | `defeat_ice` | ❌ No |

### Validator output (`scripts/validate_stage_structure.py`)

```
[OK] All 14 stages valid (including 6 required)
[OK] All stage ids unique
[OK] All 13 transitions valid
[FAIL] non-terminal stage 'black_market' has no outgoing transition
```

### Hidden bug: validator early-exits on first failure

`scripts/validate_stage_structure.py:56`:
```python
def fail(msg: str) -> None:
    print(f"  [FAIL] {msg}")
    raise SystemExit(1)
```

This means `ghost_encounter` ALSO has the same bug but is never reported. **Both stages need fixing**.

### Resolution paths (user decision)

**Option A**: Add transitions to `transitions[]` array
```json
{
  "from": "black_market",
  "to": "pending",
  "condition": "after_vendor_exit"
},
{
  "from": "ghost_encounter",
  "to": "defeat_ice",
  "condition": "loa_dialogue_complete"
}
```

**Option B**: Mark both stages as `is_terminal: true` (gameplay terminates at these)

**Option C**: Hybrid (e.g. add transition for one, mark other terminal)

Each option requires:
1. New ADR or amendment to existing (per AGENTS.md §3.2)
2. Update `design/systems/stage_structure.json`
3. Update `design/systems/dungeon_events.md` (cross-doc)
4. Regression test in `testcases/`

### Issue 2: Validator early-exit (separate)

Even after the data is fixed, the validator's `raise SystemExit(1)` on first failure means future issues will be hidden.

**Suggested fix** (low priority — user decision):
```python
fails: list[str] = []

def fail(msg: str) -> None:
    fails.append(msg)
    print(f"  [FAIL] {msg}")

# At end of validate():
if fails:
    raise SystemExit(f"{len(fails)} failures: {fails}")
```

This collects all failures before exiting.

## Verification

```
$ uv run python scripts/validate_stage_structure.py
[OK] JSON parsed successfully
[OK] Top-level structure present
[OK] All 14 stages valid (including 6 required)
[OK] All stage ids unique
[OK] All 13 transitions valid
[FAIL] non-terminal stage 'black_market' has no outgoing transition  ← exits here, ghost_encounter hidden
```

## Recommended next action

This finding DOES NOT block v1.1.0 release (these are design data issues, not code bugs). However, addressing them improves stage completeness.

Recommend:
1. Decide which option (A/B/C) is correct based on gameplay intent
2. Update ADR + data + tests together
3. Optional: also fix the validator to collect all failures before exiting

Both issues tracked in this memo. Decision yours.

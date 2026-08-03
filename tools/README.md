# Roguelike Sprawl Tools

> **Parent**: `Game/roguelike_sprawl/` Python roguelike project
> **Updated**: 2026-07-28

Python build and data-prep utilities for the roguelike_sprawl prototype.

## Structure

```
Game/roguelike_sprawl/tools/
├── build_dashboard.py    # Build static dashboard JSON for GitHub Pages
└── build_static_data.py  # Generate static game data (missions, items, etc.)
```

## Tools

### Active

| Tool | Purpose | Usage |
|------|---------|-------|
| **`build_dashboard.py`** | Generate dashboard JSON (Story, Stages, Combat, Equipment, Cyberspace) | `python3 tools/build_dashboard.py` |
| **`build_static_data.py`** | Generate static game data files | `python3 tools/build_static_data.py` |

Both tools feed `data/` (consumed by prototype runtime) and `docs/dashboards/` (consumed by GitHub Pages deploy).

## Conventions

- Python 3.11+
- Each tool reads from `prototype/src/data/` constants and writes to `data/` and `docs/dashboards/`
- Re-run before deploy to refresh dashboard data

## See also

- `Game/roguelike_sprawl/prototype/Makefile` — top-level build targets (`build-dashboard`, `build-data`)
- `Game/roguelike_sprawl/CHANGELOG.md` — change history
- `Game/roguelike_sprawl/wiki/index.md` — wiki navigation

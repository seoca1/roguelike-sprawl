.PHONY: help install sync run test lint format typecheck build clean download-font all

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

sync: ## Install/sync dependencies with uv
	uv sync --all-extras

install: sync ## Alias for sync

download-font: ## Download the libtcod font (one-time)
	uv run python scripts/download_font.py

run: ## Run the game (hello-world)
	uv run roguelike-sprawl

prologue: ## Play the prologue cinematic
	uv run python scripts/prologue.py

prologue-fast: ## Play the prologue (fast typing)
	uv run python scripts/prologue.py --speed fast

briefing: ## Play the Finn briefing scene
	uv run python scripts/prologue.py --scene briefing

demo: ## Full game demo with Korean subtitles (Prologue → Briefing → Matrix → Combat)
	uv run python scripts/full_demo.py

demo-en: ## English-only demo (no Korean)
	uv run python scripts/full_demo.py --no-korean

demo-fast: ## Full game demo (fast typing)
	uv run python scripts/full_demo.py --fast

demo-skip: ## Skip prologue and start at briefing
	uv run python scripts/full_demo.py --skip-prologue

play: ## Interactive playthrough with Korean subtitles
	uv run python scripts/full_demo.py --interactive

play-en: ## Interactive playthrough, English-only
	uv run python scripts/full_demo.py --interactive --no-korean

text-demo: ## Text-only demo (no graphics, for verification)
	uv run python scripts/text_demo.py --fast

# --- Graphic Novel (GUI window) ---
# Requires display/window environment. Launches actual game window.
gn: ## Graphic Novel — GUI window (case/novice)
	uv run python scripts/play.py --gn-mode novice

gn-veteran: ## Graphic Novel — GUI window (sil/veteran)
	uv run python scripts/play.py --gn-mode veteran

gn-heretic: ## Graphic Novel — GUI window (kas/heretic)
	uv run python scripts/play.py --gn-mode heretic

gn-all: ## Graphic Novel — GUI window (all 12 scenes shuffled)
	uv run python scripts/play.py --gn-mode prologue

# --- Graphic Novel (text/headless) ---
# No window required. Terminal output only.
gn-text: ## Graphic Novel — text mode (case/novice)
	uv run python scripts/graphic_novel.py --mode novice --speed 50

gn-text-veteran: ## Graphic Novel — text mode (sil/veteran)
	uv run python scripts/graphic_novel.py --mode veteran --speed 50

gn-text-heretic: ## Graphic Novel — text mode (kas/heretic)
	uv run python scripts/graphic_novel.py --mode heretic --speed 50

gn-text-all: ## Graphic Novel — text mode (all 12 scenes)
	uv run python scripts/graphic_novel.py --mode prologue --seed 42 --speed 50

test-tcod: ## Test tcod font rendering
	uv run python scripts/test_tcod.py

test: ## Run tests with pytest
	uv run pytest

test-cov: ## Run tests with coverage
	uv run pytest --cov

lint: ## Run ruff linter
	uv run ruff check .

format: ## Format code with ruff
	uv run ruff format .

typecheck: ## Run mypy type checker
	uv run mypy src/

build: ## Build the package
	uv build

clean: ## Clean build artifacts and caches
	rm -rf dist/ build/ *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov/
	find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true

all: format lint typecheck test ## Run all checks (format, lint, typecheck, test)

# --- Sound system ---
.PHONY: sound-test sound-manager sound-demo sound-demo-full sound-clean

sound-test: ## Test which audio backends are available
	uv run python scripts/test_sound_libraries.py

sound-manager: ## Run SoundManager unit tests
	uv run python -m pytest tests/unit/test_sound_manager.py -v

sound-demo: ## Play all 27 default sounds in sequence
	uv run python scripts/demo_sounds.py

sound-demo-full: ## Full game demo with sound integration
	uv run python scripts/full_demo_sound.py

sound-clean: ## Remove generated sound files
	rm -rf data/sounds_test/

# --- Avatar ---
.PHONY: demo-avatar

demo-avatar: ## Show Jockey Avatar visual demo (ADR-0016)
	uv run python scripts/demo_avatar.py

# --- Full demo (GUI + sound) ---
.PHONY: demo-sound-full demo-sound-headless

demo-sound-full: ## Full game demo with sound (requires GUI/display)
	uv run python scripts/full_demo_sound.py

demo-sound-headless: ## Headless sound demo (audio + text, no GUI required)
	uv run python scripts/headless_sound_demo.py

# --- Cinematic art ---
.PHONY: demo-art

demo-art: ## Show cinematic ASCII art demo
	uv run python scripts/demo_cinematic_art.py

# --- Prologue verification ---
.PHONY: verify-prologue

verify-prologue: ## Headless verification of prologue + briefing scenes
	uv run python scripts/verify_prologue.py

# --- Dashboard ---
.PHONY: dashboard dashboard-validate

dashboard: ## Open project dashboard in browser
	@echo "Opening http://localhost:8765/dashboard/index.html"
	@echo "(Run 'make dashboard-server' in another terminal if not already running)"
	open http://localhost:8765/dashboard/index.html 2>/dev/null || \
	  xdg-open http://localhost:8765/dashboard/index.html 2>/dev/null || \
	  echo "Open manually: http://localhost:8765/dashboard/index.html"

dashboard-server: ## Start local HTTP server for dashboard (port 8765)
	uv run python -m http.server 8765

dashboard-validate: ## Validate prologue_data.json structure
	uv run python scripts/validate_prologue_data.py

# --- Event dialogues validation ---
.PHONY: validate-event-dialogues

validate-event-dialogues: ## Validate event_dialogues.json structure
	uv run python scripts/validate_event_dialogues.py

# --- Stage structure validation ---
.PHONY: validate-stage-structure

validate-stage-structure: ## Validate stage_structure.json
	uv run python scripts/validate_stage_structure.py

# --- Top hub (cross-project) ---
.PHONY: hub

hub: ## Open cross-project dashboard hub (Game/dashboard/index.html)
	@echo "Cross-project hub: http://localhost:8765/dashboard/index.html"
	open http://localhost:8765/dashboard/index.html 2>/dev/null || \
	  xdg-open http://localhost:8765/dashboard/index.html 2>/dev/null || \
	  echo "Open manually: http://localhost:8765/dashboard/index.html"

dashboard-server: ## Start local HTTP server at Game/ level (port 8765)
	cd $(CURDIR)/../.. && $(CURDIR)/.venv/bin/python -m http.server 8765

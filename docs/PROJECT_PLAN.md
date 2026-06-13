# LogLens - Project Plan

> **Purpose:** source-of-truth roadmap. Lives in the repo so any contributor (human or AI) can resume work from the current phase.
>
> **Maintenance:** update on every phase close. The Phase Status table reflects current state. The Change Log records what shifted between phase closures.
>
> **Restart pattern (lost chat):** *"Working on loglens (github.com/PritKalariya/loglens). Plan is in `docs/PROJECT_PLAN.md`. Currently at Phase X. Continue."*

---

## Project Overview

LogLens is a machine learning classifier for system log lines, trained on the [LogHub](https://github.com/logpai/loghub) BGL or HDFS datasets and exposed via a FastAPI `/predict` endpoint.

**Scope:** end-to-end ML service covering environment management, model training, API serving, testing, CI/CD, containerization, and cloud deployment. Each phase isolates one layer.

**Repo:** https://github.com/PritKalariya/loglens

---

## Working Philosophy

Each phase has two stages:

1. **Learning sprint** - move fast, write code in notebooks, prototype messily, prioritize understanding over hygiene. Goal: internalize what the phase teaches.
2. **Polish pass** - once learning is solid, promote notebook code to modules, add tests, update README, write any missing scripts. The phase closes only after polish.

Tests, typed modules, scripts, and documentation polish are deliberately deferred until learning is done. Premature abstraction during a learning sprint kills the feedback loop the sprint exists for. The phases below describe both stages where applicable.

---

## Phase Status

| Phase | Title | Status |
|-------|-------|--------|
| 1 | Identity Foundation (Git + GitHub) | ✅ Done |
| 2 | Project Scaffold (uv + folder layout) | ✅ Done |
| 3 | Quality Gates + Public Repo | ✅ Done |
| 4 | Data Layer (LogHub ingestion + EDA) | ✅ Done |
| 5 | Baseline Model (TF-IDF + LogReg) | 🟡 Current |
| 6 | FastAPI Inference Endpoint | 🔵 Planned |
| 7 | CI/CD via GitHub Actions | 🔵 Planned |
| 8 | Containerization + Cloud Deploy (capstone) | 🔵 Planned |

Legend: ✅ Done · 🟡 Current · 🔵 Planned · ⚪ Deferred · ❌ Dropped

---

## Phase 1 - Identity Foundation ✅

**Goal:** local machine interacts with GitHub securely.

**Completed:**
- Git installed and globally configured (`user.name`, `user.email`, `init.defaultBranch=main`, `pull.rebase=false`, `core.editor="code --wait"`)
- ed25519 SSH key generated at `~/.ssh/id_ed25519`
- Public key registered with the GitHub account
- `ssh -T git@github.com` returns authenticated handshake

**Exit criteria:** push to GitHub succeeds from local machine.

---

## Phase 2 - Project Scaffold ✅

**Goal:** reproducible Python environment + professional folder layout + initial dependencies.

**Completed:**
- uv installed
- Project created via `uv init --package loglens --python 3.12` (src/ layout)
- Direct dependencies added: `scikit-learn`, `pandas`, `fastapi`, `uvicorn[standard]`
- `uv.lock` committed
- ML folder structure: `data/{raw,processed,external}/`, `models/`, `notebooks/`, `tests/` (with `.gitkeep` for empty dirs)
- ML-aware `.gitignore` (datasets, model artifacts, secrets, mlruns, OS junk)
- First commit: `chore: scaffold project with uv, src layout, ML folders, gitignore`

**Exit criteria:** `uv sync` on fresh clone reproduces the environment exactly.

---

## Phase 3 - Quality Gates + Public Repo ✅

**Goal:** automatic code quality + README/LICENSE + repo published.

**Completed:**
- `ruff` configured in `pyproject.toml` (line-length 100; lint families E/W/F/I/B/C4/UP/SIM/N)
- `pre-commit` hooks: trailing whitespace, end-of-file, YAML/TOML check, large-file guard, merge-conflict marker, private-key detection, ruff, ruff-format
- `.pre-commit-config.yaml` committed and active
- README: hook paragraph, status checklist, tech stack, quickstart, structure, dataset citation
- MIT LICENSE
- VS Code: `files.insertFinalNewline` and `files.trimTrailingWhitespace` enabled
- GitHub repo created (public); local pushed to `origin/main`
- About topics set: `machine-learning`, `fastapi`, `scikit-learn`, `mlops`, `log-analysis`

**Exit criteria:** repo lives publicly at github.com/PritKalariya/loglens; README renders; commit history visible.

---

## Phase 4 - Data Layer ✅

**Goal:** working loader that returns a clean `(text, label)` DataFrame; class balance understood.

**Note on dataset:** at full scale LogHub publishes only the raw `BGL.log` on Zenodo. The structured CSV exists only as a 2,000-line sample, too small for training, so the raw file is parsed directly.

**Learning sprint (completed):**
- Acquired raw `BGL.log` (~4.75M lines) under `data/raw/`
- Parsed the 10-field format with `str.split(n=9)` (Content field contains spaces, breaks naive CSV parsing)
- Chose `text` = Content only, `Level` excluded (excluding Level avoids leaking the label into features)
- Binarized label (0 = normal, 1 = anomaly)
- Recorded class balance and surfaced key data findings

**Key data findings:**
- Raw anomaly ratio: 7.34%; **unique-row anomaly ratio: 13.69%** (normal logs are more templated than anomalies)
- **92% of lines are exact duplicates** - only ~358K unique texts out of 4.75M. Drives the dedup-before-split decision in Phase 5.
- 3 texts carry inconsistent labels (label noise, < 0.001% impact)
- ~316 malformed rows dropped via canonical Level filter; ~34K null-Content rows dropped

**Polish pass (completed):**
- [x] Loader promoted to `src/loglens/data.py` (`load_bgl(path, deduplicate=True)`, `CANONICAL_LEVELS` constant)
- [x] `data/raw/README.md` documenting source, license, parser assumptions, and why the folder is empty on a fresh clone
- [x] `tests/test_data.py`: 11 tests covering shape, nulls, label domain, dedup, malformed-row dropping (all passing)
- [x] Committed and pushed (`feat(data): added BGL loader, tests, and dataset docs`)

**Required reading:** [LogHub repo overview](https://github.com/logpai/loghub).

**Exit criteria:** loader works and is tested; class balance recorded; `text` decision documented; polish pass committed. ✅

---

## Phase 5 - Baseline Model 🔵

**Goal:** end-to-end baseline - log line in, predicted label out.

**Planned work:**
- `src/loglens/features.py` - TF-IDF vectorizer pipeline
- `src/loglens/model.py` - `train()` and `predict()`; scikit-learn `Pipeline` bundling vectorizer + classifier
- Logistic Regression baseline
- Serialize to `models/loglens-v0.joblib`
- Evaluate: precision, recall, F1, confusion matrix, classification report
- `scripts/train.py` - reproducible training entrypoint
- Tests: trains on tiny sample without error; predict returns valid label

**Deliverable:** trained model artifact + reproducible training script.

**Required reading:** [scikit-learn - Working with Text Data](https://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html).

**Exit criteria:** `uv run python scripts/train.py` produces a working model artifact; tests pass.

---

## Phase 6 - FastAPI Inference Endpoint 🔵

**Goal:** `/predict` endpoint serving the trained model at `localhost:8000`.

**Planned work:**
- `src/loglens/api.py` - FastAPI app, model loaded at startup via lifespan handler, `/predict` and `/health` endpoints
- Pydantic request/response schemas
- Error handling: unloaded model, malformed input, prediction failure → correct HTTP status codes
- `tests/test_api.py` with `TestClient`: happy path, edge cases, error paths
- Manual verification via `curl` and auto-generated Swagger UI at `/docs`

**Deliverable:** `uv run uvicorn loglens.api:app --reload` serves predictions.

**Required reading:** [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/) - "First Steps" through "Request Body".

**Exit criteria:** `curl -X POST localhost:8000/predict -d '{"line": "..."}'` returns a valid JSON prediction.

---

## Phase 7 - CI/CD via GitHub Actions 🔵

**Goal:** every push triggers automated tests + lint.

**Planned work:**
- `.github/workflows/ci.yml` - triggers on push and PR
- Steps: checkout, setup Python 3.12, install uv, `uv sync --dev`, `pre-commit run --all-files`, `pytest`
- CI status badge in README
- Branch protection on `main`: require CI green before merge

**Deliverable:** green CI badge in README; commits display ✓ on GitHub.

**Required reading:** [GitHub Actions Quickstart](https://docs.github.com/en/actions/quickstart) + `actions/setup-python` README.

**Exit criteria:** broken commit on feature branch fails CI; passing commit on `main` shows green badge.

---

## Phase 8 - Containerization + Cloud Deploy 🔵 (Capstone)

**Goal:** deployable service with a public URL.

**Planned work:**
- Focused Docker learning detour (2-3 days) before adding the tool
- Multi-stage `Dockerfile`: builder + minimal runtime (with uv cache mounts)
- `docker compose up` runs the full stack locally
- Push image to GitHub Container Registry
- Deploy target chosen at phase start: AWS App Runner / Fly.io / Railway
- Public URL added to README

**Stretch (optional, post-capstone):**
- MLflow experiment tracking + model registry
- Prometheus metrics + Grafana dashboard
- Load testing (locust / k6)
- A/B serving two model versions

**Deliverable:** public URL returning predictions to any internet client.

**Required reading:** [Docker Get Started](https://docs.docker.com/get-started/).

**Exit criteria:** curl from an external machine returns a prediction from the deployed service.

---

## Decision Log

Decisions that propagate forward; not revisited without reason.

| Made in Phase | Decision | Revisit if |
|---------------|----------|------------|
| 2 | Python 3.12 | 3.12 reaches EOL or required libs require 3.13+ |
| 2 | uv as package manager | Team mandate for poetry/pip |
| 2 | src/ layout | Never expected |
| 3 | MIT license | Patent grant becomes relevant |
| 3 | ruff (replaces flake8/isort/black) | Never expected |
| 3 | Pre-commit hooks (not CI-only) | Never expected |
| 3 | Conventional Commits | Never expected |
| 4 | BGL dataset (over HDFS / Thunderbird) | Scaling test needed (Thunderbird listed as Phase 8 stretch) |
| 4 | Notebook-first; promote to module only when imported elsewhere | Never expected (general principle) |
| 4 | Text input = Content only, Level excluded | After baseline; full-row variant as ablation experiment |
| 4 | Train on unique (deduplicated) texts; consider raw distribution at eval | When evaluating - report both training-view and production-view metrics |
| 4 | Drop malformed rows via canonical Level filter | Never expected |
| Pending | Defer Docker until Phase 8 | After Phase 7 closes |

---

## Conventions

- **Commits:** Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `test:`, `refactor:`)
- **Branches:** `main` always deployable; feature work on `feat/<slug>` branches, PR-merged once CI is live (Phase 7+)
- **Tests:** each module in `src/loglens/` has a matching `tests/test_<module>.py`
- **Required reading:** completed before implementation work on the phase begins

---

## Change Log

Updates to this plan, keyed to phase completions (most recent first).

- **After Phase 4 close** - BGL loader promoted to `src/loglens/data.py` (`deduplicate` flag, `CANONICAL_LEVELS` constant); 11 passing tests; dataset documented in `data/raw/README.md`. Data findings: 92% duplicate lines, 13.69% anomaly ratio on unique rows vs 7.34% raw. Structured CSV unavailable at full scale, so raw file is parsed directly.
- **After Phase 3 close** - repo published on GitHub; VS Code settings standardized for pre-commit compliance; this plan committed to `docs/`.
- **After Phase 2 close** - scaffold committed; ML folder structure established.
- **After Phase 1 close** - identity layer verified.
- **Initial draft** - all 8 phases defined.

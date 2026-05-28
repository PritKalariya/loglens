# LogLens

A machine learning classifier for system log lines, trained on the [LogHub](https://github.com/logpai/loghub) BGL/HDFS datasets. Exposes a FastAPI `/predict` endpoint for real-time inference.

## Why

Operations teams generate millions of log lines daily. Most are routine; a small fraction signal failures, security incidents, or anomalies. This project explores a lightweight ML approach to surfacing the signal from the noise — the kind of foundational classifier that sits underneath modern observability platforms (Datadog, Splunk, New Relic).

## Status

🚧 Under active development — building out the MLOps pipeline incrementally.

- [x] Project scaffold, tooling, CI-ready quality gates
- [ ] Dataset ingestion (LogHub)
- [ ] Baseline classifier (TF-IDF + Logistic Regression)
- [ ] FastAPI `/predict` endpoint
- [ ] Dockerization
- [ ] CI/CD via GitHub Actions
- [ ] Cloud deployment

## Tech Stack

- **Python 3.12** — managed by [uv](https://github.com/astral-sh/uv)
- **scikit-learn** — model training
- **FastAPI + uvicorn** — inference API
- **pandas** — data wrangling
- **ruff** — lint + format
- **pre-commit** — automated quality gates
- **pytest** — testing

## Quickstart

```bash
# Clone
git clone git@github.com:PritKalariya/loglens.git
cd loglens

# Install dependencies (uv reads pyproject.toml + uv.lock)
uv sync

# Verify the environment
uv run python -c "import sklearn, pandas, fastapi; print('OK')"
```

## Project Structure
```
loglens/
├── data/             # Datasets (gitignored)
│   ├── raw/          # Original LogHub dumps
│   ├── processed/    # Cleaned/labeled data
│   └── external/     # Third-party reference data
├── models/           # Trained model artifacts (gitignored)
├── notebooks/        # Jupyter exploration
├── src/loglens/      # Application package
├── tests/            # pytest suite
├── pyproject.toml    # Dependencies + tool config
└── uv.lock           # Locked dependency versions
```

## Development

```bash
# Run all quality checks manually
uv run pre-commit run --all-files

# Run tests
uv run pytest

# Format and lint
uv run ruff format .
uv run ruff check . --fix
```

## Dataset

Built against [LogHub](https://github.com/logpai/loghub), a large collection of system logs released by the LogPAI team for log analysis research. Cite:

> Zhu, J., He, S., He, P., Liu, J., & Lyu, M. R. (2023). Loghub: A large collection of system log datasets for AI-driven log analytics. *IEEE ISSRE*.

## License

MIT

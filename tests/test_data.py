"""Tests for the BGL data loader."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from loglens.data import CANONICAL_LEVELS, load_bgl

# A tiny synthetic BGL log covering the cases the loader must handle:
#   - a normal line ("-")                              -> label 0
#   - two anomaly lines (KERNDTLB, APPSEV)             -> label 1
#   - a duplicate of the normal line                   -> dedup target
#   - a malformed line with a non-canonical Level      -> dropped
SAMPLE_LOG = (
    "- 1117838570 2005.06.03 R02-M1-N0-C:J12-U11 2005-06-03-15.42.50.363779 "
    "R02-M1-N0-C:J12-U11 RAS KERNEL INFO instruction cache parity error corrected\n"
    "KERNDTLB 1118536327 2005.06.11 R30-M0-N9-C:J16-U01 2005-06-11-17.32.07.581048 "
    "R30-M0-N9-C:J16-U01 RAS KERNEL FATAL data TLB error interrupt\n"
    "APPSEV 1119012345 2005.06.17 R10-M1-N4-C:J05-U11 2005-06-17-09.15.00.000001 "
    "R10-M1-N4-C:J05-U11 RAS APP ERROR application severe fault\n"
    "- 1117838571 2005.06.03 R02-M1-N0-C:J12-U11 2005-06-03-15.42.51.131467 "
    "R02-M1-N0-C:J12-U11 RAS KERNEL INFO instruction cache parity error corrected\n"
    "- 1119999999 2005.06.20 R01-M0-N0-C:J00-U01 2005-06-20-00.00.00.000000 "
    "R01-M0-N0-C:J00-U01 RAS KERNEL KILL malformed garbage line\n"
)


@pytest.fixture
def sample_log_path(tmp_path: Path) -> str:
    """Write the synthetic log to a temp file and return its path."""
    log_file = tmp_path / "BGL_sample.log"
    log_file.write_text(SAMPLE_LOG, encoding="utf-8")
    return str(log_file)


def test_returns_dataframe(sample_log_path: str) -> None:
    result = load_bgl(sample_log_path)
    assert isinstance(result, pd.DataFrame)


def test_has_exactly_text_and_label_columns(sample_log_path: str) -> None:
    result = load_bgl(sample_log_path)
    assert list(result.columns) == ["text", "label"]


def test_no_null_text(sample_log_path: str) -> None:
    result = load_bgl(sample_log_path)
    assert result["text"].isnull().sum() == 0


def test_label_domain_is_binary(sample_log_path: str) -> None:
    result = load_bgl(sample_log_path)
    assert set(result["label"].unique()).issubset({0, 1})


def test_label_dtype_is_int(sample_log_path: str) -> None:
    result = load_bgl(sample_log_path)
    assert pd.api.types.is_integer_dtype(result["label"])


def test_malformed_row_is_dropped(sample_log_path: str) -> None:
    # The "KILL" Level line is malformed and must not appear.
    result = load_bgl(sample_log_path)
    assert not result["text"].str.contains("malformed garbage").any()


def test_deduplicate_removes_repeated_text(sample_log_path: str) -> None:
    # Two identical normal lines -> one row when deduplicated.
    deduped = load_bgl(sample_log_path, deduplicate=True)
    assert deduped["text"].duplicated().sum() == 0
    # 3 unique valid texts: normal, KERNDTLB anomaly, APPSEV anomaly.
    assert len(deduped) == 3


def test_no_deduplicate_keeps_repeated_text(sample_log_path: str) -> None:
    # Without dedup: 4 valid rows (2 normal duplicates + 2 anomalies).
    full = load_bgl(sample_log_path, deduplicate=False)
    assert len(full) == 4
    assert full["text"].duplicated().sum() == 1


def test_anomaly_labeled_correctly(sample_log_path: str) -> None:
    result = load_bgl(sample_log_path)
    anomaly = result[result["text"] == "data TLB error interrupt"]
    assert anomaly["label"].iloc[0] == 1


def test_normal_labeled_correctly(sample_log_path: str) -> None:
    result = load_bgl(sample_log_path)
    normal = result[result["text"] == "instruction cache parity error corrected"]
    assert normal["label"].iloc[0] == 0


def test_canonical_levels_is_frozenset() -> None:
    # Guard against accidental mutation of the module constant.
    assert isinstance(CANONICAL_LEVELS, frozenset)
    assert "INFO" in CANONICAL_LEVELS

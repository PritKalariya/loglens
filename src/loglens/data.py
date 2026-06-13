"""Data loading and preprocessing for the BGL log dataset.

Parses the raw BGL.log file into a clean ``(text, label)`` DataFrame suitable
for training a binary log-anomaly classifier.
"""

from __future__ import annotations

import pandas as pd

# Canonical Level values defined by the BGL schema. Rows whose Level falls
# outside this set are malformed (field-shift artifacts from naive splitting)
# and are dropped during loading.
CANONICAL_LEVELS: frozenset[str] = frozenset(
    {"INFO", "FATAL", "ERROR", "WARNING", "SEVERE", "FAILURE"}
)

# The 10 space-separated fields in a raw BGL log line. The final field,
# Content, is free text and may itself contain spaces.
COLUMNS: list[str] = [
    "Label",
    "Timestamp",
    "Date",
    "Node",
    "Time",
    "NodeRepeat",
    "Type",
    "Component",
    "Level",
    "Content",
]


def load_bgl(path: str, deduplicate: bool = True) -> pd.DataFrame:
    """Load and clean the BGL log file into a ``(text, label)`` DataFrame.

    The raw file has 10 space-separated fields per line, the last of which
    (Content) is free text containing spaces. It is parsed by reading each
    line as a single column, then splitting at most 9 times so everything
    after the 9th field stays together as Content.

    Cleaning steps:
        1. Drop rows whose Level is not a canonical BGL value (malformed lines).
        2. Drop rows with a null Content (parser artifacts from short lines).

    Args:
        path: Filesystem path to the raw ``BGL.log`` file.
        deduplicate: If True (default), return only unique text rows - the
            "training view" that avoids train/test leakage from the dataset's
            heavy duplication. If False, return all cleaned rows - the
            "production view" reflecting the distribution the model will serve.

    Returns:
        A DataFrame with two columns:
            - ``text`` (str): the log message Content.
            - ``label`` (int): 0 for normal lines, 1 for anomalies.
    """
    # Read each line as a single field, using a separator that never appears
    # in the data so pandas does not split on spaces.
    raw = pd.read_csv(
        path,
        sep="\x07",
        header=None,
        names=["line"],
        engine="python",
        encoding="utf-8",
        on_bad_lines="skip",
    )

    # Split each line into the 10 structured fields.
    df = raw["line"].str.split(n=9, expand=True)
    df.columns = COLUMNS

    # Drop malformed rows (Level outside the canonical set).
    df = df[df["Level"].isin(CANONICAL_LEVELS)].reset_index(drop=True)

    # Binarize the label: 0 = normal ("-"), 1 = anomaly (any alert tag).
    df["label"] = (df["Label"] != "-").astype(int)

    # Project to the two columns we care about and rename.
    data = df[["Content", "label"]].rename(columns={"Content": "text"})

    # Drop parser-artifact nulls.
    data = data.dropna(subset=["text"]).reset_index(drop=True)

    if deduplicate:
        data = data.drop_duplicates(subset=["text"]).reset_index(drop=True)

    return data

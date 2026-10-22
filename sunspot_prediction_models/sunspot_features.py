"""Shared tabular feature engineering for the baseline and CNN notebooks.

Keeping this in ONE place guarantees that the classical baselines and the neural
networks are compared on exactly the same inputs.

Put this file next to the notebooks and use:  from features import build_features, FEATURE_SETS
"""

import numpy as np
import pandas as pd

# Every engineered column that can be used as a tabular input.
ALL_FEATURES = [
    "log_area", "ll", "nn",                  # size descriptors (come from the same SRS record as the label)
    "lat", "abs_lon",                        # position on the disk
    "mag_simple", "mag_mixed", "mag_complex",  # grouped magnetic type (polarity proxy)
]

# Which subsets to test. 'size_only' is what the notebooks used so far.
FEATURE_SETS = {
    # ll (longitudinal extent) practically defines the Zurich class -> label leakage
    "size_only": ["log_area", "ll", "nn"],
    "all": ["log_area", "ll", "nn", "lat", "abs_lon", "mag_simple", "mag_mixed", "mag_complex"],
    # leakage-free: nothing that encodes the extent of the group
    "no_size": ["lat", "abs_lon", "mag_simple", "mag_mixed", "mag_complex"],
    "position_only": ["lat", "abs_lon"],
    "polarity_only": ["mag_simple", "mag_mixed", "mag_complex"],
}


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return a float32 DataFrame with all engineered columns, row-aligned with df."""
    out = pd.DataFrame(index=df.index)
    out["log_area"] = np.log1p(df["area"].astype("float32"))  # area is heavy-tailed and can be 0
    out["ll"] = df["ll"].astype("float32")
    out["nn"] = df["nn"].astype("float32")
    out["lat"] = df["lat"].astype("float32")
    out["abs_lon"] = df["lon"].abs().astype("float32")        # limb vs. disk center
    for cls in ("simple", "mixed", "complex"):
        out[f"mag_{cls}"] = (df["mag_class"] == cls).astype("float32")
    return out[ALL_FEATURES].astype("float32")
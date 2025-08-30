import json
import os
from math import sqrt
from typing import Iterable, Tuple

import numpy as np
import pandas as pd


def ensure_dirs(*paths: str) -> None:
    """Create directories if they do not exist."""
    for p in paths:
        os.makedirs(p, exist_ok=True)


def accel_mag(ax: float, ay: float, az: float) -> float:
    """Return acceleration magnitude."""
    return sqrt(ax ** 2 + ay ** 2 + az ** 2)


def sliding_windows(samples: Iterable, sr_hz: int, win_s: float, step_s: float) -> Iterable[Tuple[int, int]]:
    """Yield start/end indices for sliding windows."""
    samples = list(samples)
    win = int(sr_hz * win_s)
    step = int(sr_hz * step_s)
    for start in range(0, len(samples) - win + 1, step):
        yield start, start + win


def extract_features(window: pd.DataFrame) -> dict:
    """Compute statistical features for accelerometer window."""
    df = window if isinstance(window, pd.DataFrame) else pd.DataFrame(window)
    ax = df['ax'].to_numpy()
    ay = df['ay'].to_numpy()
    az = df['az'].to_numpy()
    mag = np.sqrt(ax ** 2 + ay ** 2 + az ** 2)
    jerk = np.diff(mag, prepend=mag[0])

    feats = {}
    for name, data in {'ax': ax, 'ay': ay, 'az': az, 'mag': mag, 'jerk': jerk}.items():
        feats[f'{name}_mean'] = float(np.mean(data))
        feats[f'{name}_std'] = float(np.std(data))
        feats[f'{name}_min'] = float(np.min(data))
        feats[f'{name}_max'] = float(np.max(data))
        feats[f'{name}_range'] = float(np.max(data) - np.min(data))

    g = 9.80665
    feats['count_peaks'] = int(np.sum(mag > 1.5 * g))
    feats['count_dips'] = int(np.sum(mag < 0.5 * g))
    return feats


def json_to_sample(js: str) -> dict:
    """Convert JSON string to a sample dict."""
    data = json.loads(js)
    return {
        'ts': data.get('ts', 0),
        'ax': data.get('ax', 0.0),
        'ay': data.get('ay', 0.0),
        'az': data.get('az', 0.0),
    }

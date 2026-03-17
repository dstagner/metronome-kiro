from typing import Optional

from metronome.utils import clamp_bpm

_MAX_TAPS = 4
_RESET_GAP_SECONDS = 3.0


class TapTempo:
    """Records tap timestamps and computes BPM from the average interval."""

    def __init__(self) -> None:
        self._timestamps: list[float] = []

    def record_tap(self, timestamp: float) -> Optional[int]:
        """Store tap timestamp and return computed BPM, or None if fewer than 2 taps.

        Auto-resets if the gap since the last tap exceeds 3 seconds.
        Keeps only the last 4 timestamps.
        Returns clamped BPM in [20, 300].
        """
        if self._timestamps and (timestamp - self._timestamps[-1]) > _RESET_GAP_SECONDS:
            self._timestamps = []

        self._timestamps.append(timestamp)

        if len(self._timestamps) > _MAX_TAPS:
            self._timestamps = self._timestamps[-_MAX_TAPS:]

        if len(self._timestamps) < 2:
            return None

        intervals = [
            self._timestamps[i] - self._timestamps[i - 1]
            for i in range(1, len(self._timestamps))
        ]
        mean_interval = sum(intervals) / len(intervals)
        bpm = round(60.0 / mean_interval)
        return clamp_bpm(bpm)

    def reset(self) -> None:
        """Clear all stored timestamps."""
        self._timestamps = []

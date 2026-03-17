"""Property tests for TapTempo.

Validates: Requirements 1.2
"""
from hypothesis import given, assume
import hypothesis.strategies as st

from metronome.utils import BPM_MIN, BPM_MAX
from metronome.tap_tempo import TapTempo


@given(
    st.floats(min_value=0.1, max_value=3.0, allow_nan=False, allow_infinity=False),
    st.integers(min_value=2, max_value=4),
)
def test_bpm_result_always_in_range(interval: float, n_taps: int) -> None:
    """BPM computed from evenly-spaced taps is always clamped to [BPM_MIN, BPM_MAX]."""
    tt = TapTempo()
    result = None
    for i in range(n_taps):
        result = tt.record_tap(float(i) * interval)
    assert result is not None
    assert BPM_MIN <= result <= BPM_MAX


@given(
    st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    st.floats(min_value=3.01, max_value=10.0, allow_nan=False, allow_infinity=False),
)
def test_reset_after_3_second_gap(first_tap: float, gap: float) -> None:
    """A gap > 3 s between taps resets the sequence so the next tap returns None."""
    tt = TapTempo()
    tt.record_tap(first_tap)
    result = tt.record_tap(first_tap + gap)
    assert result is None

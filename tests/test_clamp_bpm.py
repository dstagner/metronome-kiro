"""Property tests for clamp_bpm.

Validates: Requirements 1.1
"""
from hypothesis import given
import hypothesis.strategies as st

from metronome.utils import BPM_MIN, BPM_MAX, clamp_bpm


@given(st.integers())
def test_clamp_bpm_always_in_range(value: int) -> None:
    """clamp_bpm returns a value in [BPM_MIN, BPM_MAX] for any integer input."""
    result = clamp_bpm(value)
    assert BPM_MIN <= result <= BPM_MAX

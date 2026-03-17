BPM_MIN = 20
BPM_MAX = 300


def clamp_bpm(value: int) -> int:
    """Clamp a BPM value to the valid range [BPM_MIN, BPM_MAX]."""
    return max(BPM_MIN, min(BPM_MAX, value))


def is_accent(beat_number: int, beats_per_measure: int) -> bool:
    """Return True if beat_number is the first beat of a measure (zero-indexed)."""
    return beat_number % beats_per_measure == 0

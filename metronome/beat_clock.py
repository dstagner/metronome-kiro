"""BeatClock: drift-corrected beat scheduling in a background thread."""

import sys
import threading
import time
from typing import Callable, Optional

from metronome.utils import is_accent


class BeatClock:
    """Fires an on_beat callback at a tempo-accurate interval.

    The clock runs in a daemon thread and uses time.perf_counter() to
    correct for accumulated drift across beats.
    """

    def __init__(self, on_beat: Callable[[int, bool], None]) -> None:
        self.on_beat = on_beat
        self._bpm: int = 120
        self._beats_per_measure: int = 4
        self._stop_flag: threading.Event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the beat clock in a daemon thread."""
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_flag.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Signal the clock to stop; the thread finishes its current interval."""
        self._stop_flag.set()

    def set_bpm(self, bpm: int) -> None:
        """Update tempo; takes effect on the next beat interval."""
        self._bpm = bpm

    def set_beats_per_measure(self, n: int) -> None:
        """Update beats per measure; takes effect at the next measure boundary."""
        self._pending_beats_per_measure: Optional[int] = n

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _run(self) -> None:
        beat_number: int = 0
        # Initialise pending time-sig storage if not already set.
        if not hasattr(self, "_pending_beats_per_measure"):
            self._pending_beats_per_measure = None

        next_beat_time = time.perf_counter()

        while not self._stop_flag.is_set():
            bpm = self._bpm
            interval = 60.0 / bpm

            # Apply pending time-signature change at measure boundary.
            if beat_number % self._beats_per_measure == 0 and self._pending_beats_per_measure is not None:
                self._beats_per_measure = self._pending_beats_per_measure
                self._pending_beats_per_measure = None
                beat_number = 0  # reset to start of new measure

            accent = is_accent(beat_number, self._beats_per_measure)

            try:
                self.on_beat(beat_number, accent)
            except Exception as exc:  # noqa: BLE001
                print(f"BeatClock: exception in on_beat callback: {exc}", file=sys.stderr)

            beat_number += 1
            next_beat_time += interval

            # Drift-corrected sleep: sleep only the remaining time until the
            # next scheduled beat, clamping to zero if we're already late.
            sleep_duration = next_beat_time - time.perf_counter()
            if sleep_duration > 0:
                time.sleep(sleep_duration)

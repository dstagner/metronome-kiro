# Implementation Plan: Python Metronome

## Overview

Implement a standalone desktop metronome in Python using `tkinter` for the GUI and `pygame.mixer` (with `simpleaudio` fallback) for audio. The build proceeds bottom-up: core utilities first, then the beat engine, then audio, then the GUI layer, finishing with wiring and lifecycle handling.

## Tasks

- [x] 1. Set up project structure and core utilities
  - Create `metronome/` package with `__init__.py` and `__main__.py` entry point
  - Implement `clamp_bpm(value: int) -> int` and `BPM_MIN`/`BPM_MAX` constants in `metronome/utils.py`
  - Implement `is_accent(beat_number: int, beats_per_measure: int) -> bool` in `metronome/utils.py`
  - Define `AppState` dataclass in `metronome/state.py`
  - Set up `tests/` directory with `pytest` and `hypothesis` as dev dependencies (`requirements-dev.txt`)
  - _Requirements: 1.1, 1.4, 5.3_

  - [ ]* 1.1 Write property test for `clamp_bpm` (Property 1)
    - **Property 1: BPM clamping is always in range**
    - **Validates: Requirements 1.1, 1.4, 6.4**
    - File: `tests/test_clamp_bpm.py`

  - [ ]* 1.2 Write property test for `is_accent` (Property 10)
    - **Property 10: Accent placement follows time signature**
    - **Validates: Requirements 5.1, 5.3**
    - File: `tests/test_accent_placement.py`

- [x] 2. Implement `TapTempo`
  - Create `metronome/tap_tempo.py` with `TapTempo` class
  - `record_tap(timestamp: float) -> Optional[int]`: store up to last 4 timestamps, compute average interval, return clamped BPM or `None` if fewer than 2 taps
  - `reset() -> None`: clear stored timestamps
  - Auto-reset when gap since last tap exceeds 3 seconds
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [ ]* 2.1 Write property test for tap BPM calculation (Property 11)
    - **Property 11: Tap tempo BPM calculation**
    - **Validates: Requirements 6.2, 6.4**
    - File: `tests/test_tap_tempo.py`

  - [ ]* 2.2 Write property test for tap sequence reset (Property 12)
    - **Property 12: Tap sequence resets after 3-second gap**
    - **Validates: Requirements 6.3**
    - File: `tests/test_tap_tempo.py`

- [x] 3. Checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement `AudioPlayer`
  - Create `metronome/audio.py`
  - Synthesize regular tick (~1000 Hz, ~20ms) and accent tick (~1500 Hz, ~20ms) as numpy arrays at init; load into `pygame.mixer` buffers
  - `play_tick(accent: bool) -> None`: play the appropriate buffer
  - `close() -> None`: release mixer resources
  - Implement `SilentAudioPlayer` no-op subclass
  - Catch `pygame.mixer.init()` failure in `AudioPlayer.__init__` and raise so caller can substitute `SilentAudioPlayer`
  - _Requirements: 3.1, 3.2, 3.3, 7.2, 7.3_

  - [ ]* 4.1 Write property test for accent audio parameters (Property 6)
    - **Property 6: Accent sound parameters differ from regular tick**
    - **Validates: Requirements 3.3**
    - File: `tests/test_audio_params.py`

  - [ ]* 4.2 Write unit test for `SilentAudioPlayer` fallback
    - Verify `AudioPlayer` construction falls back to `SilentAudioPlayer` when `pygame.mixer.init()` raises
    - File: `tests/test_unit_lifecycle.py`

- [x] 5. Implement `BeatClock`
  - Create `metronome/beat_clock.py` with `BeatClock` class
  - Run in a daemon `threading.Thread`; use `time.perf_counter()` for drift-corrected sleep
  - `start() -> None`, `stop() -> None` (sets flag; thread finishes current interval before exiting)
  - `set_bpm(bpm: int) -> None`: takes effect on next beat interval
  - `set_beats_per_measure(n: int) -> None`: takes effect at next measure boundary
  - Fire `on_beat(beat_number: int, is_accent: bool)` callback on each beat
  - Catch exceptions in the beat callback; log to stderr; continue
  - _Requirements: 1.2, 2.5, 5.4_

  - [ ]* 5.1 Write property test for beat interval (Property 2)
    - **Property 2: Beat interval matches BPM**
    - **Validates: Requirements 1.2**
    - File: `tests/test_beat_interval.py`

  - [ ]* 5.2 Write property test for beat timing accuracy (Property 5)
    - **Property 5: Beat timing accuracy**
    - **Validates: Requirements 3.1**
    - File: `tests/test_beat_timing.py`

  - [ ]* 5.3 Write unit test for `stop()` completing current interval
    - Verify `BeatClock.stop()` does not exit mid-interval
    - File: `tests/test_unit_lifecycle.py`

  - [ ]* 5.4 Write unit test for time signature change mid-measure
    - Verify new beats-per-measure applies at next measure boundary
    - File: `tests/test_unit_lifecycle.py`

- [x] 6. Checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement `MetronomeApp` GUI
  - Create `metronome/app.py` with `MetronomeApp(tk.Tk)` class
  - Add BPM slider (20–300) + numeric label (`BPM_Control`)
  - Add Start and Stop buttons (`Transport_Controls`); wire enabled/disabled states to running flag
  - Add Tap button; call `TapTempo.record_tap()` and update BPM slider on result
  - Add time signature spinbox (1–8)
  - Add visual indicator canvas; flash on beat via `tkinter.after()`; use distinct color for accent vs regular beat; reset to default after 100ms
  - Use `tkinter.after()` to dispatch beat callbacks from `BeatClock` thread to GUI thread
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 4.1, 4.2, 4.3, 5.2, 6.1_

  - [ ]* 7.1 Write property test for BPM label (Property 3)
    - **Property 3: BPM label always reflects current value**
    - **Validates: Requirements 1.3**
    - File: `tests/test_bpm_label.py`

  - [ ]* 7.2 Write property test for transport button states (Property 4)
    - **Property 4: Transport button states are consistent with running state**
    - **Validates: Requirements 2.3, 2.4**
    - File: `tests/test_transport_state.py`

  - [ ]* 7.3 Write property test for visual indicator flash duration (Property 7)
    - **Property 7: Visual indicator flash duration is within bounds**
    - **Validates: Requirements 4.1**
    - File: `tests/test_audio_params.py`

  - [ ]* 7.4 Write property test for visual indicator accent appearance (Property 8)
    - **Property 8: Visual indicator accent appearance differs from regular beat**
    - **Validates: Requirements 4.2**
    - File: `tests/test_audio_params.py`

  - [ ]* 7.5 Write property test for visual indicator inactive state (Property 9)
    - **Property 9: Visual indicator is inactive when metronome is stopped**
    - **Validates: Requirements 4.3**
    - File: `tests/test_indicator_state.py`

  - [ ]* 7.6 Write unit test for widget existence after init
    - Verify Start, Stop, Tap buttons and time-sig spinbox exist after `MetronomeApp.__init__`
    - File: `tests/test_unit_lifecycle.py`

- [x] 8. Implement application lifecycle and wiring
  - Implement `on_closing()` in `MetronomeApp`: call `clock.stop()`, `audio.close()`, then `destroy()`
  - Wire `BeatClock.on_beat` to call `audio.play_tick()` and schedule GUI flash via `root.after()`
  - Initialize `AudioPlayer`; catch failure and substitute `SilentAudioPlayer`; display error label in GUI if silent mode
  - Add `__main__.py` entry point: instantiate `MetronomeApp`, call `mainloop()`
  - _Requirements: 7.1, 7.2, 7.3_

  - [ ]* 8.1 Write unit test for `on_closing()` cleanup
    - Mock `BeatClock` and `AudioPlayer`; verify both `stop()` and `close()` are called on window close
    - File: `tests/test_unit_lifecycle.py`

  - [ ]* 8.2 Write unit test for silent mode on audio failure
    - Verify error label appears in GUI when audio init fails
    - File: `tests/test_unit_lifecycle.py`

- [x] 9. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Property tests use `hypothesis`; run with `pytest tests/`
- `BeatClock` communicates back to the GUI exclusively via `tkinter.after()` to keep widget access on the main thread

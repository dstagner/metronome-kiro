"""MetronomeApp: main GUI window for the Python Metronome."""

import time
import tkinter as tk
from tkinter import ttk

from metronome.audio import AudioPlayer, SilentAudioPlayer
from metronome.beat_clock import BeatClock
from metronome.state import AppState
from metronome.tap_tempo import TapTempo
from metronome.utils import BPM_MAX, BPM_MIN, clamp_bpm

# Visual indicator colours
_COLOUR_DEFAULT = "#cccccc"
_COLOUR_ACCENT = "#ff8c00"   # orange
_COLOUR_REGULAR = "#00aa44"  # green
_FLASH_DURATION_MS = 100


class MetronomeApp(tk.Tk):
    """Top-level tkinter window for the metronome application."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Metronome")
        self.resizable(False, False)

        self._state = AppState()
        self._tap_tempo = TapTempo()

        # Audio — fall back to silent mode if device is unavailable
        self._silent_mode = False
        try:
            self._audio = AudioPlayer()
        except Exception:
            self._audio = SilentAudioPlayer()
            self._silent_mode = True

        # Beat clock
        self._clock = BeatClock(self.on_beat)

        # Tkinter variable for BPM (drives slider and label in sync)
        self._bpm_var = tk.IntVar(value=self._state.bpm)
        self._bpm_var.trace_add("write", self._on_bpm_var_changed)

        self._build_ui()
        self._update_transport_buttons()

        if self._silent_mode:
            error_label = ttk.Label(
                self,
                text="⚠ Audio device unavailable — running in silent mode",
                foreground="red",
            )
            error_label.pack(pady=(0, 6))

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": 6}

        # ---- BPM control row ----------------------------------------
        bpm_frame = ttk.LabelFrame(self, text="Tempo (BPM)")
        bpm_frame.pack(fill="x", **pad)

        self._bpm_slider = ttk.Scale(
            bpm_frame,
            from_=BPM_MIN,
            to=BPM_MAX,
            orient="horizontal",
            variable=self._bpm_var,
            command=self._on_slider_moved,
        )
        self._bpm_slider.pack(side="left", fill="x", expand=True, padx=(8, 4), pady=6)

        self._bpm_label = ttk.Label(bpm_frame, text=str(self._state.bpm), width=5, anchor="center")
        self._bpm_label.pack(side="left", padx=(4, 8), pady=6)

        # ---- Time signature row -------------------------------------
        ts_frame = ttk.LabelFrame(self, text="Beats per Measure")
        ts_frame.pack(fill="x", **pad)

        self._beats_var = tk.IntVar(value=self._state.beats_per_measure)
        self._ts_spinbox = ttk.Spinbox(
            ts_frame,
            from_=1,
            to=8,
            textvariable=self._beats_var,
            width=4,
            command=self._on_beats_changed,
        )
        self._ts_spinbox.pack(padx=8, pady=6)
        self._beats_var.trace_add("write", self._on_beats_var_changed)

        # ---- Transport controls row ---------------------------------
        transport_frame = ttk.Frame(self)
        transport_frame.pack(fill="x", **pad)

        self._start_btn = ttk.Button(transport_frame, text="Start", command=self._on_start)
        self._start_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))

        self._stop_btn = ttk.Button(transport_frame, text="Stop", command=self._on_stop)
        self._stop_btn.pack(side="left", expand=True, fill="x", padx=(4, 4))

        self._tap_btn = ttk.Button(transport_frame, text="Tap", command=self._on_tap)
        self._tap_btn.pack(side="left", expand=True, fill="x", padx=(4, 0))

        # ---- Visual indicator ---------------------------------------
        indicator_frame = ttk.LabelFrame(self, text="Beat")
        indicator_frame.pack(fill="both", expand=True, **pad)

        self._indicator = tk.Canvas(
            indicator_frame,
            width=200,
            height=80,
            bg=_COLOUR_DEFAULT,
            highlightthickness=0,
        )
        self._indicator.pack(padx=8, pady=8)

    # ------------------------------------------------------------------
    # BPM helpers
    # ------------------------------------------------------------------

    def _on_slider_moved(self, value: str) -> None:
        """Called by the Scale widget; value is a float string."""
        bpm = clamp_bpm(round(float(value)))
        # Update var without triggering recursive trace
        if self._bpm_var.get() != bpm:
            self._bpm_var.set(bpm)
        self._bpm_label.config(text=str(bpm))
        self._state.bpm = bpm
        self._clock.set_bpm(bpm)

    def _on_bpm_var_changed(self, *_args) -> None:
        """Trace callback: keep label in sync whenever _bpm_var changes."""
        try:
            bpm = clamp_bpm(self._bpm_var.get())
        except tk.TclError:
            return
        self._bpm_label.config(text=str(bpm))
        self._state.bpm = bpm

    def set_bpm(self, bpm: int) -> None:
        """Programmatically set BPM (e.g. from tap tempo result)."""
        bpm = clamp_bpm(bpm)
        self._bpm_var.set(bpm)
        self._bpm_label.config(text=str(bpm))
        self._state.bpm = bpm
        self._clock.set_bpm(bpm)

    # ------------------------------------------------------------------
    # Time signature helpers
    # ------------------------------------------------------------------

    def _on_beats_changed(self) -> None:
        self._apply_beats_var()

    def _on_beats_var_changed(self, *_args) -> None:
        self._apply_beats_var()

    def _apply_beats_var(self) -> None:
        try:
            n = int(self._beats_var.get())
        except (tk.TclError, ValueError):
            return
        n = max(1, min(8, n))
        self._state.beats_per_measure = n
        self._clock.set_beats_per_measure(n)

    # ------------------------------------------------------------------
    # Transport callbacks (no-op placeholders; wired in task 8)
    # ------------------------------------------------------------------

    def _on_start(self) -> None:
        """Start the metronome."""
        self._state.running = True
        self._update_transport_buttons()
        self._clock.start()

    def _on_stop(self) -> None:
        """Stop the metronome."""
        self._state.running = False
        self._update_transport_buttons()
        self._reset_indicator()
        self._clock.stop()

    def _on_tap(self) -> None:
        """Record a tap and update BPM if a result is available."""
        result = self._tap_tempo.record_tap(time.monotonic())
        if result is not None:
            self.set_bpm(result)

    def _update_transport_buttons(self) -> None:
        """Sync Start/Stop button states with the running flag."""
        if self._state.running:
            self._start_btn.config(state="disabled")
            self._stop_btn.config(state="normal")
        else:
            self._start_btn.config(state="normal")
            self._stop_btn.config(state="disabled")

    # ------------------------------------------------------------------
    # Visual indicator
    # ------------------------------------------------------------------

    def flash_beat(self, accent: bool) -> None:
        """Flash the visual indicator; safe to call from any thread via after()."""
        colour = _COLOUR_ACCENT if accent else _COLOUR_REGULAR
        self._indicator.config(bg=colour)
        self.after(_FLASH_DURATION_MS, self._reset_indicator)

    def _reset_indicator(self) -> None:
        self._indicator.config(bg=_COLOUR_DEFAULT)

    def on_beat(self, beat_number: int, is_accent: bool) -> None:
        """Beat callback from BeatClock; dispatches to GUI thread via after()."""
        self._audio.play_tick(is_accent)
        self.after(0, self.flash_beat, is_accent)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_closing(self) -> None:
        """WM_DELETE_WINDOW handler — stop engine and release resources."""
        self._state.running = False
        self._clock.stop()
        self._audio.close()
        self.destroy()

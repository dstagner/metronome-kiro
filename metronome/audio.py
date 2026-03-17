"""Audio subsystem for the metronome.

Synthesizes tick sounds using numpy and plays them via pygame.mixer.
Falls back to SilentAudioPlayer when audio is unavailable.
"""

import numpy as np
import pygame


_SAMPLE_RATE = 44100
_TICK_DURATION = 0.020  # 20ms


def _synthesize_tick(frequency: float, duration: float = _TICK_DURATION) -> np.ndarray:
    """Synthesize a short sine-wave click at the given frequency."""
    num_samples = int(_SAMPLE_RATE * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    wave = np.sin(2 * np.pi * frequency * t)

    # Apply a simple linear fade-out envelope to avoid clicks
    envelope = np.linspace(1.0, 0.0, num_samples)
    wave = (wave * envelope * 32767).astype(np.int16)

    # pygame expects stereo (2-channel) data
    return np.column_stack((wave, wave))


class AudioPlayer:
    """Plays tick sounds using pygame.mixer.

    Raises pygame.error (or any exception from pygame.mixer.init) if the
    audio device is unavailable, so the caller can substitute SilentAudioPlayer.
    """

    def __init__(self) -> None:
        pygame.mixer.init(frequency=_SAMPLE_RATE, size=-16, channels=2, buffer=512)

        regular_array = _synthesize_tick(1000.0)
        accent_array = _synthesize_tick(1500.0)

        self._regular_sound = pygame.sndarray.make_sound(regular_array)
        self._accent_sound = pygame.sndarray.make_sound(accent_array)

    def play_tick(self, accent: bool = False) -> None:
        """Play the regular or accent tick sound."""
        if accent:
            self._accent_sound.play()
        else:
            self._regular_sound.play()

    def close(self) -> None:
        """Release mixer resources."""
        pygame.mixer.quit()


class SilentAudioPlayer(AudioPlayer):
    """No-op fallback used when the audio device is unavailable."""

    def __init__(self) -> None:
        # Skip pygame initialisation entirely
        pass

    def play_tick(self, accent: bool = False) -> None:
        pass

    def close(self) -> None:
        pass

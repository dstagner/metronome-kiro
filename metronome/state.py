from dataclasses import dataclass, field


@dataclass
class AppState:
    bpm: int = 120                       # 20–300 inclusive
    beats_per_measure: int = 4           # 1–8 inclusive
    running: bool = False
    tap_timestamps: list[float] = field(default_factory=list)

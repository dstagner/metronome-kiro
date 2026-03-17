# Requirements Document

## Introduction

A browser-based metronome application built in TypeScript, bundled with Vite, and run entirely in the browser without a server. The app allows musicians and practitioners to set a tempo (BPM), start and stop the beat, and receive both visual and audible feedback on each beat. Audio is synthesized via the Web Audio API; timing uses a lookahead scheduler driven by `AudioContext.currentTime` rather than `setInterval`, ensuring accurate, drift-free beat generation.

## Glossary

- **Metronome**: The application responsible for producing rhythmic beat signals at a user-defined tempo.
- **BPM**: Beats Per Minute — the unit of tempo, representing how many beats occur in one minute.
- **Beat**: A single rhythmic pulse produced by the Metronome at the interval defined by the current BPM.
- **Tick**: The audible click sound emitted on each Beat, synthesized as a short sine-wave burst.
- **Visual_Indicator**: The DOM element that flashes or changes appearance on each Beat to provide visual feedback.
- **Transport_Controls**: The UI buttons that start and stop the Metronome, plus the Tap button.
- **BPM_Control**: The UI element (slider or number input) used to set the tempo.
- **Accent**: A Beat that is louder or visually distinct, marking the first beat of a measure.
- **Time_Signature**: The number of beats per measure, determining how often an Accent occurs.
- **AudioContext**: The Web Audio API object that owns the audio clock and graph.
- **BeatScheduler**: The lookahead scheduling component that drives beat generation using `AudioContext.currentTime`.
- **AudioEngine**: The component that synthesizes Tick sounds via `OscillatorNode` and `GainNode`.
- **SilentAudioEngine**: A no-op fallback AudioEngine used when the Web Audio API is unavailable.

## Requirements

### Requirement 1: Tempo Control

**User Story:** As a musician, I want to set the tempo in BPM, so that I can practice at the correct speed.

#### Acceptance Criteria

1. THE BPM_Control SHALL accept integer BPM values in the range 20 to 300 inclusive.
2. WHEN the user adjusts the BPM_Control, THE BeatScheduler SHALL update the beat interval without requiring a restart.
3. THE BPM_Control SHALL display the current BPM value as a numeric label at all times.
4. IF the user enters a BPM value outside the range 20–300, THEN THE BPM_Control SHALL clamp the value to the nearest valid boundary and display the clamped value.

---

### Requirement 2: Start and Stop

**User Story:** As a musician, I want to start and stop the metronome with a single control, so that I can easily control playback during practice.

#### Acceptance Criteria

1. THE Transport_Controls SHALL provide a Start button that begins beat generation when the Metronome is stopped.
2. THE Transport_Controls SHALL provide a Stop button that halts beat generation when the Metronome is running.
3. WHEN the Metronome is started, THE Transport_Controls SHALL disable the Start button and enable the Stop button.
4. WHEN the Metronome is stopped, THE Transport_Controls SHALL enable the Start button and disable the Stop button.
5. WHEN the Metronome is stopped, THE BeatScheduler SHALL allow already-scheduled audio notes to complete before the AudioContext is released, ensuring no abrupt audio cutoff.

---

### Requirement 3: Audible Beat

**User Story:** As a musician, I want to hear a click on every beat, so that I can follow the tempo by ear.

#### Acceptance Criteria

1. WHEN a Beat occurs, THE AudioEngine SHALL play a Tick sound within 10ms of the scheduled beat time as measured by `AudioContext.currentTime`.
2. THE AudioEngine SHALL synthesize the Tick sound using the Web Audio API (`OscillatorNode` and `GainNode`), requiring no external audio files or system audio tools.
3. WHEN an Accent Beat occurs, THE AudioEngine SHALL play a Tick sound that is audibly distinct from a regular Tick (higher frequency: 1500 Hz accent vs 1000 Hz regular).

---

### Requirement 4: Visual Beat Indicator

**User Story:** As a musician, I want to see a visual flash on every beat, so that I can follow the tempo visually.

#### Acceptance Criteria

1. WHEN a Beat occurs, THE Visual_Indicator SHALL change its appearance (color or CSS class) for a minimum of 50ms and a maximum of 200ms.
2. WHEN an Accent Beat occurs, THE Visual_Indicator SHALL display a visually distinct appearance compared to a regular Beat.
3. WHILE the Metronome is stopped, THE Visual_Indicator SHALL remain in its default (inactive) state.

---

### Requirement 5: Time Signature

**User Story:** As a musician, I want to set a time signature, so that I can practice with accented downbeats.

#### Acceptance Criteria

1. THE Metronome SHALL support time signature numerators (beats per measure) of 1, 2, 3, 4, 5, 6, 7, and 8.
2. THE Metronome SHALL provide a UI control to select the beats-per-measure value.
3. WHEN the beats-per-measure value is set to N, THE BeatScheduler SHALL accent the first beat of every N-beat group.
4. WHEN the beats-per-measure value is changed while the Metronome is running, THE BeatScheduler SHALL apply the new Time_Signature starting from the next measure boundary.

---

### Requirement 6: Tap Tempo

**User Story:** As a musician, I want to tap a button to set the tempo, so that I can match the BPM of a song by ear.

#### Acceptance Criteria

1. THE Transport_Controls SHALL provide a Tap button that records the timestamp of each tap.
2. WHEN the Tap button is pressed two or more times, THE Metronome SHALL calculate the BPM as the average interval between the last four taps and update the BPM_Control accordingly.
3. WHEN no tap is received within 3 seconds of the last tap, THE Metronome SHALL reset the tap sequence so the next tap begins a new sequence.
4. WHEN the BPM calculated from taps falls outside the range 20–300, THE Metronome SHALL clamp the value to the nearest valid boundary.

---

### Requirement 7: Application Lifecycle

**User Story:** As a user, I want the application to load and unload cleanly in the browser, so that it does not leave active audio resources or background timers running.

#### Acceptance Criteria

1. THE Metronome SHALL render the complete UI and be ready for interaction within 3 seconds of the page loading on a standard device with a modern browser.
2. WHEN the user navigates away from or closes the page, THE Metronome SHALL stop beat generation and close the AudioContext before the page unloads.
3. IF the Web Audio API is unavailable or the AudioContext cannot be created, THEN THE Metronome SHALL display an error banner in the UI and operate in silent mode (visual feedback only, using SilentAudioEngine).
4. WHEN the user first interacts with the page (clicks Start or Tap), THE AudioEngine SHALL resume the AudioContext to satisfy the browser autoplay policy before producing audio.

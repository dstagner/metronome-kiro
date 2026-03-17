# Implementation Plan: JS Metronome

## Overview

Bottom-up build: project scaffold → core utilities → tap tempo → audio engine → scheduler → UI → wiring → HTML/CSS. Each step is independently testable before the next layer is added.

## Tasks

- [x] 1. Scaffold project (Vite + TypeScript + Vitest)
  - Create `js-metronome/` directory with `package.json` declaring `vite`, `typescript`, `vitest`, and `fast-check` as dev dependencies
  - Add `vite.config.ts` pointing root at `js-metronome/` and test config for Vitest
  - Add `tsconfig.json` with `strict: true`, `target: "ES2020"`, `lib: ["ES2020", "DOM"]`
  - Create empty `src/` and `tests/` directories with placeholder `.gitkeep` files
  - _Requirements: 7.1_

- [x] 2. Implement core utilities (`src/state.ts`)
  - [x] 2.1 Define `AppState` interface, constants (`BPM_MIN`, `BPM_MAX`, `LOOKAHEAD_S`, `SCHEDULE_INTERVAL_MS`, `FLASH_DURATION_MS`), and export `clampBpm`, `beatInterval`, `isAccent`
    - _Requirements: 1.1, 1.4, 5.1, 5.3_

  - [ ]* 2.2 Write property test for `clampBpm` (Property 1)
    - **Property 1: BPM clamping is always in range**
    - **Validates: Requirements 1.1, 1.4, 6.4**
    - File: `tests/test-clamp-bpm.test.ts`
    - Use `fc.integer({ min: -1000, max: 1000 })` and `fc.float()` strategies

  - [ ]* 2.3 Write property test for `beatInterval` (Property 2)
    - **Property 2: Beat interval matches BPM**
    - **Validates: Requirement 1.2**
    - File: `tests/test-beat-interval.test.ts`
    - Use `fc.integer({ min: 20, max: 300 })` strategy

  - [ ]* 2.4 Write property test for `isAccent` (Property 10)
    - **Property 10: Accent placement follows time signature**
    - **Validates: Requirements 5.1, 5.3**
    - File: `tests/test-accent-placement.test.ts`
    - Use `fc.integer({ min: 1, max: 8 })` and `fc.nat()` strategies

- [x] 3. Implement TapTempo module (`src/tapTempo.ts`)
  - [x] 3.1 Implement `recordTap(timestamp)` and `reset()` with auto-reset on 3-second gap and max-4-tap window
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [ ]* 3.2 Write property test for tap BPM calculation (Property 11)
    - **Property 11: Tap tempo BPM calculation**
    - **Validates: Requirements 6.2, 6.4**
    - File: `tests/test-tap-tempo.test.ts`
    - Use `fc.array(fc.float({ min: 0.1, max: 2.0 }), { minLength: 2, maxLength: 4 })` strategy

  - [ ]* 3.3 Write property test for tap sequence reset (Property 12)
    - **Property 12: Tap sequence resets after 3-second gap**
    - **Validates: Requirement 6.3**
    - File: `tests/test-tap-tempo.test.ts` (same file, additional test)
    - Use `fc.float({ min: 3.001, max: 10.0 })` strategy for gap

- [x] 4. Checkpoint — ensure all tests pass
  - Run `vitest --run` and confirm all tests pass before proceeding.
  - Ask the user if any questions arise.

- [x] 5. Implement AudioEngine (`src/audioEngine.ts`)
  - [x] 5.1 Implement `IAudioEngine` interface, `AudioEngine` class (OscillatorNode + GainNode synthesis, 1000 Hz regular / 1500 Hz accent, 20ms fade envelope), and `SilentAudioEngine` no-op fallback
    - _Requirements: 3.1, 3.2, 3.3, 7.3, 7.4_

  - [ ]* 5.2 Write property test for accent frequency (Property 6)
    - **Property 6: Accent sound frequency differs from regular tick**
    - **Validates: Requirement 3.3**
    - File: `tests/test-audio-params.test.ts`
    - Use `fc.boolean()` strategy; assert accent frequency (1500) !== regular frequency (1000)

  - [ ]* 5.3 Write unit test for AudioEngine fallback
    - Verify that when `AudioContext` is unavailable, `SilentAudioEngine` is substituted and `showAudioError()` is called
    - File: `tests/test-unit-lifecycle.test.ts`
    - _Requirements: 7.3_

- [x] 6. Implement BeatScheduler (`src/scheduler.ts`)
  - [x] 6.1 Implement `BeatScheduler` class with `start()`, `stop()`, `setBpm()`, `setBeatsPerMeasure()`, and `_tick()` lookahead loop; apply pending time-signature changes at measure boundaries
    - _Requirements: 1.2, 2.1, 2.2, 2.3, 2.4, 2.5, 5.3, 5.4_

  - [ ]* 6.2 Write property test for beat timing accuracy (Property 5)
    - **Property 5: Beat timing accuracy**
    - **Validates: Requirement 3.1**
    - File: `tests/test-beat-timing.test.ts`
    - Use `fc.integer({ min: 20, max: 300 })` strategy; assert scheduled time is within `LOOKAHEAD_S` of `currentTime`

  - [ ]* 6.3 Write unit tests for scheduler lifecycle
    - Test `stop()` sets `_running = false` and clears timer
    - Test `_tick()` does not schedule beats when `running === false`
    - Test time-signature change mid-measure applies at next measure boundary
    - File: `tests/test-unit-lifecycle.test.ts`
    - _Requirements: 2.5, 5.4_

- [x] 7. Checkpoint — ensure all tests pass
  - Run `vitest --run` and confirm all tests pass before proceeding.
  - Ask the user if any questions arise.

- [x] 8. Implement UI module (`src/ui.ts`)
  - [x] 8.1 Implement `flashIndicator(accent)` (CSS class toggle, auto-reset after `FLASH_DURATION_MS`), `setTransportState(running)` (enable/disable Start/Stop buttons), `updateBpmDisplay(bpm)`, `showAudioError()` banner, and `init()` wiring for BPM slider and time-signature selector
    - _Requirements: 1.3, 2.3, 2.4, 4.1, 4.2, 4.3, 7.3_

  - [ ]* 8.2 Write property test for transport button states (Property 4)
    - **Property 4: Transport button states are consistent with running state**
    - **Validates: Requirements 2.3, 2.4**
    - File: `tests/test-transport-state.test.ts`
    - Use `fc.boolean()` strategy; assert Start enabled iff `running === false`

  - [ ]* 8.3 Write property test for BPM display (Property 3)
    - **Property 3: BPM display always reflects current value**
    - **Validates: Requirement 1.3**
    - File: `tests/test-bpm-display.test.ts`
    - Use `fc.integer({ min: 20, max: 300 })` strategy

  - [ ]* 8.4 Write property tests for visual indicator (Properties 7, 8, 9)
    - **Property 7: Visual indicator flash duration is within bounds** — assert `FLASH_DURATION_MS` in [50, 200]
    - **Property 8: Visual indicator accent appearance differs from regular beat** — `fc.boolean()` strategy
    - **Property 9: Visual indicator is inactive when metronome is stopped** — invariant check
    - **Validates: Requirements 4.1, 4.2, 4.3**
    - File: `tests/test-audio-params.test.ts` and `tests/test-indicator-state.test.ts`

  - [ ]* 8.5 Write unit test for DOM structure
    - Verify start, stop, tap buttons, BPM slider, time-sig selector, and indicator element exist after `init()`
    - File: `tests/test-unit-lifecycle.test.ts`
    - _Requirements: 7.1_

- [x] 9. Implement main entry point (`src/main.ts`)
  - Wire `AudioEngine` (with `SilentAudioEngine` fallback), `BeatScheduler`, `TapTempo`, and UI module together on `DOMContentLoaded`
  - Attach `beforeunload` handler calling `scheduler.stop()` and `audioEngine.close()`
  - _Requirements: 2.1, 2.2, 6.1, 7.2, 7.4_

  - [ ]* 9.1 Write unit test for `beforeunload` lifecycle
    - Verify `scheduler.stop()` and `audioEngine.close()` are called on `beforeunload`
    - File: `tests/test-unit-lifecycle.test.ts`
    - _Requirements: 7.2_

- [x] 10. Add `index.html` and `style.css`
  - `index.html`: include BPM slider (`#slider-bpm`), BPM label (`#bpm-display`), Start (`#btn-start`), Stop (`#btn-stop`), Tap (`#btn-tap`) buttons, time-signature selector (`#select-beats`), and visual indicator (`#indicator`); link `style.css` and `src/main.ts`
  - `style.css`: layout, default/accent/regular indicator states, error banner style
  - _Requirements: 1.3, 2.1, 2.2, 4.1, 4.2, 5.2, 6.1, 7.3_

- [x] 11. Final checkpoint — ensure all tests pass and app runs
  - Run `vitest --run` and confirm all tests pass.
  - Verify `vite dev` starts without errors (run manually: `cd js-metronome && npm run dev`).
  - Ask the user if any questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Property tests use **fast-check** with Vitest; run with `vitest --run` from `js-metronome/`
- `SilentAudioEngine` ensures the app is always testable without a real `AudioContext`

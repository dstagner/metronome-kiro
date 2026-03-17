import { AppState, clampBpm } from './state';
import { AudioEngine, SilentAudioEngine, IAudioEngine } from './audioEngine';
import { BeatScheduler } from './scheduler';
import { recordTap } from './tapTempo';
import {
  updateBpmDisplay,
  setTransportState,
  flashIndicator,
  showAudioError,
  resetIndicator,
} from './ui';

document.addEventListener('DOMContentLoaded', () => {
  const state: AppState = {
    bpm: 120,
    beatsPerMeasure: 4,
    running: false,
    tapTimestamps: [],
  };

  let audioEngine: IAudioEngine;
  try {
    audioEngine = new AudioEngine();
  } catch (_e) {
    audioEngine = new SilentAudioEngine();
    showAudioError();
  }

  const scheduler = new BeatScheduler(
    audioEngine,
    (_beatNumber: number, accent: boolean, scheduledTime: number) => {
      const delayMs = (scheduledTime - audioEngine.currentTime()) * 1000;
      setTimeout(() => flashIndicator(accent), delayMs);
    }
  );

  // Start
  document.getElementById('btn-start')?.addEventListener('click', () => {
    scheduler.setBpm(state.bpm);
    scheduler.setBeatsPerMeasure(state.beatsPerMeasure);
    scheduler.start();
    state.running = true;
    setTransportState(true);
  });

  // Stop
  document.getElementById('btn-stop')?.addEventListener('click', () => {
    scheduler.stop();
    state.running = false;
    setTransportState(false);
    resetIndicator();
  });

  // BPM slider
  document.getElementById('slider-bpm')?.addEventListener('input', (e: Event) => {
    state.bpm = clampBpm(Number((e.target as HTMLInputElement).value));
    updateBpmDisplay(state.bpm);
    scheduler.setBpm(state.bpm);
  });

  // Beats per measure selector
  document.getElementById('select-beats')?.addEventListener('change', (e: Event) => {
    state.beatsPerMeasure = Number((e.target as HTMLSelectElement).value);
    scheduler.setBeatsPerMeasure(state.beatsPerMeasure);
  });

  // Tap tempo
  document.getElementById('btn-tap')?.addEventListener('click', () => {
    const bpm = recordTap(performance.now() / 1000);
    if (bpm !== null) {
      state.bpm = bpm;
      updateBpmDisplay(bpm);
      scheduler.setBpm(bpm);
    }
  });

  // Cleanup on page unload
  window.addEventListener('beforeunload', () => {
    scheduler.stop();
    audioEngine.close();
  });

  // Initial UI state
  setTransportState(false);
  updateBpmDisplay(state.bpm);
});

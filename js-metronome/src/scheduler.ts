import { IAudioEngine } from './audioEngine';
import { LOOKAHEAD_S, SCHEDULE_INTERVAL_MS, isAccent } from './state';

export type OnBeatCallback = (beatNumber: number, accent: boolean, scheduledTime: number) => void;

export class BeatScheduler {
  private _audioEngine: IAudioEngine;
  private _onBeat: OnBeatCallback;
  private _running: boolean = false;
  private _beatNumber: number = 0;
  private _nextBeatTime: number = 0;
  private _bpm: number = 120;
  private _beatsPerMeasure: number = 4;
  private _pendingBeatsPerMeasure: number | null = null;
  private _timerId: ReturnType<typeof setTimeout> | null = null;

  constructor(audioEngine: IAudioEngine, onBeat: OnBeatCallback) {
    this._audioEngine = audioEngine;
    this._onBeat = onBeat;
    this._tick = this._tick.bind(this);
  }

  start(): void {
    if (this._running) return;
    this._running = true;
    this._beatNumber = 0;
    this._nextBeatTime = this._audioEngine.currentTime();
    this._audioEngine.resume();
    this._tick();
  }

  stop(): void {
    this._running = false;
    if (this._timerId !== null) {
      clearTimeout(this._timerId);
      this._timerId = null;
    }
  }

  setBpm(bpm: number): void {
    this._bpm = bpm;
  }

  setBeatsPerMeasure(n: number): void {
    this._pendingBeatsPerMeasure = n;
  }

  private _tick(): void {
    if (!this._running) return;

    const currentTime = this._audioEngine.currentTime();

    while (this._nextBeatTime < currentTime + LOOKAHEAD_S) {
      const accent = isAccent(this._beatNumber, this._beatsPerMeasure);

      this._audioEngine.scheduleNote(this._nextBeatTime, accent);

      try {
        this._onBeat(this._beatNumber, accent, this._nextBeatTime);
      } catch (e) {
        console.error('onBeat callback threw an error:', e);
      }

      this._beatNumber += 1;

      // Apply pending time signature change at measure boundary
      if (this._beatNumber % this._beatsPerMeasure === 0 && this._pendingBeatsPerMeasure !== null) {
        this._beatsPerMeasure = this._pendingBeatsPerMeasure;
        this._pendingBeatsPerMeasure = null;
        this._beatNumber = 0;
      }

      this._nextBeatTime += 60.0 / this._bpm;
    }

    this._timerId = setTimeout(this._tick, SCHEDULE_INTERVAL_MS);
  }
}

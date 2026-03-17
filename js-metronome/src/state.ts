export interface AppState {
  bpm: number;
  beatsPerMeasure: number;
  running: boolean;
  tapTimestamps: number[];
}

export const BPM_MIN = 20;
export const BPM_MAX = 300;
export const LOOKAHEAD_S = 0.100;
export const SCHEDULE_INTERVAL_MS = 25;
export const FLASH_DURATION_MS = 100;

export function clampBpm(value: number): number {
  return Math.max(BPM_MIN, Math.min(BPM_MAX, Math.round(value)));
}

export function beatInterval(bpm: number): number {
  return 60.0 / bpm;
}

export function isAccent(beatNumber: number, beatsPerMeasure: number): boolean {
  return beatNumber % beatsPerMeasure === 0;
}

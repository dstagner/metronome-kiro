import { clampBpm } from './state';

const MAX_TAPS = 4;
const RESET_GAP_S = 3.0;

let _timestamps: number[] = [];

export function recordTap(timestamp: number): number | null {
  if (_timestamps.length > 0 && (timestamp - _timestamps[_timestamps.length - 1]) > RESET_GAP_S) {
    _timestamps = [];
  }

  _timestamps.push(timestamp);

  if (_timestamps.length > MAX_TAPS) {
    _timestamps = _timestamps.slice(-MAX_TAPS);
  }

  if (_timestamps.length < 2) {
    return null;
  }

  let intervalSum = 0;
  for (let i = 1; i < _timestamps.length; i++) {
    intervalSum += _timestamps[i] - _timestamps[i - 1];
  }
  const meanInterval = intervalSum / (_timestamps.length - 1);
  return clampBpm(60.0 / meanInterval);
}

export function reset(): void {
  _timestamps = [];
}

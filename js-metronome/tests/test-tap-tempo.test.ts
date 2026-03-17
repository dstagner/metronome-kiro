// Feature: js-metronome, Property 11 & 12: Tap tempo BPM calculation and reset
// Validates: Requirements 6.2, 6.3, 6.4

import { describe, test, beforeEach } from 'vitest';
import * as fc from 'fast-check';
import { recordTap, reset } from '../src/tapTempo';
import { clampBpm } from '../src/state';

beforeEach(() => {
  reset();
});

const MAX_TAPS = 4;

describe('tap tempo BPM calculation (Property 11)', () => {
  test('BPM from 2-4 taps equals clampBpm(60 / meanInterval)', () => {
    fc.assert(
      fc.property(
        fc.array(fc.float({ min: Math.fround(0.1), max: Math.fround(2.0), noNaN: true }), { minLength: 2, maxLength: 4 }),
        (intervals: number[]) => {
          reset();

          // Build monotonically increasing timestamps from intervals
          const timestamps: number[] = [0];
          for (const interval of intervals) {
            timestamps.push(timestamps[timestamps.length - 1] + interval);
          }

          let result: number | null = null;
          for (const ts of timestamps) {
            result = recordTap(ts);
          }

          // After >= 2 taps, result must be non-null
          if (result === null) return false;

          // The implementation keeps only the last MAX_TAPS timestamps,
          // so compute the mean over the intervals of those timestamps.
          const usedTimestamps = timestamps.slice(-MAX_TAPS);
          const usedIntervals: number[] = [];
          for (let i = 1; i < usedTimestamps.length; i++) {
            usedIntervals.push(usedTimestamps[i] - usedTimestamps[i - 1]);
          }
          const meanInterval = usedIntervals.reduce((a, b) => a + b, 0) / usedIntervals.length;
          const expected = clampBpm(60.0 / meanInterval);
          return result === expected;
        }
      ),
      { numRuns: 200 }
    );
  });
});

describe('tap sequence reset after 3-second gap (Property 12)', () => {
  test('a gap > 3s resets the tap sequence so the next tap starts fresh', () => {
    fc.assert(
      fc.property(
        fc.float({ min: Math.fround(3.001), max: Math.fround(10.0), noNaN: true }),
        (gap: number) => {
          reset();

          // Record two taps close together to establish a sequence
          recordTap(0.0);
          recordTap(0.5);

          // Now record a tap after a gap exceeding 3 seconds
          const result = recordTap(0.5 + gap);

          // After the gap, the sequence resets — only one tap in the new sequence,
          // so result should be null (need at least 2 taps)
          return result === null;
        }
      ),
      { numRuns: 200 }
    );
  });
});

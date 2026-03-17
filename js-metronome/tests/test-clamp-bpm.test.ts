// Feature: js-metronome, Property 1: BPM clamping is always in range
// Validates: Requirements 1.1, 1.4, 6.4

import { describe, test } from 'vitest';
import * as fc from 'fast-check';
import { clampBpm } from '../src/state';

describe('clampBpm', () => {
  test('always returns a value in [20, 300] for any integer', () => {
    fc.assert(
      fc.property(fc.integer({ min: -1000, max: 1000 }), (n: number) => {
        const result = clampBpm(n);
        return result >= 20 && result <= 300;
      }),
      { numRuns: 200 }
    );
  });

  test('always returns a value in [20, 300] for any float', () => {
    fc.assert(
      fc.property(fc.float({ min: -1000, max: 1000, noNaN: true }), (n: number) => {
        const result = clampBpm(n);
        return result >= 20 && result <= 300;
      }),
      { numRuns: 200 }
    );
  });

  test('values already in range are returned unchanged after rounding', () => {
    fc.assert(
      fc.property(fc.integer({ min: 20, max: 300 }), (n: number) => {
        return clampBpm(n) === n;
      }),
      { numRuns: 200 }
    );
  });
});

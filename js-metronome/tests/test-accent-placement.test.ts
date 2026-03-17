// Feature: js-metronome, Property 10: Accent placement follows time signature
// Validates: Requirements 5.1, 5.3

import { describe, test } from 'vitest';
import * as fc from 'fast-check';
import { isAccent } from '../src/state';

describe('isAccent', () => {
  test('isAccent(k, N) === (k % N === 0) for any k >= 0 and N in [1, 8]', () => {
    fc.assert(
      fc.property(
        fc.nat(),
        fc.integer({ min: 1, max: 8 }),
        (k: number, N: number) => {
          return isAccent(k, N) === (k % N === 0);
        }
      ),
      { numRuns: 200 }
    );
  });
});

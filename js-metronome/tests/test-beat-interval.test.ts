// Feature: js-metronome, Property 2: Beat interval matches BPM
// Validates: Requirement 1.2

import { describe, test } from 'vitest';
import * as fc from 'fast-check';
import { beatInterval } from '../src/state';

describe('beatInterval', () => {
  test('beatInterval(bpm) === 60 / bpm for any bpm in [20, 300]', () => {
    fc.assert(
      fc.property(fc.integer({ min: 20, max: 300 }), (bpm: number) => {
        return beatInterval(bpm) === 60 / bpm;
      }),
      { numRuns: 200 }
    );
  });
});

import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  CARD_SPRING,
  SPRING_PRESETS,
  advanceSpring,
  simulateFrameDeltas,
  simulateQtDriverDeltas,
  simulateSpring,
} from '../assets/card-spring.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../assets/qt-spring');
const assets = path.resolve(root, '..');
const checks = [];
const check = (condition, name) => {
  assert.ok(condition, name);
  checks.push(name);
};

// The existing source MediaCard trace remains the primary web contract.
const trace = JSON.parse(fs.readFileSync(path.join(assets, 'card-scale-oracle.json'), 'utf8'));
const press = trace.samples.filter((sample) => sample.phase === 'press');
const release = trace.samples.filter((sample) => sample.phase === 'release');
const pressModel = simulateSpring({ from: press[0].scale, target: 0.95, steps: press.length - 1 });
const releaseModel = simulateSpring({ from: 0.95, target: 1, steps: release.length }).slice(1);
check(press.every((sample, index) => Math.abs(sample.scale - pressModel[index].position) <= 1e-12), 'source card press trace exact');
check(release.every((sample, index) => Math.abs(sample.scale - releaseModel[index].position) <= 1e-12), 'source card release trace exact');
check(press.find((sample) => sample.scale === 0.95 && sample.t_ms > 0)?.t_ms === 592, 'source card epsilon settlement at 592ms');

// The browser adapter is fixed-step and therefore independent of callback
// cadence at equivalent logical times. This is a deterministic host rule,
// deliberately separate from the Qt startup-phase adapter below.
const fixedFrames = simulateFrameDeltas({ from: 1, target: 0.95, frameDeltas: [16, 16, 16, 16], startup: 'immediate' });
const splitFrames = simulateFrameDeltas({ from: 1, target: 0.95, frameDeltas: Array(8).fill(8), startup: 'immediate' });
const positionAt = (samples, time) => samples.find((sample) => sample.t_ms === time)?.position;
for (const time of [16, 32, 48, 64]) {
  check(Math.abs(positionAt(fixedFrames, time) - positionAt(splitFrames, time)) <= 1e-12, `browser fixed-step cadence at ${time}ms`);
}
const unevenFrames = simulateFrameDeltas({ from: 1, target: 0.95, frameDeltas: [5, 11, 7, 25, 13, 3, 29, 16], startup: 'immediate' });
check(Math.abs(positionAt(unevenFrames, 16) - positionAt(fixedFrames, 16)) <= 1e-12, 'browser uneven cadence first logical sample');
check(Math.abs(positionAt(unevenFrames, 48) - positionAt(fixedFrames, 48)) <= 1e-12, 'browser uneven cadence third logical sample');

// A retarget retains the fractional interval and velocity. Losing either one
// is a visible discontinuity when a pointer reverses while a card is moving.
let state = { position: 1, velocity: 0, accumulator: 0 };
state = advanceSpring(state, 0.95, 24, CARD_SPRING);
const beforeRetarget = { ...state };
state = advanceSpring(state, 1, 8, CARD_SPRING);
const expectedRetarget = advanceSpring(beforeRetarget, 1, 8, CARD_SPRING);
check(Math.abs(state.position - expectedRetarget.position) <= 1e-12, 'retarget keeps position and fractional time');
check(Math.abs(state.velocity - expectedRetarget.velocity) <= 1e-12, 'retarget keeps velocity');

// Compare every arbitrary source spring tuple with the QML probe. The probe
// models the QAnimationDriver lifecycle explicitly: the first callback stores
// its interval, and the second callback consumes it. This avoids time-shifting
// the actual Qt evidence into the browser's immediate-onset contract.
const qtFiles = [
  ['scale', CARD_SPRING],
  ['tilt', SPRING_PRESETS.pointerTilt],
  ['inspector', SPRING_PRESETS.inspectorWidth],
];
let qtComparisons = 0;
let qtMaxError = 0;
for (const prefix of ['qt', 'actual']) {
for (const [name, parameters] of qtFiles) {
  for (const cadence of ['fixed16', 'split8', 'uneven']) {
    const source = JSON.parse(fs.readFileSync(path.join(root, `${prefix}-${name}-${cadence}.json`), 'utf8')).scenarios[0];
    const model = simulateQtDriverDeltas({
      from: source.from ?? 0,
      target: source.target ?? 1,
      frameDeltas: source.deltas_ms,
      parameters,
    });
    assert.equal(model.length, source.values.length, `${name}/${cadence} sample count`);
    for (let index = 0; index < model.length; index += 1) {
      const error = Math.abs(model[index].position - source.values[index]);
      qtMaxError = Math.max(qtMaxError, error);
      qtComparisons += 1;
      assert.ok(error <= 1e-12, `${name}/${cadence} Qt sample ${index} error ${error}`);
    }
  }
}
}
check(qtComparisons === 210, 'Qt probe covers normalized and real scale, tilt, inspector amplitudes across three cadences');
check(qtMaxError <= 1e-12, 'Qt probe trajectory error is zero within numeric precision');

const result = {
  status: 'pass',
  checks: checks.length,
  qt_comparisons: qtComparisons,
  qt_max_abs_error: qtMaxError,
  browser_contract: 'fixed logical 16ms step with explicit immediate/deferred startup mode',
  qt_contract: 'advanceAnimation() probe with explicit first-callback lifecycle; not a claim about live compositor onset',
  presets: {
    cardScale: CARD_SPRING,
    pointerTilt: SPRING_PRESETS.pointerTilt,
    inspectorWidth: SPRING_PRESETS.inspectorWidth,
  },
};

console.log(JSON.stringify(result));

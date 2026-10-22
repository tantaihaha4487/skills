// The MediaCard Bounce wrapper is a local Qt SpringAnimation, not a CSS
// spring token. These presets use the numeric tuples in the source QML. The
// browser adapter deliberately runs a fixed logical step and accumulates RAF
// wall time: this makes a 60 Hz, 120 Hz, or uneven callback sequence produce
// the same logical samples. It does not claim that Qt's wall-clock driver has
// the same startup phase; qt_spring_probe.cpp records that separate boundary.
export const CARD_SPRING = Object.freeze({
  stiffness: 7,
  damping: 0.24,
  epsilon: 0.002,
  stepMs: 16,
});

export const SPRING_PRESETS = Object.freeze({
  cardScale: CARD_SPRING,
  pointerTilt: Object.freeze({ stiffness: 4, damping: 0.3, epsilon: 0.01, stepMs: 16 }),
  inspectorWidth: Object.freeze({ stiffness: 4, damping: 0.32, epsilon: 0.5, stepMs: 16 }),
});

function finiteNonNegative(value, label) {
  if (!Number.isFinite(value) || value < 0) throw new RangeError(`${label} must be finite and non-negative`);
  return value;
}

export function springStep(state, target, parameters = CARD_SPRING) {
  const velocity = state.velocity * (1 - parameters.damping)
    + (target - state.position) * parameters.stiffness;
  const position = state.position + velocity * parameters.stepMs / 1000;
  const settled = Math.abs(target - position) <= parameters.epsilon
    && Math.abs(velocity) <= parameters.epsilon;
  return settled
    ? { position: target, velocity: 0, settled: true }
    : { position, velocity, settled: false };
}

/**
 * Consume an arbitrary callback interval using the measured logical step.
 * The returned accumulator is intentionally public so a retarget can retain
 * a fractional frame instead of silently changing the trajectory.
 */
export function advanceSpring(state, target, milliseconds, parameters = CARD_SPRING, {
  maxFrameMs = 200,
} = {}) {
  finiteNonNegative(milliseconds, 'milliseconds');
  finiteNonNegative(maxFrameMs, 'maxFrameMs');
  if (!Number.isFinite(parameters.stepMs) || parameters.stepMs <= 0) {
    throw new RangeError('parameters.stepMs must be finite and positive');
  }
  let next = {
    position: state.position,
    velocity: state.velocity,
    accumulator: state.accumulator ?? 0,
    settled: false,
  };
  next.accumulator += Math.min(milliseconds, maxFrameMs);
  while (next.accumulator >= parameters.stepMs && !next.settled) {
    const stepped = springStep(next, target, parameters);
    next = {
      position: stepped.position,
      velocity: stepped.velocity,
      accumulator: next.accumulator - parameters.stepMs,
      settled: stepped.settled,
    };
  }
  if (next.settled) {
    next.position = target;
    next.velocity = 0;
    next.accumulator = 0;
  }
  return next;
}

export function simulateSpring({
  from,
  target,
  initialVelocity = 0,
  steps,
  parameters = CARD_SPRING,
}) {
  let state = { position: from, velocity: initialVelocity };
  const samples = [{ t_ms: 0, position: state.position, velocity: state.velocity }];
  for (let i = 1; i <= steps; i += 1) {
    state = springStep(state, target, parameters);
    samples.push({
      t_ms: i * parameters.stepMs,
      position: state.position,
      velocity: state.velocity,
    });
  }
  return samples;
}

/**
 * Deterministic logical samples for arbitrary RAF intervals. `immediate`
 * models the measured MediaCard fixture (the first sample advances one
 * logical step); `deferred` is useful when a host intentionally waits for a
 * first callback before beginning interaction motion. Neither mode rewrites
 * the Qt source trace; the mode is part of the host lifecycle contract.
 */
export function simulateFrameDeltas({
  from,
  target,
  initialVelocity = 0,
  frameDeltas,
  parameters = CARD_SPRING,
  startup = 'immediate',
  maxFrameMs = 200,
}) {
  if (!Array.isArray(frameDeltas)) throw new TypeError('frameDeltas must be an array');
  if (!['immediate', 'deferred'].includes(startup)) throw new RangeError(`unknown startup mode: ${startup}`);
  let state = { position: from, velocity: initialVelocity, accumulator: 0, settled: false };
  const samples = [{ t_ms: 0, position: state.position, velocity: state.velocity, settled: false }];
  let elapsed = 0;
  let first = true;
  for (const delta of frameDeltas) {
    finiteNonNegative(delta, 'frame delta');
    elapsed += delta;
    if (first && startup === 'deferred') {
      first = false;
    } else {
      state = advanceSpring(state, target, delta, parameters, { maxFrameMs });
      first = false;
    }
    samples.push({ t_ms: elapsed, position: state.position, velocity: state.velocity, settled: state.settled });
  }
  return samples;
}

/**
 * Reproduces the lifecycle of the deterministic QAnimationDriver probe. Qt
 * registers the Behavior on the first driver callback and retains that first
 * interval; it consumes the accumulated interval on the second callback.
 * This is intentionally named as a probe adapter, not the browser default:
 * the source MediaCard fixture and a live compositor can begin in a different
 * phase.
 */
export function simulateQtDriverDeltas({
  from,
  target,
  initialVelocity = 0,
  frameDeltas,
  parameters = CARD_SPRING,
  maxFrameMs = 200,
}) {
  if (!Array.isArray(frameDeltas)) throw new TypeError('frameDeltas must be an array');
  let state = { position: from, velocity: initialVelocity, accumulator: 0, settled: false };
  const samples = [{ t_ms: 0, position: state.position, velocity: state.velocity, settled: false }];
  let elapsed = 0;
  for (let index = 0; index < frameDeltas.length; index += 1) {
    const delta = finiteNonNegative(frameDeltas[index], 'frame delta');
    elapsed += delta;
    state.accumulator += Math.min(delta, maxFrameMs);
    if (index > 0) {
      state = advanceSpring(state, target, 0, parameters, { maxFrameMs });
    }
    samples.push({ t_ms: elapsed, position: state.position, velocity: state.velocity, settled: state.settled });
  }
  return samples;
}

export class CardScaleAnimation {
  constructor({
    element,
    initial = 1,
    parameters = CARD_SPRING,
    onUpdate,
    performance = false,
    startup = 'immediate',
    maxFrameMs = 200,
  }) {
    this.element = element;
    this.parameters = parameters;
    this.position = initial;
    this.velocity = 0;
    this.target = initial;
    this.onUpdate = onUpdate;
    this.performance = performance;
    this.startup = startup;
    this.maxFrameMs = maxFrameMs;
    this.frame = null;
    this.lastTimestamp = null;
    this.accumulator = 0;
    this.started = false;
    this.disposed = false;
    this.render();
  }

  render() {
    if (this.element) {
      this.element.style.setProperty('--spring-scale', String(this.position));
    }
    this.onUpdate?.(this.position, this);
  }

  setPerformance(performance) {
    this.performance = performance;
    if (performance) {
      this.position = this.target;
      this.velocity = 0;
      this.cancel();
      this.render();
    } else if (this.position !== this.target) {
      this.schedule();
    }
  }

  setTarget(target) {
    if (this.disposed) return;
    this.target = target;
    // A retarget cancels the pending browser callback but preserves the
    // measured current position and velocity, matching a live Qt behavior.
    // Stop only the pending callback. Keep accumulator/velocity so a
    // retarget during an uneven RAF interval does not lose elapsed time.
    this.cancel({ preserveState: true });
    if (this.performance) {
      this.position = target;
      this.velocity = 0;
      this.render();
      return;
    }
    if (this.position === target && this.velocity === 0) {
      this.render();
      return;
    }
    this.schedule();
  }

  advance(milliseconds) {
    if (this.disposed || this.performance) return;
    const next = advanceSpring(
      { position: this.position, velocity: this.velocity, accumulator: this.accumulator },
      this.target,
      milliseconds,
      this.parameters,
      { maxFrameMs: this.maxFrameMs },
    );
    this.position = next.position;
    this.velocity = next.velocity;
    this.accumulator = next.accumulator;
    this.render();
    if (this.position === this.target && this.velocity === 0) {
      this.cancel();
      this.started = false;
    }
  }

  schedule() {
    if (this.disposed || this.performance || this.frame !== null) return;
    this.lastTimestamp = null;
    const tick = (timestamp) => {
      this.frame = null;
      if (this.disposed || this.performance) return;
      if (this.lastTimestamp === null) {
        this.lastTimestamp = timestamp;
        this.started = true;
        // The measured source MediaCard fixture advances on its first
        // interaction sample. Hosts that need a deferred onset can opt in.
        if (this.startup === 'immediate') this.accumulator += this.parameters.stepMs;
      } else {
        this.accumulator += Math.min(this.maxFrameMs, Math.max(0, timestamp - this.lastTimestamp));
        this.lastTimestamp = timestamp;
      }
      this.advance(0);
      if (!(this.position === this.target && this.velocity === 0)) {
        this.frame = requestAnimationFrame(tick);
      }
    };
    this.frame = requestAnimationFrame(tick);
  }

  cancel({ preserveState = false } = {}) {
    if (this.frame !== null) cancelAnimationFrame(this.frame);
    this.frame = null;
    this.lastTimestamp = null;
    if (!preserveState) {
      this.accumulator = 0;
      this.started = false;
    }
  }

  dispose() {
    this.disposed = true;
    this.cancel();
    this.element = null;
    this.onUpdate = null;
  }
}

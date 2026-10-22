// Browser implementation of the reference shell's immersive reveal lifecycle.  The
// values are kept as live state instead of replacing a CSS animation on each
// toggle, so opening while closing (and the reverse) starts at the current
// reveal and rotation rather than jumping to an endpoint.

const clamp = (value, low = 0, high = 1) => Math.max(low, Math.min(high, value));
const mix = (a, b, t) => a + (b - a) * t;
const outCubic = (t) => 1 - (1 - t) ** 3;
const outBack = (t, overshoot = 2.4) => 1 + (overshoot + 1) * (t - 1) ** 3 + overshoot * (t - 1) ** 2;
const inBack = (t, overshoot = 1.2) => (overshoot + 1) * t ** 3 - overshoot * t ** 2;

// Keep this table in lock-step with the reference shape catalogue.  the reference shell grows
// the mask using the shape distance-field parameters, rather than a generic
// polygon multiplier.  The browser fixture samples the same analytic polar boundary;
// the reach calculation follows the source equation so
// valley-heavy shapes clear the same corners at the same scalar progress.
export const REVEAL_SHAPE_PARAMS = Object.freeze({
  circle: [0, 0, 1, 0],
  cookie6: [6, 0.1, 1, 0],
  cookie9: [9, 0.09, 1, 0],
  clover4: [4, 0.42, 0.55, 0],
  clover8: [8, 0.28, 0.6, 0],
  sunny: [8, 0.14, 2.2, 0],
  verySunny: [8, 0.26, 2.6, 0],
  softBurst: [10, 0.16, 1.5, 0],
  burst: [12, 0.24, 2.8, 0],
  flower: [8, 0.32, 0.45, 0],
  puffy: [6, 0.18, 0.5, 0],
  pentagon: [5, 0.12, 3, 0],
  gem: [6, 0.08, 4, 0],
});

/**
 * Deterministic scalar trace for the reference shell's fixed-driver lifecycle.
 *
 * The first QAnimationDriver callback records its interval and the second
 * callback consumes it.  Consequently the source trace labels t=0 and t=16
 * with the initial values, and the first visible step appears at t=32.  The
 * browser runtime may receive its first RAF at a different wall-clock phase;
 * this helper keeps that measured source boundary explicit for parity tests.
 */
export function sourceImmersiveSamples({
  openEndMs = 720,
  closeEndMs = 640,
  sampleMs = 16,
  startupDelayMs = 16,
  startSpin = 0,
} = {}) {
  const effective = (time) => Math.max(0, time - startupDelayMs);
  const open = [];
  for (let time = 0; time <= openEndMs; time += sampleMs) {
    const elapsed = effective(time);
    let reach = 0;
    let reveal = 0.01;
    let spin = startSpin;
    if (elapsed <= 260) {
      reach = mix(0, 0.2, outBack(elapsed / 260, 2.4));
    } else if (elapsed <= 320) {
      reach = 0.2;
    } else if (elapsed < 600) {
      reach = mix(0.2, 1, inBack((elapsed - 320) / 280, 1.2));
    } else {
      reach = 1;
    }
    if (elapsed < 600) {
      spin = startSpin + 1.6 * Math.PI * (elapsed / 600);
    } else {
      reach = 1;
      reveal = 1;
      spin = startSpin + 1.6 * Math.PI;
    }
    open.push({ phase: 'open', t_ms: time, reach, reveal, spin, fade: 1 });
  }

  const closeStartSpin = startSpin + 1.6 * Math.PI;
  const close = [];
  for (let time = 0; time <= closeEndMs; time += sampleMs) {
    const elapsed = effective(time);
    const t = clamp(elapsed / 520);
    const eased = outCubic(t);
    close.push({
      phase: 'close',
      t_ms: time,
      reach: mix(1, 0, eased),
      reveal: mix(0.99, 0, eased),
      spin: closeStartSpin + 1.4 * eased,
      fade: 1,
    });
  }
  return { open, close };
}

export function revealMaskReach(reach, width, height, shapeName = 'cookie9') {
  const params = REVEAL_SHAPE_PARAMS[shapeName] || REVEAL_SHAPE_PARAMS.circle;
  const divisor = params[3] > 0.5 ? 1 : 1 - params[1];
  return Math.max(0, reach) * Math.hypot(width, height) / 2 / divisor + 2;
}

function hash32(text) {
  let value = 2166136261;
  for (const byte of new TextEncoder().encode(String(text ?? ''))) value = Math.imul(value ^ byte, 16777619) >>> 0;
  return value >>> 0;
}

// Default reveal seed; a number is used as the hash directly.
export const DEFAULT_REVEAL_SEED = 867747986;

export function chooseRevealShape(key, names) {
  const pool = names.filter((name) => name !== 'circle');
  const seed = typeof key === 'number' ? key >>> 0 : hash32(key);
  return pool[seed % pool.length] || 'cookie9';
}

export function sampleShapePath(pathData, samples = 96) {
  if (typeof document === 'undefined') return [];
  const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  path.setAttribute('d', pathData);
  const length = path.getTotalLength();
  return Array.from({ length: samples }, (_, index) => path.getPointAtLength(length * index / samples));
}

export class ImmersiveController {
  constructor({ element, shell, shapes = {}, names = [], onOpen = () => {}, onClose = () => {} }) {
    this.element = element;
    this.shell = shell;
    this.shapes = shapes;
    this.names = names;
    this.onOpen = onOpen;
    this.onClose = onClose;
    this.reveal = 0;
    this.reach = 0;
    this.spin = 0;
    this.fade = 1;
    this.shapeName = names[0] || 'cookie9';
    this.shapeSelected = false;
    this.targetOpen = false;
    this.mode = 'shape';
    this.noShapes = false;
    this.duration = 600;
    this.startedAt = 0;
    this.startReveal = 0;
    this.startReach = 0;
    this.startSpin = 0;
    this.frame = null;
    this.disposed = false;
    this.lastTime = null;
    this.element.hidden = true;
  }

  setOpen(open, { policy = 'shape', key = DEFAULT_REVEAL_SEED, noShapes = false } = {}) {
    if (this.disposed) return;
    this.targetOpen = Boolean(open);
    this.mode = policy;
    this.noShapes = Boolean(noShapes);
    this.cancelFrame();
    this.startReveal = this.reveal;
    this.startReach = this.reach;
    // the reference shell wraps the shared turn before each transition so long-running
    // playback cannot grow an unbounded angle.  The scalar reveal is a
    // loader/drawing gate: opening holds it at .01 while reach grows, then
    // finishOpening promotes it to 1 (the shader geometry is reach).
    this.startSpin = this.spin % (2 * Math.PI);
    this.spin = this.startSpin;
    if (this.targetOpen && this.mode === 'shape' && (!this.shapeSelected || this.reveal <= 0.002 || this.noShapes)) {
      this.shapeName = this.noShapes ? 'circle' : chooseRevealShape(key, this.names);
      this.shapeSelected = true;
    }
    if (this.mode === 'snap') {
      this.spin = this.startSpin + (this.targetOpen ? 1.6 * Math.PI : 1.4);
      this.reveal = this.targetOpen ? 1 : 0;
      this.reach = this.targetOpen ? 1 : 0;
      this.render();
      this.complete();
      return;
    }
    if (this.mode === 'fade') {
      this.element.hidden = false;
      this.shell.inert = this.targetOpen;
      this.shell.style.visibility = 'visible';
      this.reveal = this.targetOpen ? 0.01 : Math.min(this.startReveal, 0.99);
      this.reach = this.targetOpen ? 1 : this.startReach;
      this.startOpacity = this.targetOpen ? 0 : this.fade;
      this.fade = this.startOpacity;
      if (this.targetOpen) this.spin = this.startSpin + 1.6 * Math.PI;
      this.element.style.clipPath = 'none';
      this.element.style.opacity = String(this.startOpacity);
      this.duration = this.targetOpen ? 240 : 200;
    } else {
      this.element.hidden = false;
      this.shell.inert = this.targetOpen;
      if (!this.targetOpen) this.shell.style.visibility = 'visible';
      this.duration = this.targetOpen ? 600 : 520;
      this.element.style.opacity = '1';
      this.fade = 1;
      if (this.targetOpen) {
        this.reveal = 0.01;
      } else {
        // closeMotion's first PropertyAction is min(immersiveReveal, .99)
        // before its OutCubic shrink begins.
        this.startReveal = Math.min(this.reveal, 0.99);
        this.reveal = this.startReveal;
      }
    }
    this.startedAt = performance.now();
    this.lastTime = this.startedAt;
    this.render();
    this.frame = requestAnimationFrame((time) => this.tick(time));
  }

  tick(time) {
    this.frame = null;
    if (this.disposed) return;
    const elapsed = Math.max(0, time - this.startedAt);
    const t = clamp(elapsed / this.duration);
    if (this.mode === 'fade') {
      this.fade = this.targetOpen ? outCubic(t) : this.startOpacity * (1 - t ** 3);
      this.element.style.opacity = String(this.fade);
    } else if (this.targetOpen) {
      // the reference shell's 260ms OutBack + 60ms hold + 280ms InBack stages.
      if (elapsed <= 260) this.reach = mix(this.startReach, 0.2, outBack(elapsed / 260, 2.4));
      else if (elapsed <= 320) this.reach = 0.2;
      else this.reach = mix(0.2, 1, inBack((elapsed - 320) / 280, 1.2));
      this.reveal = 0.01;
      this.spin = this.startSpin + 1.6 * Math.PI * t;
    } else {
      const eased = outCubic(t);
      this.reach = mix(this.startReach, 0, eased);
      this.reveal = mix(this.startReveal, 0, eased);
      this.spin = this.startSpin + 1.4 * eased;
    }
    this.render();
    if (t >= 1) {
      this.complete();
      return;
    }
    this.frame = requestAnimationFrame((next) => this.tick(next));
  }

  render() {
    if (this.mode === 'fade' || this.mode === 'snap' || this.reveal >= 0.999) {
      this.element.style.clipPath = 'none';
      return;
    }
    const params = REVEAL_SHAPE_PARAMS[this.shapeName] || REVEAL_SHAPE_PARAMS.circle;
    const width=this.element.clientWidth||innerWidth,height=this.element.clientHeight||innerHeight;
    const scale = revealMaskReach(this.reach, width, height, this.shapeName);
    const cx = width / 2, cy = height / 2;
    // the reference shell clamps the picked lobe count to five before shape_mask.frag.
    // The mask uses an analytic radial boundary, not the atlas outline.
    // CSS polygon rasterization remains a host adaptation; use the shader
    // renderer when exact edge pixels are part of the parity contract.
    const polygon = Array.from({length:1024}, (_, index) => {
      const theta = index * 2 * Math.PI / 1024;
      const radius = params[3] > .5
        ? scale / (Math.abs(Math.cos(theta)) ** params[2] + Math.abs(Math.sin(theta)) ** params[2]) ** (1 / params[2])
        : scale * (1 - params[1] + params[1] * (.5 + .5 * Math.cos(Math.min(params[0],5) * theta)) ** params[2]);
      return `${cx + radius * Math.cos(theta + this.spin)}px ${cy + radius * Math.sin(theta + this.spin)}px`;
    }).join(',');
    this.element.style.clipPath = `polygon(${polygon})`;
  }

  complete() {
    this.cancelFrame();
    this.fade = 1;
    if (this.targetOpen) {
      this.reveal = 1;
      this.reach = 1;
      this.element.hidden = false;
      this.element.style.opacity = '1';
      this.element.style.clipPath = 'none';
      this.shell.style.visibility = 'hidden';
      this.shell.inert = true;
      this.onOpen();
    } else {
      if (this.mode === 'fade') this.spin = this.startSpin + 1.4;
      this.reveal = 0;
      this.reach = 0;
      this.element.hidden = true;
      this.element.style.opacity = '1';
      this.element.style.clipPath = 'none';
      this.shell.style.visibility = 'visible';
      this.shell.inert = false;
      this.onClose();
    }
  }

  cancelFrame() {
    if (this.frame !== null) cancelAnimationFrame(this.frame);
    this.frame = null;
    this.lastTime = null;
  }

  cancel() { this.cancelFrame(); }

  dispose() {
    this.disposed = true;
    this.cancelFrame();
    this.element.hidden = true;
    this.shell.inert = false;
    this.shell.style.visibility = 'visible';
  }
}

// Source-shaped card-to-collection-hero handoff.  The native implementation
// keeps an already decoded cover in a temporary Item until the destination
// ArtworkImage is ready.  This browser adapter does the same with a fixed
// overlay, a moving target rect and the measured fixed-step spring.

function step(state, target) {
  const velocity = state.velocity * (1 - 0.27) + (target - state.position) * 3.4;
  const position = state.position + velocity * 0.016;
  const settled = Math.abs(target - position) <= 0.002 && Math.abs(velocity) <= 0.002;
  return settled ? { position: target, velocity: 0, settled: true } : { position, velocity, settled: false };
}

export class HeroFlight {
  constructor({
    root = document.body,
    performance = false,
    onFinish = () => {},
  } = {}) {
    this.root = root;
    this.performance = performance;
    this.onFinish = onFinish;
    this.overlay = null;
    this.destination = null;
    this.position = 0;
    this.velocity = 0;
    this.frame = null;
    this.deadline = null;
    this.lastTimestamp = null;
    this.accumulator = 0;
    this.from = null;
    this.to = null;
    this.fromRadius = 12;
    this.toRadius = 17;
    this.disposed = false;
  }

  setPerformance(performance) {
    this.performance = performance;
    if (performance && this.overlay) this.finish();
  }

  arm({ sourceElement, source, destination = null, fromRadius = 12, toRadius = 17 }) {
    this.cancel();
    if (this.disposed || this.performance || !sourceElement || !source) return false;
    const rect = sourceElement.getBoundingClientRect();
    if (rect.width <= 0 || rect.height <= 0) return false;
    this.from = { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
    this.fromRadius = fromRadius;
    this.toRadius = toRadius;
    this.position = 0;
    this.velocity = 0;
    this.destination = destination;
    const overlay = document.createElement('div');
    overlay.className = 'hero-flight';
    overlay.setAttribute('aria-hidden', 'true');
    const image = document.createElement('img');
    image.alt = '';
    image.decoding = 'sync';
    image.src = source;
    overlay.append(image);
    this.overlay = overlay;
    this.root.append(overlay);
    this.render();
    this.deadline = setTimeout(() => this.finish(), 2200);
    if (destination) this.setDestination(destination);
    else this.schedule();
    return true;
  }

  setDestination(destination) {
    if (!this.overlay) return;
    this.destination?.classList.remove('hero-flight-target');
    this.destination = destination;
    if (!destination) return;
    destination.classList.add('hero-flight-target');
    this.measureDestination();
    this.schedule();
  }

  measureDestination() {
    if (!this.destination) return;
    const rect = this.destination.getBoundingClientRect();
    if (rect.width <= 0 || rect.height <= 0) return;
    this.to = { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
  }

  rescale(factor) {
    if(this.disposed||!this.overlay||!this.from)return;
    if(!Number.isFinite(factor)||factor<=0)throw new RangeError('Invalid hero zoom ratio');
    for(const rect of [this.from,this.to])if(rect)for(const key of ['x','y','width','height'])rect[key]*=factor;
    this.fromRadius*=factor;this.toRadius*=factor;
    this.measureDestination();this.render();
  }

  destinationReady() {
    if (!this.destination) return false;
    const image = this.destination instanceof HTMLImageElement ? this.destination : this.destination.querySelector('img');
    return !image || (image.complete && image.naturalWidth > 0);
  }

  schedule() {
    if (this.frame !== null || !this.overlay) return;
    this.lastTimestamp = null;
    this.accumulator = 0;
    const tick = (timestamp) => {
      this.frame = null;
      if (this.disposed || !this.overlay) return;
      this.measureDestination();
      if (this.lastTimestamp === null) this.accumulator = 16;
      else this.accumulator += Math.min(200, Math.max(0, timestamp - this.lastTimestamp));
      this.lastTimestamp = timestamp;
      while (this.accumulator >= 16) {
        const next = step({ position: this.position, velocity: this.velocity }, 1);
        this.position = next.position;
        this.velocity = next.velocity;
        this.accumulator -= 16;
        if (next.settled) break;
      }
      this.render();
      if (this.position === 1 && this.velocity === 0 && this.to && this.destinationReady()) this.finish();
      else this.frame = requestAnimationFrame(tick);
    };
    this.frame = requestAnimationFrame(tick);
  }

  advance(milliseconds) {
    if (!this.overlay || this.disposed || this.performance) return;
    this.accumulator += Math.max(0, milliseconds);
    while (this.accumulator >= 16) {
      const next = step({ position: this.position, velocity: this.velocity }, 1);
      this.position = next.position;
      this.velocity = next.velocity;
      this.accumulator -= 16;
      if (next.settled) break;
    }
    this.render();
    if (this.position === 1 && this.velocity === 0 && this.to && this.destinationReady()) this.finish();
  }

  render() {
    if (!this.overlay || !this.from) return;
    const target = this.to || this.from;
    // The source deliberately flies past its target before settling.
    const t = this.position;
    const x = this.from.x + (target.x - this.from.x) * t;
    const y = this.from.y + (target.y - this.from.y) * t;
    const width = this.from.width + (target.width - this.from.width) * t;
    const height = width;
    const radius = this.fromRadius + (this.toRadius - this.fromRadius) * t;
    Object.assign(this.overlay.style, {
      left: `${x}px`, top: `${y}px`, width: `${width}px`, height: `${height}px`,
      borderRadius: `${Math.max(0, radius)}px`,
    });
  }

  finish() {
    if (!this.overlay) return;
    this.cancelFrame();
    if (this.deadline !== null) clearTimeout(this.deadline);
    this.deadline = null;
    this.destination?.classList.remove('hero-flight-target');
    const overlay = this.overlay;
    this.overlay = null;
    this.destination = null;
    this.to = null;
    overlay.remove();
    this.onFinish();
  }

  cancelFrame() {
    if (this.frame !== null) cancelAnimationFrame(this.frame);
    this.frame = null;
    this.lastTimestamp = null;
    this.accumulator = 0;
  }

  cancel() {
    this.cancelFrame();
    if (this.deadline !== null) clearTimeout(this.deadline);
    this.deadline = null;
    this.destination?.classList.remove('hero-flight-target');
    this.overlay?.remove();
    this.overlay = null;
    this.destination = null;
    this.to = null;
  }

  dispose() {
    this.disposed = true;
    this.cancel();
    this.onFinish = () => {};
  }
}

export function heroSpringSamples(steps = 160) {
  let state = { position: 0, velocity: 0 };
  const samples = [{ t_ms: 0, position: 0, velocity: 0 }];
  for (let index = 1; index <= steps; index += 1) {
    state = step(state, 1);
    samples.push({ t_ms: index * 16, position: state.position, velocity: state.velocity });
    if (state.settled) break;
  }
  return samples;
}

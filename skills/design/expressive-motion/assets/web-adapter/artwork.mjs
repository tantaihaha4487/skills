import {hash32 as fallbackSeed} from './hash.mjs';
import {clamp} from './math.mjs';

// Deterministic browser port of src/artwork/PlaylistCovers.cpp::fallback.
// This is intentionally a local rendering helper: it never fetches artwork or
// derives a provider identity from a process seeded hash.

const PALETTES = Object.freeze([
  { dark: '#42313e', light: '#f0dfdf', shape: '#dc9988', ribbon: '#f4ddae', accent: '#a6bcaa' },
  { dark: '#293f39', light: '#e2e8d8', shape: '#b3c9a0', ribbon: '#e8b28f', accent: '#f4e7c6' },
  { dark: '#553c32', light: '#f2e2ce', shape: '#e7ae76', ribbon: '#a6bdc9', accent: '#f4dec1' },
  { dark: '#303e54', light: '#e1e7ef', shape: '#b1badb', ribbon: '#ead69a', accent: '#d69583' },
  { dark: '#49432e', light: '#eee7d5', shape: '#d8c27c', ribbon: '#c9a1aa', accent: '#f4e4c2' },
  { dark: '#453849', light: '#eae0eb', shape: '#c3acd1', ribbon: '#a6c7b8', accent: '#eed29d' },
]);

/** FNV-1a over UTF-8, matching the C++ fallback byte-for-byte. */
export {fallbackSeed};

export function fallbackSpec(key, dark = true) {
  const seed = fallbackSeed(key);
  const palette = PALETTES[seed % PALETTES.length];
  return Object.freeze({
    key: String(key ?? ''),
    seed,
    sleeve: seed % PALETTES.length,
    composition: (seed >>> 8) % 6,
    phase: ((seed >>> 16) % 360) * Math.PI / 180,
    dark: Boolean(dark),
    ...palette,
    base: dark ? palette.dark : palette.light,
  });
}

function hexRgb(hex) {
  const value = Number.parseInt(hex.slice(1), 16);
  return [value >> 16 & 255, value >> 8 & 255, value & 255];
}

function alphaRgb(hex, alpha) {
  const [r, g, b] = hexRgb(hex);
  return `rgba(${r},${g},${b},${alpha})`;
}

function lighter(hex, factor) {
  const [r, g, b] = hexRgb(hex);
  return `rgb(${clamp(Math.round(r * factor / 100), 0, 255)},${clamp(Math.round(g * factor / 100), 0, 255)},${clamp(Math.round(b * factor / 100), 0, 255)})`;
}

function drawBloom(ctx, spec, centre) {
  const { composition, phase } = spec;
  ctx.beginPath();
  if (composition === 2 || composition === 4) {
    ctx.ellipse(centre.x, centre.y, 119, 119, 0, 0, Math.PI * 2);
  } else {
    const petals = composition === 1 ? 8 : 10;
    for (let step = 0; step <= 360; step += 1) {
      const angle = step * Math.PI / 180;
      const radius = 108 + 10 * Math.cos(petals * angle + phase);
      const x = centre.x + Math.cos(angle) * radius;
      const y = centre.y + Math.sin(angle) * radius;
      if (step === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
  }
}

function drawCurve(ctx, composition, centre) {
  ctx.beginPath();
  switch (composition) {
    case 0:
      ctx.moveTo(-30, 173); ctx.bezierCurveTo(67, 61, 128, 292, 285, 160); break;
    case 1:
      ctx.moveTo(49, -30); ctx.bezierCurveTo(236, 22, 17, 152, 277, 189); break;
    case 2:
      ctx.moveTo(-28, 77); ctx.bezierCurveTo(151, -3, 16, 266, 286, 191); break;
    case 3:
      ctx.moveTo(-28, 199); ctx.bezierCurveTo(200, 258, 78, -32, 277, 66); break;
    case 4:
      ctx.ellipse(172, 136, 76, 76, 0, 0, Math.PI * 2); break;
    default:
      ctx.moveTo(-26, 118); ctx.bezierCurveTo(88, 231, 154, -26, 285, 78);
  }
}

/**
 * Paint a fallback sleeve at the requested edge. Canvas is used instead of
 * embedding the native screenshot: the six native palettes/compositions and
 * fixed paper grain remain independently rendered in the browser.
 */
export function renderFallback(key, dark = true, edge = 256) {
  if (typeof document === 'undefined') return null;
  const size = Math.max(1, Math.round(edge));
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d', { alpha: false });
  const spec = fallbackSpec(key, dark);
  const scale = size / 256;
  ctx.scale(scale, scale);
  const base = spec.base;
  ctx.fillStyle = base;
  ctx.fillRect(0, 0, 256, 256);
  const wash = ctx.createLinearGradient(0, 0, 256, 256);
  wash.addColorStop(0, lighter(base, dark ? 108 : 102));
  wash.addColorStop(1, base);
  ctx.fillStyle = wash;
  ctx.fillRect(0, 0, 256, 256);
  ctx.lineJoin = 'round';
  ctx.lineCap = 'round';
  ctx.setLineDash([]);

  const centres = [{ x: 170, y: 102 }, { x: 89, y: 173 }, { x: 180, y: 177 },
    { x: 83, y: 90 }, { x: 172, y: 136 }, { x: 113, y: 170 }];
  const centre = centres[spec.composition];
  drawBloom(ctx, spec, centre);
  ctx.save();
  ctx.translate(0, 3);
  ctx.fillStyle = alphaRgb('#16121b', dark ? 0.16 : 0.08);
  ctx.fill();
  ctx.restore();
  drawBloom(ctx, spec, centre);
  ctx.fillStyle = spec.shape;
  ctx.fill();

  drawCurve(ctx, spec.composition, centre);
  ctx.strokeStyle = spec.ribbon;
  ctx.lineWidth = spec.composition === 4 ? 29 : 37;
  ctx.stroke();
  if (spec.composition === 2 || spec.composition === 4) {
    ctx.beginPath();
    ctx.fillStyle = base;
    ctx.arc(centre.x, centre.y, spec.composition === 4 ? 30 : 17, 0, Math.PI * 2);
    ctx.fill();
  }
  const accents = [{ x: 39, y: 45 }, { x: 210, y: 47 }, { x: 42, y: 210 },
    { x: 211, y: 212 }, { x: 39, y: 49 }, { x: 211, y: 211 }];
  ctx.beginPath();
  ctx.fillStyle = spec.accent;
  ctx.arc(accents[spec.composition].x, accents[spec.composition].y, 7, 0, Math.PI * 2);
  ctx.fill();
  ctx.setTransform(1, 0, 0, 1, 0, 0);

  const pixels = ctx.getImageData(0, 0, size, size);
  const xSeeds = Array.from({length:size},(_,x)=>(Math.floor(x*256/size)*374761393)>>>0);
  for (let y = 0; y < size; y += 1) {
    const ySeed = (Math.floor(y * 256 / size) * 668265263) >>> 0;
    for (let x = 0; x < size; x += 1) {
      let grain = xSeeds[x] + ySeed + spec.seed;
      grain = Math.imul((grain ^ (grain >>> 13)) >>> 0, 1274126177) >>> 0;
      const delta = ((grain >>> 24) % 5) - 2;
      const at = (y * size + x) * 4;
      pixels.data[at] = clamp(pixels.data[at] + delta, 0, 255);
      pixels.data[at + 1] = clamp(pixels.data[at + 1] + delta, 0, 255);
      pixels.data[at + 2] = clamp(pixels.data[at + 2] + delta, 0, 255);
    }
  }
  ctx.putImageData(pixels, 0, 0);
  return canvas.toDataURL('image/png');
}

const cache = new Map();
export function fallbackDataUrl(key, dark = true, edge = 256) {
  const size = Math.max(1, Math.round(edge));
  const cacheKey = `${dark ? 'dark' : 'light'}:${String(key ?? '')}:${size}`;
  if (!cache.has(cacheKey)) cache.set(cacheKey, renderFallback(key, dark, size));
  return cache.get(cacheKey);
}

export function clearFallbackCache() { cache.clear(); }

export const fallbackPalettes = PALETTES;

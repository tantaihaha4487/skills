import {SOURCE_REVEAL_SHAPES} from './reveal-shapes.mjs';
import {compileShader,uniformFields} from './shader-utils.mjs';
export {SOURCE_REVEAL_SHAPES};

// Independent WebGL2 adapter for source rounded_image.frag and
// shape_mask.frag. Programs, geometry, and the texture owner persist across
// frames. The caller supplies source shader text, uniforms, and optionally a
// real HTMLImageElement, ImageBitmap, HTMLCanvasElement, or OffscreenCanvas;
// this file contains no screenshot, path, or fallback artwork.
const VERTEX = `#version 300 es
in vec2 position;
out vec2 qt_TexCoord0;
void main() {
  gl_Position = vec4(position, 0.0, 1.0);
  // Qt Quick's ShaderEffect coordinates are top-left origin. The upload
  // path preserves the TexImageSource row order so this remains true for
  // WebGL textures.
  qt_TexCoord0 = vec2(position.x * 0.5 + 0.5, 0.5 - position.y * 0.5);
}`;

const DEFAULT_SOURCE_COLOR = Object.freeze([0x62, 0xd2, 0x94, 0xff]);
const CANVAS_RENDERERS = new WeakMap();

export function adaptSourceShader(source) {
  let shader = source.replace(/^#version 440\s*/m, '#version 300 es\nprecision highp float;\n');
  shader = shader.replace(/layout\(location\s*=\s*0\)\s+in\s+vec2\s+qt_TexCoord0\s*;/,
                          'in vec2 qt_TexCoord0;');
  shader = shader.replace(/layout\(location\s*=\s*0\)\s+out\s+vec4\s+fragColor\s*;/,
                          'out vec4 fragColor;');
  shader = shader.replace(/layout\(std140,\s*binding\s*=\s*0\)\s+uniform\s+buf\s*\{([\s\S]*?)\};/,
    (_match, fields) => uniformFields(fields));
  shader = shader.replace(/layout\(binding\s*=\s*1\)\s+uniform\s+sampler2D\s+source\s*;/,
                          'uniform sampler2D source;');
  return shader;
}

function programFor(gl, source) {
  const vertex = compileShader(gl, gl.VERTEX_SHADER, VERTEX, 'WebGL shader compilation failed');
  let fragment;
  try {
    fragment = compileShader(gl, gl.FRAGMENT_SHADER, adaptSourceShader(source), 'WebGL shader compilation failed');
  } catch (error) {
    gl.deleteShader(vertex);
    throw error;
  }
  let program;
  try {
    program = gl.createProgram();
    gl.attachShader(program, vertex);
    gl.attachShader(program, fragment);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      const log = gl.getProgramInfoLog(program);
      throw new Error(log || 'WebGL shader link failed');
    }
    return program;
  } catch (error) {
    if (program) gl.deleteProgram(program);
    throw error;
  } finally {
    // Shader objects are short-lived link inputs. The linked program remains
    // owned by SourceRenderer until dispose(), rather than being rebuilt per
    // animation frame.
    gl.deleteShader(vertex);
    gl.deleteShader(fragment);
  }
}

function sourceDimensions(source) {
  if (!source) return {width: 1, height: 1};
  return {
    width: source.naturalWidth || source.videoWidth || source.width || 0,
    height: source.naturalHeight || source.videoHeight || source.height || 0,
  };
}

function sourceURI(source) {
  if (!source) return '';
  const currentSrc = typeof source.currentSrc === 'string' ? source.currentSrc : '';
  const src = typeof source.src === 'string' ? source.src : '';
  return currentSrc || src;
}

function sourceTime(source) {
  const time = source && source.currentTime;
  return typeof time === 'number' && Number.isFinite(time) ? time : null;
}

function sourceSnapshot(source) {
  return {
    dimensions: sourceDimensions(source),
    sourceURI: sourceURI(source),
    sourceTime: sourceTime(source),
  };
}

function isImageElement(source) {
  return (typeof HTMLImageElement !== 'undefined' && source instanceof HTMLImageElement)
    || source?.tagName === 'IMG';
}

function isVideoElement(source) {
  return (typeof HTMLVideoElement !== 'undefined' && source instanceof HTMLVideoElement)
    || source?.tagName === 'VIDEO';
}

function assertTextureSourceReady(source, snapshot) {
  if (!source) return;
  if (isImageElement(source)
      && (!source.complete || source.naturalWidth <= 0 || source.naturalHeight <= 0)) {
    throw new Error('Texture image must be decoded before upload');
  }
  if (isVideoElement(source)
      && (source.readyState < 2 || source.videoWidth <= 0 || source.videoHeight <= 0)) {
    throw new Error('Texture video must have a decoded current frame before upload');
  }
  if (snapshot.dimensions.width <= 0 || snapshot.dimensions.height <= 0) {
    throw new Error('Texture source must have non-zero decoded dimensions');
  }
}

function imageDataSource(source) {
  return typeof ImageData !== 'undefined' && source instanceof ImageData;
}

function imageDataPixels(source, {flipY, premultiplyAlpha}) {
  if (!flipY && !premultiplyAlpha) return source.data;
  const pixels = new Uint8Array(source.data.length);
  for (let y = 0; y < source.height; y++) {
    const sourceY = flipY ? source.height - 1 - y : y;
    for (let x = 0; x < source.width; x++) {
      const from = (sourceY * source.width + x) * 4;
      const to = (y * source.width + x) * 4;
      const alpha = source.data[from + 3];
      const factor = premultiplyAlpha ? alpha / 255 : 1;
      pixels[to] = premultiplyAlpha ? Math.round(source.data[from] * factor) : source.data[from];
      pixels[to + 1] = premultiplyAlpha ? Math.round(source.data[from + 1] * factor) : source.data[from + 1];
      pixels[to + 2] = premultiplyAlpha ? Math.round(source.data[from + 2] * factor) : source.data[from + 2];
      pixels[to + 3] = alpha;
    }
  }
  return pixels;
}

function setTextureParameters(gl, smooth) {
  // QML Image/ShaderEffectSource use smooth filtering by default. Fixtures
  // that intentionally set smooth:false pass textureSmooth:false explicitly.
  const filter = smooth ? gl.LINEAR : gl.NEAREST;
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, filter);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, filter);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
}

function uploadTexture(gl, texture, source, {
  sourceColor = DEFAULT_SOURCE_COLOR,
  flipY = false,
  premultiplyAlpha = true,
  textureSmooth = true,
} = {}) {
  gl.bindTexture(gl.TEXTURE_2D, texture);
  setTextureParameters(gl, textureSmooth);
  // Qt's ShaderEffect texture coordinates address an image from the top-left.
  // WebGL's TexImageSource upload maps its first row to sampler coordinate
  // zero; keep UNPACK_FLIP_Y_WEBGL disabled so these coordinates sample the
  // same top-left row as Qt. Premultiplication matches Qt Quick's scenegraph
  // texture path before shader coverage is applied.
  gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, flipY ? 1 : 0);
  gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, premultiplyAlpha ? 1 : 0);
  if (source == null) {
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE,
                  new Uint8Array(sourceColor));
  } else if (imageDataSource(source)) {
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, source.width, source.height, 0,
                  gl.RGBA, gl.UNSIGNED_BYTE, imageDataPixels(source, {flipY, premultiplyAlpha}));
  } else {
    // This overload accepts HTMLImageElement, ImageBitmap, HTMLCanvasElement,
    // OffscreenCanvas, and other browser TexImageSource implementations.
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, source);
  }
  // Do not leak upload policy into a caller's later texture uploads.
  gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, 0);
  gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, 0);
  gl.bindTexture(gl.TEXTURE_2D, null);
}

function textureStateEqual(state, source, options, snapshot) {
  if (!state || state.source !== source || state.version !== options.version
      || state.flipY !== options.flipY || state.premultiplyAlpha !== options.premultiplyAlpha
      || state.textureSmooth !== options.textureSmooth) {
    return false;
  }
  if (state.dimensions.width !== snapshot.dimensions.width
      || state.dimensions.height !== snapshot.dimensions.height
      || state.sourceURI !== snapshot.sourceURI
      || state.sourceTime !== snapshot.sourceTime) {
    return false;
  }
  if (source == null) return state.sourceColorKey === options.sourceColor.join(',');
  return true;
}

function cloneStats(stats) {
  return {
    programCompiles: stats.programCompiles,
    textureUploads: stats.textureUploads,
    draws: stats.draws,
  };
}

/** Owns a WebGL2 context and all GPU resources used by source shader frames. */
export class SourceRenderer {
  constructor(canvas, contextOptions = {}) {
    this.canvas = canvas;
    this.contextOptions = {
      alpha: false,
      antialias: false,
      depth: false,
      stencil: false,
      preserveDrawingBuffer: true,
      premultipliedAlpha: false,
      ...contextOptions,
    };
    this.gl = canvas.getContext('webgl2', this.contextOptions);
    if (!this.gl) throw new Error('WebGL 2 unavailable');
    this.transparent = this.gl.getContextAttributes()?.alpha === true;
    // Keep generated fixture colors deterministic across WebGL backends.
    this.gl.disable(this.gl.DITHER);
    this.programs = new Map();
    this.texture = this.gl.createTexture();
    this.vao = this.gl.createVertexArray();
    this.buffer = this.gl.createBuffer();
    this.textureState = null;
    this.disposed = false;
    this.stats = {programCompiles: 0, textureUploads: 0, draws: 0};
    this.gl.bindVertexArray(this.vao);
    this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.buffer);
    this.gl.bufferData(this.gl.ARRAY_BUFFER,
      new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), this.gl.STATIC_DRAW);
    this.gl.bindVertexArray(null);
  }

  program(programKey, source) {
    const existing = this.programs.get(programKey);
    if (existing && existing.source === source) return existing;
    const program = programFor(this.gl, source);
    let position;
    try {
      position = this.gl.getAttribLocation(program, 'position');
    } catch (error) {
      this.gl.deleteProgram(program);
      throw error;
    }
    const info = {program, source, position, locations: new Map()};
    if (existing) this.gl.deleteProgram(existing.program);
    this.programs.set(programKey, info);
    this.stats.programCompiles++;
    return info;
  }

  location(info, name) {
    if (!info.locations.has(name)) {
      info.locations.set(name, this.gl.getUniformLocation(info.program, name));
    }
    return info.locations.get(name);
  }

  uniform(info, name, value) {
    const location = this.location(info, name);
    if (location === null) return;
    if (typeof value === 'number') {
      this.gl.uniform1f(location, value);
    } else if (Array.isArray(value) && value.length === 2) {
      this.gl.uniform2f(location, value[0], value[1]);
    } else if (Array.isArray(value) && value.length === 4) {
      this.gl.uniform4f(location, value[0], value[1], value[2], value[3]);
    } else {
      throw new TypeError(`Unsupported uniform ${name}`);
    }
  }

  ensureTexture({textureSource = null, sourceColor = DEFAULT_SOURCE_COLOR,
    textureVersion = 0, textureFlipY = false, premultiplyAlpha = true,
    textureSmooth = true, forceTextureUpload = false} = {}) {
    const snapshot = sourceSnapshot(textureSource);
    assertTextureSourceReady(textureSource, snapshot);
    const options = {
      version: textureVersion,
      flipY: textureFlipY,
      premultiplyAlpha,
      textureSmooth,
      sourceColor,
    };
    if (!forceTextureUpload && textureStateEqual(this.textureState, textureSource, options, snapshot)) return;
    uploadTexture(this.gl, this.texture, textureSource, {
      sourceColor, flipY: textureFlipY, premultiplyAlpha, textureSmooth,
    });
    this.textureState = {
      source: textureSource,
      version: textureVersion,
      flipY: textureFlipY,
      premultiplyAlpha,
      sourceColorKey: sourceColor.join(','),
      dimensions: snapshot.dimensions,
      sourceURI: snapshot.sourceURI,
      sourceTime: snapshot.sourceTime,
      textureSmooth,
    };
    this.stats.textureUploads++;
  }

  render(shaderKey, source, uniforms, options = {}) {
    if (this.disposed) return null;
    const info = this.program(options.programKey || shaderKey, source);
    this.ensureTexture(options);
    const gl = this.gl;
    gl.viewport(0, 0, this.canvas.width, this.canvas.height);
    gl.clearColor(0, 0, 0, this.transparent ? 0 : 1);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.useProgram(info.program);
    gl.bindVertexArray(this.vao);
    gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer);
    if (info.position >= 0) {
      gl.enableVertexAttribArray(info.position);
      gl.vertexAttribPointer(info.position, 2, gl.FLOAT, false, 0, 0);
    }
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.texture);
    const sourceLocation = this.location(info, 'source');
    if (sourceLocation !== null) gl.uniform1i(sourceLocation, 0);
    const opacityLocation = this.location(info, 'qt_Opacity');
    if (opacityLocation !== null) gl.uniform1f(opacityLocation, 1);
    for (const [name, value] of Object.entries(uniforms)) this.uniform(info, name, value);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    const error = gl.getError();
    if (error !== gl.NO_ERROR) throw new Error(`WebGL error ${error}`);
    this.stats.draws++;
    // Live callers keep the persistent canvas and avoid a synchronous PNG
    // readback/encode on every frame. Golden capture is explicit and owned by
    // the offline renderCases helper or a caller that opts into capture.
    return options.capture === true ? this.canvas.toDataURL('image/png') : this.canvas;
  }

  resourceStats() {
    return cloneStats(this.stats);
  }

  dispose() {
    if (this.disposed) return;
    for (const info of this.programs.values()) this.gl.deleteProgram(info.program);
    this.programs.clear();
    this.gl.deleteTexture(this.texture);
    this.gl.deleteBuffer(this.buffer);
    this.gl.deleteVertexArray(this.vao);
    this.textureState = null;
    this.disposed = true;
  }
}

export function renderSourceShader(canvas, source, uniforms, options = {}) {
  const owner = options.renderer || CANVAS_RENDERERS.get(canvas) || new SourceRenderer(canvas);
  if (!options.renderer && !CANVAS_RENDERERS.has(canvas)) CANVAS_RENDERERS.set(canvas, owner);
  const {renderer: _renderer, ...renderOptions} = options;
  return owner.render(options.programKey || source, source, uniforms, renderOptions);
}

export function disposeSourceRenderer(canvas) {
  const owner = CANVAS_RENDERERS.get(canvas);
  if (!owner) return;
  owner.dispose();
  CANVAS_RENDERERS.delete(canvas);
}

/** Create deterministic top-left-origin texture fixtures without screenshots. */
export function createProgrammaticTexture(kind, width = 64, height = 48) {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const context = canvas.getContext('2d');
  if (!context) throw new Error('2D canvas unavailable for source fixture');
  const pixels = context.createImageData(width, height);
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const at = (y * width + x) * 4;
      if (kind === 'gradient') {
        // Match the native probe's three-stop vertical Gradient: black,
        // green at the midpoint, then yellow at the bottom.
        const t = y / (height - 1);
        pixels.data[at] = t <= .5 ? 0 : Math.floor((t * 2 - 1) * 255);
        pixels.data[at + 1] = t <= .5 ? Math.floor(t * 2 * 255) : 255;
        pixels.data[at + 2] = 0;
        pixels.data[at + 3] = 255;
      } else if (kind === 'checker') {
        const light = ((Math.floor(x / (width / 8)) + Math.floor(y / (height / 7))) & 1) === 0;
        pixels.data[at] = light ? 240 : 30;
        pixels.data[at + 1] = light ? 180 : 50;
        pixels.data[at + 2] = light ? 100 : 220;
        pixels.data[at + 3] = 255;
      } else if (kind === 'transparent') {
        pixels.data[at] = 210;
        pixels.data[at + 1] = 80;
        pixels.data[at + 2] = 220;
        pixels.data[at + 3] = Math.floor(x * 255 / (width - 1));
      } else {
        throw new Error(`Unknown programmatic texture fixture: ${kind}`);
      }
    }
  }
  context.putImageData(pixels, 0, 0);
  canvas.dataset.rendererTexture = kind;
  return canvas;
}

// Source shape-catalogue params values used by the reference shell's reveal picker. The
// reveal shader clamps lobes to five in the reference shell; callers use
// sourceRevealUniforms below so reach normalization stays source-derived.
export function sourceRevealUniforms(shapeName, revealReach, spin, width = 320, height = 240) {
  const picked = SOURCE_REVEAL_SHAPES[shapeName];
  if (!picked) throw new Error(`Unknown source reveal shape: ${shapeName}`);
  const shape = [Math.min(picked[0], 5), picked[1], picked[2], picked[3]];
  const reach = Math.max(0, revealReach) * Math.hypot(width, height) / 2
    / (shape[3] > 0.5 ? 1 : 1 - shape[1]) + 2;
  return {itemSize: [width, height], shape, reach, spin};
}

// A small host-side lifecycle wrapper. It owns no autonomous clock: source
// code supplies the state and asks for a frame. This keeps hidden and disposed
// work explicit while preserving source settings semantics.
export class RendererClosureSession {
  constructor(canvas) {
    this.canvas = canvas;
    this.renderer = new SourceRenderer(canvas);
    this.state = {shown: true, reducedMotion: false, performanceMode: false, noShapes: false};
    this.frames = 0;
    this.disposed = false;
  }

  setState(patch) {
    if (!this.disposed) Object.assign(this.state, patch);
  }

  render(shader, source, uniforms, options = {}) {
    if (this.disposed || !this.state.shown) return null;
    const prepared = sourceSettingsUniforms(shader, uniforms, this.state);
    this.frames++;
    return this.renderer.render(shader, source, prepared, options);
  }

  resourceStats() {
    return this.renderer.resourceStats();
  }

  dispose() {
    if (this.disposed) return;
    this.renderer.dispose();
    this.disposed = true;
    this.canvas.width = 0;
    this.canvas.height = 0;
  }
}

export function sourceSettingsUniforms(shader, uniforms, {
  noShapes = false,
} = {}) {
  const next = Object.fromEntries(Object.entries(uniforms).map(([name, value]) => [
    name, Array.isArray(value) ? value.slice() : value,
  ]));
  if (!noShapes) return next;
  if (shader === 'rounded_image') {
    next.waviness = 0;
    next.ringWaves = 0;
    next.ringAmplitude = 0;
    next.ringThickness = 0;
    next.ringColor = [0, 0, 0, 0];
  } else if (shader === 'shape_mask') {
    // the reference shell changes the picked reveal shape to Shapes.params("circle")
    // when noShapes is set: (lobes, depth, sharpness, kind).
    next.shape = [0, 0, 1, 0];
  }
  return next;
}

export async function renderCases(cases, shaders) {
  const output = [];
  const canvas = document.createElement('canvas');
  canvas.width = cases[0]?.width || 1;
  canvas.height = cases[0]?.height || 1;
  canvas.dataset.rendererClosure = 'persistent-case-owner';
  document.body.append(canvas);
  const renderer = new SourceRenderer(canvas);
  const textures = new Map();
  try {
    for (const testCase of cases) {
      canvas.width = testCase.width;
      canvas.height = testCase.height;
      let textureSource = null;
      if (testCase.texture && testCase.texture !== 'solid') {
        if (!textures.has(testCase.texture)) textures.set(testCase.texture,
          createProgrammaticTexture(testCase.texture));
        textureSource = textures.get(testCase.texture);
      }
      const dataUrl = renderer.render(testCase.shader, shaders[testCase.shader], testCase.uniforms, {
        textureSource,
        textureSmooth: testCase.textureSmooth ?? false,
        programKey: testCase.shader,
        capture: true,
      });
      output.push({name: testCase.name, shader: testCase.shader, width: canvas.width,
        height: canvas.height, texture: testCase.texture || 'solid',
        dataUrl, resourceStats: renderer.resourceStats()});
    }
  } finally {
    renderer.dispose();
    for (const texture of textures.values()) texture.width = 0;
    canvas.remove();
  }
  return output;
}

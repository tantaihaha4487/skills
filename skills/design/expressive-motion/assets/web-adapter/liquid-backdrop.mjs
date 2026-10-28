// Source GLSL equations, adapted from Qt's uniform blocks to WebGL 2 uniforms.
// Inputs are supplied by the host. This module does not synthesize audio data.
import {compileShader,loadShaderSources,uniformFields} from './shader-utils.mjs';
const VERTEX = `#version 300 es
in vec2 position;
out vec2 qt_TexCoord0;
void main(){gl_Position=vec4(position,0,1);qt_TexCoord0=vec2(position.x*.5+.5,.5-position.y*.5);}`;
const deleteTargets=(gl,targets)=>targets.forEach(target=>{
  if(target.texture){const texture=target.texture;target.texture=null;gl.deleteTexture(texture);}
  if(target.framebuffer){const framebuffer=target.framebuffer;target.framebuffer=null;gl.deleteFramebuffer(framebuffer);}
});

export function adaptFragment(source) {
  return source.replace('#version 440', '#version 300 es\nprecision highp float;')
    .replace('layout(location = 0) in', 'in')
    .replace(/layout\(std140, binding = 0\) uniform buf \{([\s\S]*?)\};/, (_, fields) => uniformFields(fields))
    .replace(/layout\(binding = 1\) uniform/g, 'uniform')
    .replace(/texture\(source, (uv|qt_TexCoord0)\)/g, 'texture(source, vec2($1.x, 1.0 - $1.y))');
}

export class LiquidBackdrop {
  static async create(canvas, options = {}) {
    const sources = await loadShaderSources(['liquid_backdrop', 'backdrop_blur', 'backdrop_composite']);
    return new LiquidBackdrop(canvas, sources, options);
  }

  constructor(canvas, sources, { now = () => performance.now(), schedule = (callback, delay) => setTimeout(callback, delay), cancel = id => clearTimeout(id) } = {}) {
    this.canvas = canvas;
    this.gl = canvas.getContext('webgl2', { alpha: false, antialias: false, preserveDrawingBuffer: true });
    if (!this.gl) throw Error('WebGL 2 unavailable');
    this.now = now; this.schedule = schedule; this.cancel = cancel;
    this.state = { shown: false, playing: false, reduced: false, living: true, blur: 24,
      palette: [[.086,.302,.161,1],[.083,.267,.149,1],[.604,.929,.718,1],[.11,.36,.22,1],[.04,.1,.07,1]],
      energy: [0,0,0,0], lead: 0 };
    this.held = 0; this.started = null; this.timer = null; this.frames = 0; this.disposed = false;
    const gl = this.gl;
    const vertex = compileShader(gl, gl.VERTEX_SHADER, VERTEX);
    this.programs = sources.map(source => {
      const fragment = compileShader(gl, gl.FRAGMENT_SHADER, adaptFragment(source));
      const program = gl.createProgram(); gl.attachShader(program, vertex); gl.attachShader(program, fragment); gl.linkProgram(program);
      gl.deleteShader(fragment);
      if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw Error(gl.getProgramInfoLog(program));
      return program;
    });
    gl.deleteShader(vertex);
    this.vao = gl.createVertexArray(); gl.bindVertexArray(this.vao);
    this.buffer = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1,1,-1,-1,1,1,1]), gl.STATIC_DRAW);
    this.targets = [];
    this.uniformLocations=this.programs.map(()=>new Map());
    this.positions=this.programs.map(program=>gl.getAttribLocation(program,'position'));
  }

  clockTime() { return this.held + (this.started == null ? 0 : (this.now() - this.started) / 1000); }

  setState(patch) {
    if (this.disposed) return;
    const before = this.clockTime(); Object.assign(this.state, patch);
    const active = this.state.shown && this.state.playing && !this.state.reduced && this.state.living;
    if (this.timer != null) { this.cancel(this.timer); this.timer = null; }
    this.held = before; this.started = active ? this.now() : null;
    if (this.state.shown) this.render();
    else {this.releaseTargets();if(this.canvas.width!==1)this.canvas.width=1;if(this.canvas.height!==1)this.canvas.height=1;}
    if (active) this.tick();
  }

  resetClock() {
    if(this.disposed)return;
    this.held=0;
    this.started=this.state.shown&&this.state.playing&&!this.state.reduced&&this.state.living?this.now():null;
  }

  tick() {
    this.timer = this.schedule(() => {
      this.timer = null;
      if (this.disposed) return;
      this.render(); this.tick();
    }, 33);
  }

  resize(width, height) {
    if (this.disposed) return;
    this.width = Math.max(1, Math.round(width)); this.height = Math.max(1, Math.round(height));
    if (this.state.shown) this.render();
  }

  releaseTargets() {
    const gl=this.gl;
    deleteTargets(gl,this.targets);
    this.targets=[];this.textureWidth=0;this.textureHeight=0;
  }

  allocate(width, height) {
    const gl = this.gl;
    if (this.textureWidth === width && this.textureHeight === height && this.targets.length === 3) return;
    const previousTargets=this.targets,nextTargets=[];
    try {
      for(let i=0;i<3;i++){
        const target={texture:null,framebuffer:null};nextTargets.push(target);
        target.texture=gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, target.texture);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA8, width, height, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
        target.framebuffer=gl.createFramebuffer(); gl.bindFramebuffer(gl.FRAMEBUFFER, target.framebuffer);
        gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, target.texture, 0);
        if (gl.checkFramebufferStatus(gl.FRAMEBUFFER) !== gl.FRAMEBUFFER_COMPLETE) throw Error('Incomplete backdrop framebuffer');
      }
    }catch(error){
      deleteTargets(gl,nextTargets);
      throw error;
    }
    this.targets=nextTargets;this.textureWidth=width;this.textureHeight=height;
    deleteTargets(gl,previousTargets);
  }

  render({ time } = {}) {
    if (this.disposed || !this.width) return;
    const gl = this.gl, s = this.state;
    if(this.canvas.width!==this.width)this.canvas.width=this.width;
    if(this.canvas.height!==this.height)this.canvas.height=this.height;
    const scale = s.blur > 2 ? Math.max(1/8, 2/s.blur) : 1;
    const width = Math.max(1, Math.ceil(this.width * scale)), height = Math.max(1, Math.ceil(this.height * scale));
    this.allocate(width, height);
    const flows = !s.reduced && s.living;
    const fieldTime = time ?? (flows ? this.clockTime() : 37);
    this.lastTime = fieldTime;
    gl.bindVertexArray(this.vao);
    for (let pass = 0; pass < 4; pass++) {
      const programIndex=pass===0?0:pass===3?2:1,program=this.programs[programIndex];
      gl.useProgram(program);
      const position = this.positions[programIndex]; gl.enableVertexAttribArray(position); gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);
      const locations=this.uniformLocations[programIndex];
      const uniform=name=>{if(!locations.has(name))locations.set(name,gl.getUniformLocation(program,name));return locations.get(name);};
      gl.uniform1f(uniform('qt_Opacity'), 1);
      gl.bindFramebuffer(gl.FRAMEBUFFER, pass === 3 ? null : this.targets[pass].framebuffer);
      gl.viewport(0, 0, pass === 3 ? this.width : width, pass === 3 ? this.height : height);
      if (pass === 0) {
        gl.uniform2f(uniform('itemSize'), this.width, this.height); gl.uniform1f(uniform('time'), fieldTime);
        gl.uniform4fv(uniform('energy'), flows && s.playing && s.shown ? s.energy : [0,0,0,0]);
        gl.uniform1f(uniform('lead'), flows && s.playing && s.shown ? s.lead : 0);
        for (let i = 0; i < 5; i++) gl.uniform4fv(uniform(`c${i}`), s.palette[i % s.palette.length]);
      } else {
        gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, this.targets[pass - 1].texture); gl.uniform1i(uniform('source'), 0);
        if (pass < 3) { gl.uniform1f(uniform('sigma'), s.blur * scale); gl.uniform2f(uniform('texelStep'), pass === 1 ? 1/width : 0, pass === 2 ? 1/height : 0); }
      }
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    }
    this.frames++;
    const error = gl.getError(); if (error !== gl.NO_ERROR) throw Error(`WebGL error ${error}`);
  }

  dispose() {
    if (this.disposed) return;
    if (this.timer != null) this.cancel(this.timer);
    this.timer = null; this.disposed = true;
    const gl = this.gl;
    this.releaseTargets();
    this.programs.forEach(p => gl.deleteProgram(p)); gl.deleteBuffer(this.buffer); gl.deleteVertexArray(this.vao);
  }
}

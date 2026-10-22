// SpectrumStyle/SpectrumShaping/SpectrumItem source port. The host supplies
// analysis bands; these functions never invent a live audio stream.
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const mix=(a,b,t)=>a+(b-a)*t;
const f=Math.fround;
export function spectrumStyle(kind='compact',height=34,wave=false){
  const s={count:6,layout:0,spacing:2.6,minimumHeight:Math.min(4,Math.max(2,height*.2)),baseLevel:.08,levelScale:.92,responseExponent:1,alignment:0,glowOpacity:.32,glowRadius:2,symmetricGradient:false,bassRangeFalloff:0,radial:false,innerRadiusRatio:.66,gapRatio:.032,haloOpacity:0,haloBlur:.035,drawsBars:true,riseDuration:.025,animationDuration:.075,inactiveOpacity:.45};
  if(kind!=='compact')Object.assign(s,{count:24,layout:1,spacing:2.5,minimumHeight:3,baseLevel:.02,levelScale:1.12,responseExponent:1.1,alignment:1,glowOpacity:.48,glowRadius:5,symmetricGradient:true,bassRangeFalloff:.12,riseDuration:.016,animationDuration:.045,inactiveOpacity:.4});
  if(kind==='equalizer')Object.assign(s,{count:40,layout:2,glowOpacity:.85,glowRadius:9,symmetricGradient:false});
  if(kind==='ring')Object.assign(s,{count:36,spacing:2,minimumHeight:2,glowOpacity:.5,glowRadius:4,radial:true});
  if(wave&&kind!=='compact'&&kind!=='equalizer')Object.assign(s,{haloOpacity:1,haloBlur:.014,drawsBars:false});
  return Object.fromEntries(Object.entries(s).map(([key,value])=>[key,typeof value==='number'?f(value):value]));
}
export function bassExpanded(levels,count){
  if(!levels.length||count<=0)return[];
  const a=f(.46),b=f(.30),last=levels.length-1,positions=Array.from({length:count},(_,i)=>{const p=count===1?0:f(i/(count-1));return f((p<=a?f(f(p/a)*b):f(b+f(f(f(p-a)/f(1-a))*f(1-b))))*last);});
  const at=p=>{const lo=clamp(Math.floor(p),0,last),hi=Math.min(lo+1,last),blend=f(p-lo);return clamp(f(f(levels[lo]*f(1-blend))+f(levels[hi]*blend)));};
  return positions.map((p,i)=>{const lo=i===0?0:f(f(positions[i-1]+p)/2),hi=i===count-1?last:f(f(p+positions[i+1])/2);if(f(hi-lo)<=1)return at(p);let peak=Math.max(at(lo),at(hi));for(let n=Math.ceil(lo);n<=Math.floor(hi);n++)peak=Math.max(peak,levels[n]);return clamp(peak);});
}
export function compactLevels(levels,count){
  return Array.from({length:Math.max(0,count)},(_,i)=>{if(!levels.length)return 0;const lo=Math.floor(i*levels.length/count),hi=Math.min(Math.max(lo+1,Math.floor((i+1)*levels.length/count)),levels.length);let peak=0,squares=0;for(let n=lo;n<hi;n++){peak=Math.max(peak,levels[n]);squares=f(squares+f(levels[n]*levels[n]));}return clamp(f(f(f(Math.sqrt(f(squares/Math.max(hi-lo,1))))*f(.72))+f(peak*f(.28))));});
}
export function spectrumTargets(input,style,active=true){
  const levels=Array.from({length:48},(_,i)=>Number.isFinite(input[i])?f(clamp(input[i])):0);
  let mapped=!active?Array(style.layout===1?style.count*2:style.count).fill(0):style.layout===0?compactLevels(levels,style.count):bassExpanded(levels,style.count);
  if(active&&style.layout===1)mapped=[...mapped,...mapped.toReversed()];
  return mapped.map(x=>clamp(f(style.baseLevel+f(style.levelScale*f(x**style.responseExponent)))));
}
export function advanceSpectrum(levels,targets,velocities,seconds,style,active=true){
  const dt=f(clamp(seconds,1/240,1/15)),next=[],speed=[];
  for(let i=0;i<levels.length;i++){const difference=f(targets[i]-levels[i]);let velocity=0,value;
    if(!active&&difference<0){velocity=f((velocities[i]||0)+f(8*dt));value=Math.max(targets[i],f(levels[i]-f(velocity*dt)));}
    else value=f(levels[i]+f(difference*f(1-f(Math.exp(f(-dt/Math.max(difference>0?style.riseDuration:style.animationDuration,f(.005))))))));
    if(Math.abs(f(targets[i]-value))<f(.0005)){value=targets[i];velocity=0;}next.push(value);speed.push(velocity);
  }return{levels:next,velocities:speed,moving:next.some((v,i)=>Math.abs(v-targets[i])>=.0005)};
}

const curve=(points,closed=false)=>{
  const at=i=>points[closed?(i%points.length+points.length)%points.length:clamp(i,0,points.length-1)],out=[];
  for(let segment=0;segment<(closed?points.length:points.length-1);segment++){const p0=at(segment-1),p1=at(segment),p2=at(segment+1),p3=at(segment+2);for(let step=0;step<8;step++){const t=step/8,u=1-t;out.push([0,1].map(k=>u**3*p1[k]+3*u*u*t*(p1[k]+(p2[k]-p0[k])/6)+3*u*t*t*(p2[k]-(p3[k]-p1[k])/6)+t**3*p2[k]));}}
  if(!closed)out.push(points.at(-1));return out;
};
export function spectrumGeometry(width,height,levels,style,palette=[[1,61/255,138/255,1],[214/255,36/255,108/255,1]]){
  const bars=[],barIndices=[],halo=[],haloIndices=[],count=levels.length;
  const colors=levels.map((_,i)=>{const p=count<=1?0:i/(count-1),t=style.symmetricGradient?1-Math.abs(p*2-1):p;return palette[0].map((v,k)=>mix(v,(palette[1]||palette[0])[k],t));});
  const packed=(c,alpha)=>c.slice(0,3).map(v=>Math.round(v*clamp(alpha)*255)/255).concat(Math.round(clamp(alpha)*255)/255);
  const range=i=>1-style.bassRangeFalloff*Math.min(style.layout===1?Math.min(i,count-1-i)/Math.max(count/2-1,1):i/Math.max(count-1,1),1);
  const appendBar=(x,y,dx,dy,w,h,tip,foot,color)=>{const base=bars.length,margin=style.glowRadius*3+1;for(let n=0;n<4;n++){const lx=(n&1?1:-1)*(w*.5+margin),ly=-margin+(h+2*margin)*(n&2?1:0);bars.push([x+dy*lx+dx*ly,y-dx*lx+dy*ly,lx,ly,...color,w,h,tip,foot]);}barIndices.push(base,base+1,base+2,base+1,base+3,base+2);};
  const feather=(points,inward,colors,sigma)=>{const base=halo.length;for(let i=0;i<points.length;i++)for(let n=0;n<5;n++){const offset=[-2,-1,0,1,2][n]*sigma;halo.push([points[i][0]-inward[i][0]*offset,points[i][1]-inward[i][1]*offset,...packed(colors[i],colors[i][3]*[.977,.841,.5,.159,.023][n]*style.haloOpacity)]);}for(let i=0;i<points.length-1;i++)for(let n=0;n<4;n++){const a=base+i*5+n,b=a+5;haloIndices.push(a,b,a+1,a+1,b,b+1);}};
  if(!style.radial){
    const spacing=Math.min(style.spacing,Math.max(0,(width-count)/Math.max(count-1,1))),barWidth=Math.max(0,width-spacing*(count-1))/count;
    const heights=levels.map((v,i)=>Math.min(height,Math.max(style.minimumHeight,barWidth,height*v*range(i))));
    if(style.haloOpacity>0&&style.alignment===1){
      const spread=height*.04,sigma=Math.max(.75,height*style.haloBlur),tips=heights.map((h,i)=>[i*(barWidth+spacing)+barWidth/2,height-Math.min(height,h+spread)]);tips.unshift([0,tips[0][1]]);tips.push([width,tips.at(-1)[1]]);
      const points=curve(tips),cs=points.map(p=>{const v=clamp((p[0]-barWidth/2)/(barWidth+spacing),0,count-1),lo=Math.floor(v),hi=Math.min(lo+1,count-1);return colors[lo].map((c,k)=>mix(c,colors[hi][k],v-lo));});
      for(let i=0;i<points.length;i++){const color=packed(cs[i],cs[i][3]*style.haloOpacity);halo.push([points[i][0],points[i][1]+2*sigma,...color],[points[i][0],height+spread+3*sigma,...color]);}
      for(let i=0;i<points.length-1;i++){const n=i*2;haloIndices.push(n,n+1,n+2,n+2,n+1,n+3);}feather(points,points.map(()=>[0,1]),cs,sigma);
    }
    if(style.drawsBars)for(let i=0;i<count;i++)appendBar(i*(barWidth+spacing)+barWidth/2,style.alignment===0?(height-heights[i])/2:height,0,style.alignment===0?1:-1,barWidth,heights[i],Math.min(barWidth,heights[i])/2,Math.min(barWidth,heights[i])/2,colors[i]);
  }else{
    const edge=Math.min(width,height),inner=edge/2*style.innerRadiusRatio,w=Math.max(1.5,2*Math.PI*inner/count-style.spacing),restCircle=inner+edge/2*style.gapRatio,footCircle=inner*.8,hidden=restCircle-footCircle,maximum=Math.max(1,edge/2-restCircle),resting=Math.max(style.minimumHeight,w,maximum*.18),travel=Math.max(0,maximum-resting),radii=[];
    for(let i=0;i<count;i++){const length=hidden+resting+travel*levels[i]*range(i),theta=-Math.PI/2+2*Math.PI*(i+.5)/count,dx=Math.cos(theta),dy=Math.sin(theta);radii.push(footCircle+length+edge/2*.05);if(style.drawsBars)appendBar(width/2+dx*footCircle,height/2+dy*footCircle,dx,dy,w,length,w/2,Math.min(2,w*.3),colors[i]);}
    if(style.haloOpacity>0){
      let smooth=radii;for(let pass=0;pass<2;pass++)smooth=smooth.map((v,i)=>(smooth[(i+count-1)%count]+2*v+smooth[(i+1)%count])/4);
      const sigma=Math.max(.75,edge/2*style.haloBlur),points=count*8,rings=[];
      for(let i=0;i<=points;i++){const segment=Math.floor(i/8)%count,t=(i%8)/8,[r0,r1,r2,r3]=[-1,0,1,2].map(d=>smooth[(segment+d+count)%count]);const radius=.5*(2*r1+(r2-r0)*t+(2*r0-5*r1+4*r2-r3)*t*t+(3*r1-r0-3*r2+r3)*t*t*t),theta=-Math.PI/2+2*Math.PI*((i%points)+4)/points,p=(i%points)/points*count,lo=Math.floor(p)%count,hi=(lo+1)%count,color=colors[lo].map((v,k)=>mix(v,colors[hi][k],p-Math.floor(p)));rings.push({radius,dx:Math.cos(theta),dy:Math.sin(theta),color});}
      const vertex=(i,radius,coverage)=>{const r=rings[i];halo.push([width/2+r.dx*radius,height/2+r.dy*radius,...packed(r.color,r.color[3]*coverage*style.haloOpacity)]);};
      halo.push([width/2,height/2,...packed(rings[0].color,rings[0].color[3]*style.haloOpacity)]);for(let i=0;i<=points;i++)vertex(i,rings[i].radius-2*sigma,1);for(let i=0;i<points;i++)haloIndices.push(0,i+1,i+2);
      const base=halo.length;for(let i=0;i<=points;i++)for(let n=0;n<5;n++)vertex(i,rings[i].radius+[-2,-1,0,1,2][n]*sigma,[.977,.841,.5,.159,.023][n]);
      for(let i=0;i<points;i++)for(let n=0;n<4;n++){const a=base+i*5+n,b=a+5;haloIndices.push(a,b,a+1,a+1,b,b+1);}
    }
  }
  return{bars,barIndices,halo,haloIndices};
}

export class SpectrumRenderer{
  static async create(canvas){const fragments=await Promise.all(['spectrum_bars','spectrum_halo'].map(async name=>(await fetch(new URL(`./assets/source-shaders/${name}.frag`,import.meta.url))).text()));return new SpectrumRenderer(canvas,fragments);}
  constructor(canvas,fragments){
    this.canvas=canvas;this.gl=canvas.getContext('webgl2',{alpha:false,antialias:false,preserveDrawingBuffer:true});if(!this.gl)throw Error('WebGL2 unavailable');const gl=this.gl;
    const uniform=`uniform vec2 viewport;out vec2 vItem;void place(vec2 p){vItem=p;gl_Position=vec4(p.x/viewport.x*2.-1.,1.-p.y/viewport.y*2.,0,1);}`;
    const vertices=[`#version 300 es\nin vec2 position;in vec2 local;in vec4 color;in vec4 shape;out vec2 vLocal;flat out vec4 vColor;flat out vec4 vShape;${uniform}void main(){vLocal=local;vColor=color;vShape=shape;place(position);}`,`#version 300 es\nin vec2 position;in vec4 color;out vec4 vColor;${uniform}void main(){vColor=color;place(position);}`];
    const compile=(type,text)=>{const s=gl.createShader(type);gl.shaderSource(s,text);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;};
    this.programs=fragments.map((source,i)=>{const fragment=source.replace('#version 440','#version 300 es\nprecision highp float;').replace(/layout\(location = \d+\) (flat )?in/g,'$1in').replace(/layout\(std140, binding = 0\) uniform buf \{([\s\S]*?)\};/,(_,fields)=>fields.replace(/\/\/[^\n]*/g,'').split(';').map(x=>x.trim()).filter(Boolean).map(x=>`uniform ${x};`).join('\n'));const a=compile(gl.VERTEX_SHADER,vertices[i]),b=compile(gl.FRAGMENT_SHADER,fragment),p=gl.createProgram();gl.attachShader(p,a);gl.attachShader(p,b);gl.linkProgram(p);gl.deleteShader(a);gl.deleteShader(b);if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(p));return p;});
    this.uniforms=this.programs.map(p=>new Map());
    this.vao=gl.createVertexArray();this.buffer=gl.createBuffer();this.indices=gl.createBuffer();
  }
  render({width,height,levels,kind='compact',wave=false,palette,cut=[0,0,0,0],cutWave=[0,0,0,0]}){
    if(this.disposed)return;const s=spectrumStyle(kind,height,wave),mesh=spectrumGeometry(width,height,levels,s,palette),gl=this.gl;if(this.canvas.width!==width)this.canvas.width=width;if(this.canvas.height!==height)this.canvas.height=height;gl.viewport(0,0,width,height);gl.disable(gl.DITHER);gl.clearColor(18/255,18/255,18/255,1);gl.clear(gl.COLOR_BUFFER_BIT);gl.enable(gl.BLEND);gl.blendFunc(gl.ONE,gl.ONE_MINUS_SRC_ALPHA);gl.bindVertexArray(this.vao);
    for(const type of ['halo','bars']){const data=mesh[type],indices=mesh[type==='bars'?'barIndices':'haloIndices'];if(!data.length)continue;const program=this.programs[type==='bars'?0:1];gl.useProgram(program);const cache=this.uniforms[type==='bars'?0:1];const u=name=>{if(!cache.has(name))cache.set(name,gl.getUniformLocation(program,name));return cache.get(name);};gl.uniform2f(u('viewport'),width,height);gl.uniform1f(u('qt_Opacity'),1);gl.uniform1f(u('pixelsPerPoint'),1);gl.uniform1f(u('glowSigma'),s.glowRadius);gl.uniform1f(u('glowOpacity'),s.glowOpacity);gl.uniform4fv(u('cut'),cut);gl.uniform4fv(u('wave'),cutWave);
      gl.bindBuffer(gl.ARRAY_BUFFER,this.buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(data.flat()),gl.DYNAMIC_DRAW);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,this.indices);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint16Array(indices),gl.DYNAMIC_DRAW);const stride=(type==='bars'?12:6)*4;for(const[name,size,offset]of(type==='bars'?[['position',2,0],['local',2,8],['color',4,16],['shape',4,32]]:[['position',2,0],['color',4,8]])){const location=gl.getAttribLocation(program,name);if(location<0)continue;gl.enableVertexAttribArray(location);gl.vertexAttribPointer(location,size,gl.FLOAT,false,stride,offset);}gl.drawElements(gl.TRIANGLES,indices.length,gl.UNSIGNED_SHORT,0);
    }const error=gl.getError();if(error)throw Error(`Spectrum WebGL error ${error}`);return mesh;
  }
  dispose(){if(this.disposed)return;this.disposed=true;const gl=this.gl;this.programs.forEach(p=>gl.deleteProgram(p));gl.deleteBuffer(this.buffer);gl.deleteBuffer(this.indices);gl.deleteVertexArray(this.vao);}
}

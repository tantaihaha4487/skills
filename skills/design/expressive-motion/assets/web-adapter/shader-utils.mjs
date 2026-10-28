export function uniformFields(fields){
  return fields.replace(/\/\/[^\n]*/g,'').split(';').map(field=>field.trim()).filter(Boolean).map(field=>`uniform ${field};`).join('\n');
}

export function compileShader(gl, kind, source, fallback) {
  const shader = gl.createShader(kind);
  try {
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      const log = gl.getShaderInfoLog(shader);
      throw new Error(log || fallback);
    }
    return shader;
  } catch (error) {
    gl.deleteShader(shader);
    throw error;
  }
}

export async function loadShaderSources(names, requireOk = true){
  return Promise.all(names.map(async name=>{
    const response=await fetch(new URL(`./assets/source-shaders/${name}.frag`,import.meta.url));
    if(requireOk ? !response.ok : response.ok===false)throw Error(`Cannot load source shader ${name}`);
    return response.text();
  }));
}

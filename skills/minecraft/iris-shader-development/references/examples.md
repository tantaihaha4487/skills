# Minimal examples

## Fullscreen pass

A composite fragment shader reads a color buffer and writes exactly one target:

```glsl
#version 330 compatibility
uniform sampler2D colortex0;
in vec2 texcoord;
/* RENDERTARGETS: 0 */
layout(location = 0) out vec4 color;

void main() {
    color = texture(colortex0, texcoord);
}
```

For a new effect, first prove this pass loads, then change only the color expression. Keep the matching fullscreen vertex shader from the chosen template.

## Grayscale change

```glsl
vec4 color = texture(colortex0, texcoord);
float gray = dot(color.rgb, vec3(1.0 / 3.0));
color.rgb = vec3(gray);
```

This is deliberately simple: use it as a load/compile smoke test before adding depth, temporal state, or multiple render targets.

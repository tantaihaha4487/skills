#version 440
// one direction of the backdrop's gaussian blur, run on the small texture.
// beyond the edge it reads the dark ground, as the mac blur does when it
// softens the field into the black behind it.

layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;

layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    // one texel along the blur's direction
    vec2 texelStep;
    // the standard deviation, in texels
    float sigma;
};

layout(binding = 1) uniform sampler2D source;

const vec4 ground = vec4(0.009, 0.009, 0.012, 1.0);
const int reach = 6;

vec4 tap(vec2 uv)
{
    vec2 inside = step(vec2(0.0), uv) * step(uv, vec2(1.0));
    return mix(ground, texture(source, uv), inside.x * inside.y);
}

void main()
{
    if (sigma < 0.05) {
        fragColor = tap(qt_TexCoord0) * qt_Opacity;
        return;
    }
    float spread = -0.5 / (sigma * sigma);
    vec4 total = tap(qt_TexCoord0);
    float weights = 1.0;
    for (int i = 1; i <= reach; i++) {
        float weight = exp(float(i * i) * spread);
        vec2 offset = texelStep * float(i);
        total += weight * (tap(qt_TexCoord0 + offset) + tap(qt_TexCoord0 - offset));
        weights += 2.0 * weight;
    }
    fragColor = total / weights * qt_Opacity;
}

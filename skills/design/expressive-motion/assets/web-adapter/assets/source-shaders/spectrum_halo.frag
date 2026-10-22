#version 440
// the halo or wave, its colours already premultiplied, cut along a round
// cover's squiggle line as the bars are (spectrum_bars.frag)

layout(location = 0) in vec4 vColor;
layout(location = 1) in vec2 vItem;

layout(location = 0) out vec4 fragColor;

layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    vec4 cut;
    vec4 wave;
};

float outsideTheLine(vec2 point)
{
    if (wave.z < 0.5) {
        return 1.0;
    }
    vec2 p = point - cut.xy;
    float angle = wave.x * atan(p.x, -p.y) - wave.y;
    float curve = cut.z + cut.w * sin(angle);
    float slope = cut.w * wave.x * cos(angle) / max(curve, 1.0);
    return clamp((length(p) - curve) / sqrt(1.0 + slope * slope) + 0.5, 0.0, 1.0);
}

void main()
{
    fragColor = vColor * (qt_Opacity * outsideTheLine(vItem));
}

#version 440
// the immersive player seen through a material shape that grows from the
// window's centre (material_shape.frag's shapes, as a mask over a texture).

layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;

layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    vec2 itemSize;
    // (lobes, depth, sharpness, kind), as in material_shape.frag
    vec4 shape;
    // the shape's outermost reach, in pixels
    float reach;
    // radians
    float spin;
};

layout(binding = 1) uniform sampler2D source;

float edgeAt(float theta)
{
    if (shape.w > 0.5) {
        float c = pow(abs(cos(theta)), shape.z);
        float s = pow(abs(sin(theta)), shape.z);
        return reach / pow(c + s, 1.0 / shape.z);
    }
    float lobe = pow(0.5 + 0.5 * cos(shape.x * theta), shape.z);
    return reach * (1.0 - shape.y + shape.y * lobe);
}

void main()
{
    vec2 p = qt_TexCoord0 * itemSize - 0.5 * itemSize;
    float r = length(p);
    float theta = atan(p.y, p.x) - spin;
    const float nudge = 0.002;
    float slope = (edgeAt(theta + nudge) - edgeAt(theta - nudge)) / (2.0 * nudge);
    float d = (r - edgeAt(theta)) / sqrt(1.0 + pow(slope / max(r, 1.0), 2.0));
    fragColor = texture(source, qt_TexCoord0) * (clamp(0.5 - d, 0.0, 1.0) * qt_Opacity);
}

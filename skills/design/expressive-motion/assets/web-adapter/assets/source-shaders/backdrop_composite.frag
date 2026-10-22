#version 440
// the blurred field brought up to full size: a little more saturation, the
// shade that darkens the top and more so the bottom, and the black wash over
// all of it (ArtworkBackdrop's overlays), dithered so the dark gradients do
// not band once stretched.

layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;

layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
};

layout(binding = 1) uniform sampler2D source;

float dither(vec2 pixel)
{
    return fract(52.9829189 * fract(dot(pixel, vec2(0.06711056, 0.00583715)))) - 0.5;
}

void main()
{
    vec3 rgb = texture(source, qt_TexCoord0).rgb;
    float luma = dot(rgb, vec3(0.2126, 0.7152, 0.0722));
    rgb = clamp(mix(vec3(luma), rgb, 1.08), 0.0, 1.0);

    float y = qt_TexCoord0.y;
    float shade = y < 0.5 ? mix(0.26, 0.0, y * 2.0) : mix(0.0, 0.46, y * 2.0 - 1.0);
    rgb *= (1.0 - shade) * 0.8;
    rgb += dither(gl_FragCoord.xy) / 255.0;

    fragColor = vec4(rgb, 1.0) * qt_Opacity;
}

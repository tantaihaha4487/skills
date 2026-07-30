# shaders.properties and Iris features

`shaders/shaders.properties` controls user options and internal pipeline behavior.

## User-facing options

Use `screen` to group options, `sliders` for continuous values, `profile` for presets, and `.lang` files for labels/tooltips. Give expensive effects an obvious quality option and a safe default.

Example pattern:

```properties
screen = BLOOM BLOOM_STRENGTH
sliders = BLOOM_STRENGTH
profile.LOW = BLOOM false
profile.HIGH = BLOOM true BLOOM_STRENGTH 0.8
```

Shader option macros are injected into shader compilation; keep option names stable and do not confuse them with GLSL `#define` directives in this file.

## Internal directives

Useful directives include `iris.features.required`, `iris.features.optional`, `shadow.enabled`, `shadowTerrain`, `shadowEntities`, `particles.ordering`, `separateEntityDraws`, `program.enabled`, `size.buffer.*`, `scale`, `flip`, `blend`, `alphaTest`, and culling controls. Verify spelling and availability against current Iris docs.

Require a feature only when the pack cannot work without it. Prefer optional features with a fallback for portability.

Common feature flags include `COMPUTE_SHADERS`, `SSBO`, `CUSTOM_IMAGES`, `REVERSED_CULLING`, and `TESSELLATION_SHADERS`. Feature names and support vary by Iris release; do not hardcode a version claim without checking the current reference.

## Custom data

Use custom uniforms for CPU-derived values, custom textures/images for extra textures, and SSBOs only when their complexity and hardware boundary are justified. Document required flags, buffer formats, resolution scaling, and fallback behavior near the relevant option.

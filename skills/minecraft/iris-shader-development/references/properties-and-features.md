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

Shader options inject compile-time macros; keep option names stable; do not put GLSL `#define` here.

## Internal directives

Useful directives include `iris.features.required`, `iris.features.optional`, `shadow.enabled`, `shadowTerrain`, `shadowEntities`, `particles.ordering`, `separateEntityDraws`, `program.enabled`, `size.buffer.*`, `scale`, `flip`, `blend`, `alphaTest`, and culling controls. Verify spelling and availability against current Iris docs.

Require features only when essential; prefer optional flags with fallbacks.

Common flags include `COMPUTE_SHADERS`, `SSBO`, `CUSTOM_IMAGES`, `REVERSED_CULLING`, and `TESSELLATION_SHADERS`; names/support vary by Iris release, so check the current reference before claims.

## Custom data

Use custom uniforms for CPU-derived values, custom textures/images for extra textures, and SSBOs only when complexity and hardware boundaries justify them. Document required flags, buffer formats, resolution scaling, and fallback behavior near the relevant option.

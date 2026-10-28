---
name: iris-shader-development
description: "Create, modify, debug, optimize, and package Minecraft Java shader packs for Iris/Sodium. Use for GLSL (.vsh/.fsh/.gsh/.csh/.tcs/.tes), gbuffers/shadows/deferred/composite/final, compute work groups/feature flags, tessellation/TESSELLATION_SHADERS, shaders.properties, uniforms/buffers/render targets, OptiFine compatibility, compile errors, and GPU performance."
---

# Iris Shader Development

Develop version-aware GPU shader packs, not isolated GLSL snippets. Keep the pack loadable, explicit about Iris-only features, compatible with Sodium's rendering path, and measurable for performance.

## Required workflow

1. **Discover** the target Minecraft version, Iris and Sodium versions, loader (Fabric or NeoForge), GPU/OpenGL capability, existing pack/template, requested visual effect, OptiFine compatibility requirement, and performance target. Never infer compatibility from filenames or current memory.
2. **Inspect** the repository or pack structure, local instructions, existing includes, `shaders.properties`, program names, and license before editing. Preserve unrelated changes and authored conventions.
3. **Choose the narrowest pass** with [Iris pipeline](references/iris-pipeline.md); verify and record its stage, feature, work-group, and hardware constraints.
4. **Baseline** on a version-matched known-good template (such as shaderLABS Base-330 with `#version 330 compatibility` for Minecraft 1.17+), then make one coherent change at a time.
5. **Implement explicitly**: declare uniforms/buffer reads, use `RENDERTARGETS`, keep options/feature flags in `shaders.properties`, and reuse includes instead of duplicating GLSL.
6. **Validate in risk order**: shader load/compile, patched source, terrain/cutout/entities/water/particles/weather/hand, day/night/rain/Nether/End, resize/reload, then performance. Do not claim runtime support from syntax inspection alone.
7. **Package** only after testing. The ZIP root must contain `shaders/`; include license and concise usage notes when distributing.

## Buffer-format rule

Iris reads `const int <bufferName>Format = <format>;` directives from GLSL files, not `shaders.properties`. Format names are not GLSL, so put each directive on its own line in a block comment:

```glsl
/*
const int colortex0Format = RGBA16F;
*/
```

Other formats include `RGBA8`, `R11F_G11F_B10F`, and `RGB16F`; Iris also accepts manually defined format tokens. Never use `//` comments. Before packaging, search all shader sources for `const int *Format` assignments and verify directives against current Iris syntax.

## Compatibility rules

- Before compatibility claims, load [compatibility and tooling](references/compatibility-and-tooling.md), record exact target versions, and verify loader/mod boundaries. Never call Iris-only features OptiFine-compatible.
- Avoid names reserved by Iris patching, including `iris_`, `irisMain`, and `moj_import`.
- For transformed-source errors, load [debugging and performance](references/debugging-and-performance.md).

## Reference routing

Load only what the task needs:

- [Iris pipeline](references/iris-pipeline.md): programs, stages, gbuffers, pass selection.
- [Uniforms and buffers](references/uniforms-and-buffers.md): uniforms, depth/color/shadow buffers, outputs.
- [Properties and features](references/properties-and-features.md): options, profiles, flags, ordering, render directives.
- [Debugging and performance](references/debugging-and-performance.md): patched source, diagnosis, profiling, optimization.
- [Compatibility and tooling](references/compatibility-and-tooling.md): version matrix, Sodium/mod boundaries, templates, editors, authoritative links.
- [Examples](references/examples.md): minimal fullscreen and grayscale packs for smoke tests or illustrations.

## Output expectations

When implementing/reviewing a shader change, report target matrix, affected passes/files, compatibility boundary, visual behavior, actual validation, measured/unmeasured performance, and remaining risks. Keep changes minimal; never fabricate GPU/runtime results.

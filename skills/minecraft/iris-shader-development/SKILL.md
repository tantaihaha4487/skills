---
name: iris-shader-development
description: Create, modify, debug, optimize, and package Minecraft Java shader packs for Iris with Sodium. Use for Iris/OptiFine shader pipelines, GLSL .vsh/.fsh/.gsh/.csh/.tcs/.tes files, gbuffers, shadows, deferred/composite/final passes, shaders.properties, uniforms, buffers, render targets, Iris feature flags, Sodium compatibility, shader compile errors, and GPU performance tuning.
---

# Iris Shader Development

Develop shader packs as version-aware GPU software, not as isolated GLSL snippets. Keep the pack loadable, explicit about Iris-only features, compatible with Sodium's rendering path, and measurable for performance.

## Required workflow

1. **Discover** the target Minecraft version, Iris and Sodium versions, loader (Fabric or NeoForge), GPU/OpenGL capability, existing pack/template, requested visual effect, OptiFine compatibility requirement, and performance target. Never infer compatibility from a filename or current memory.
2. **Inspect** the repository or pack structure, local instructions, existing includes, `shaders.properties`, program names, and license before editing. Preserve unrelated changes and authored conventions.
3. **Choose the narrowest pass**: use gbuffers for geometry/material changes, `shadow` for shadow-map inputs, `deferred` for lighting between opaque and translucent geometry, `composite` for fullscreen effects, `final` for final output, and compute only when it materially improves the design.
4. **Establish a baseline** with a known-good template such as shaderLABS Base-330 for Minecraft 1.17+ and `#version 330 compatibility`, then make one coherent change at a time.
5. **Implement explicitly**: declare uniforms and buffer reads, use `RENDERTARGETS` for outputs, keep feature flags and options in `shaders.properties`, and use includes for reusable GLSL rather than duplicating logic.
6. **Validate in risk order**: shader load/compile, patched source, terrain/cutout/entities/water/particles/weather/hand, day/night/rain/Nether/End, resize/reload, then performance. Do not claim runtime support from syntax inspection alone.
7. **Package** only after testing. The ZIP root must contain the pack directory with `shaders/` at the expected level; include license and concise usage notes when distributing.

## Pass selection

- **gbuffers**: actual Minecraft geometry; start with the specific program and rely on documented fallbacks.
- **shadow**: render the light-view shadow map; keep shadow terrain/entity choices explicit.
- **deferred**: opaque lighting before translucent passes.
- **composite/deferred/final**: fullscreen post-processing and buffer-based effects.
- **compute**: Iris-supported `.csh` stages for image/SSBO work; declare required feature flags and work groups.
- **tessellation**: only gbuffers-style passes; require `TESSELLATION_SHADERS` and document the hardware boundary.

## Compatibility rules

- Treat Iris documentation at https://shaders.properties/current/ as the source of truth for current behavior; use ShaderDoc and shaderLABS for explanation and historical context.
- Record exact Minecraft, loader, Iris, Sodium, GPU, and rendering-mod versions for every compatibility claim.
- Iris supports Fabric 1.16.5+ and NeoForge 1.21.1+; Forge is not supported. Verify current release details before stating them.
- Iris-exclusive packs/features must not be presented as OptiFine-compatible. Prefer optional feature flags and fallbacks where practical.
- Check interactions with Indium, Nvidium, Distant Horizons, Voxy, Canvas, Vulkan mods, and resource packs that use core shaders. Do not assume all render-changing mods coexist.
- Avoid names reserved by Iris patching, including `iris_`, `irisMain`, and `moj_import`.
- GLSL errors may point to transformed code. Enable Iris debug mode with Ctrl+D, then inspect `.minecraft/patched_shaders/` and the full log.

## Reference routing

Load only what the task needs:

- [Iris pipeline](references/iris-pipeline.md): programs, stages, gbuffers, pass selection.
- [Uniforms and buffers](references/uniforms-and-buffers.md): uniforms, depth/color/shadow buffers, outputs.
- [Properties and features](references/properties-and-features.md): options, profiles, flags, ordering, render directives.
- [Debugging and performance](references/debugging-and-performance.md): patched source, diagnosis, profiling, optimization.
- [Compatibility and tooling](references/compatibility-and-tooling.md): version matrix, Sodium/mod boundaries, templates, editors, authoritative links.

## Output expectations

When implementing or reviewing a shader change, report: target matrix, affected passes/files, compatibility boundary, visual behavior, validation actually performed, measured or unmeasured performance impact, and remaining risks. Keep source changes minimal and never fabricate a GPU/runtime result.

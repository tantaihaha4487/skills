# Debugging and performance

## Debug loop

1. Reproduce with the smallest pack and one changed pass.
2. Enable Iris debug mode with Ctrl+D (Cmd+D on macOS), then restart the game.
3. Capture full Minecraft log and first project-owned shader error.
4. Inspect `.minecraft/patched_shaders/`; compiler line numbers refer to transformed code, not necessarily source lines.
5. Classify the issue: GLSL syntax/version, include/preprocessor, uniform or varying mismatch, wrong sampler type, invalid render target, alpha/depth state, missing feature flag, unsupported hardware, or Sodium/rendering-mod interaction.
6. Disable the changed pass, confirm baseline loads, then restore changes incrementally.
7. Test reload, resize, day/night, rain, Nether, End, first-person hand, cutout blocks, entities, water, particles, and weather as relevant.

Use RenderDoc for draw calls, framebuffer attachments, shader state, and GPU cost; inspect buffers when screenshots cannot identify the failing pass.

## Performance loop

Measure frame time and GPU behavior before/after; claim FPS gains only with a reproducible scene and settings.

Prefer:

- fewer fullscreen passes and texture samples;
- half-resolution buffers for bloom, SSAO, and volumetric effects;
- bounded ray-marching loops;
- temporal accumulation when artifacts are controlled;
- explicit render targets and only the buffers actually consumed;
- quality profiles for shadow resolution, filtering, SSAO, SSR, bloom, volumetrics, TAA, and motion blur;
- early exits for sky, far depth, disabled options, and unsupported states.

Watch excessive overdraw, shadow-pass cost, large dynamic loops, unnecessary buffer writes, precision changes, and needless full-resolution effects.

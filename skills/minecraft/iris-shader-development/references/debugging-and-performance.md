# Debugging and performance

## Debug loop

1. Reproduce with the smallest pack and one changed pass.
2. Enable Iris debug mode with Ctrl+D and restart the game.
3. Capture the full Minecraft log and the first project-owned shader error.
4. Inspect `.minecraft/patched_shaders/`; compiler line numbers refer to transformed code, not necessarily source lines.
5. Classify the issue: GLSL syntax/version, include/preprocessor, uniform or varying mismatch, wrong sampler type, invalid render target, alpha/depth state, missing feature flag, unsupported hardware, or Sodium/rendering-mod interaction.
6. Disable the changed pass, confirm the baseline loads, then restore changes incrementally.
7. Test reload, resize, day/night, rain, Nether, End, first-person hand, cutout blocks, entities, water, particles, and weather as relevant.

Use RenderDoc as an advanced tool to inspect draw calls, framebuffer attachments, shader state, and GPU cost. Do not infer a visual bug from a screenshot alone when buffer inspection can identify the failing pass.

## Performance loop

Measure frame time and GPU behavior before and after changes. Do not claim an FPS improvement without a reproducible scene and settings.

Prefer:

- fewer fullscreen passes and texture samples;
- half-resolution buffers for bloom, SSAO, and volumetric effects;
- bounded ray-marching loops;
- temporal accumulation when artifacts are controlled;
- explicit render targets and only the buffers actually consumed;
- quality profiles for shadow resolution, filtering, SSAO, SSR, bloom, volumetrics, TAA, and motion blur;
- early exits for sky, far depth, disabled options, and unsupported states.

Watch for excessive overdraw, shadow-pass cost, large dynamic loops, unnecessary buffer writes, precision changes, and effects that run at full resolution when they do not need to.

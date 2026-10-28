# Uniforms and buffers

## Frequently used uniforms

Camera/player: `cameraPosition`, `previousCameraPosition`, `eyePosition`, `playerLookVector`, `firstPersonCamera`, `isEyeInWater`, `isRiding`, `isElytraFlying`.

Time/world: `worldTime`, `worldDay`, `frameCounter`, `frameTime`, `frameTimeCounter`, `rainStrength`, `wetness`, `sunAngle`, `shadowAngle`, `moonPhase`.

Screen: `viewWidth`, `viewHeight`, `aspectRatio`, `screenBrightness`.

Fog/depth: `near`, `far`, `fogColor`, `fogDensity`, `fogStart`, `fogEnd`, `fogMode`, `fogShape`.

Matrices: `gbufferModelView`, `gbufferModelViewInverse`, `gbufferProjection`, `gbufferProjectionInverse`, `shadowModelView`, `shadowModelViewInverse`, `shadowProjection`, `shadowProjectionInverse`, and previous-frame model/projection matrices.

Lighting/material: `sunPosition`, `moonPosition`, `shadowLightPosition`, `eyeBrightness`, `eyeBrightnessSmooth`, `heldBlockLightValue`, `entityColor`, `alphaTestRef`, `renderStage`.

`chunkOffset` works only in the core profile on Minecraft 1.17+, is zero in compatibility, and remains Iris's name after vanilla renamed it to `modelOffset` in 1.21.2; check the current reference.

Check current Iris docs for uniform type, range, and Iris-exclusive tags.

## Built-in buffers

Samplers include `colortex0` through `colortexN`, `depthtex0`, `depthtex1`, `shadowtex0`, `shadowtex1`, `shadowcolor0`, and `noisetex`; color buffers default to display resolution, while depth/shadow formats and resolution vary. Iris also supports custom textures, images, and SSBOs.

Declare read samplers and explicit outputs; modern packs should prefer:

```glsl
/* RENDERTARGETS: 0,3 */
layout(location = 0) out vec4 sceneColor;
layout(location = 1) out vec4 auxiliary;
```

Legacy `DRAWBUFFERS` cannot address higher indices. Never leave outputs implicit: unintended bindings can overwrite data and cost performance.

## Coordinate and color cautions

Confirm model/player/view/clip/screen/world space. Treat depth as non-linear unless deliberately linearized. Preserve alpha in cutout/translucent programs and document linear/display-encoded colors.

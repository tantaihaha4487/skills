# Uniforms and buffers

## Frequently used uniforms

Camera/player: `cameraPosition`, `previousCameraPosition`, `eyePosition`, `playerLookVector`, `firstPersonCamera`, `isEyeInWater`, `isRiding`, `isElytraFlying`.

Time/world: `worldTime`, `worldDay`, `frameCounter`, `frameTime`, `frameTimeCounter`, `rainStrength`, `wetness`, `sunAngle`, `shadowAngle`, `moonPhase`.

Screen: `viewWidth`, `viewHeight`, `aspectRatio`, `screenBrightness`.

Fog/depth: `near`, `far`, `fogColor`, `fogDensity`, `fogStart`, `fogEnd`, `fogMode`, `fogShape`.

Matrices: `gbufferModelView`, `gbufferModelViewInverse`, `gbufferProjection`, `gbufferProjectionInverse`, `shadowModelView`, `shadowModelViewInverse`, `shadowProjection`, `shadowProjectionInverse`, and previous-frame model/projection matrices.

Lighting/material: `sunPosition`, `moonPosition`, `shadowLightPosition`, `eyeBrightness`, `eyeBrightnessSmooth`, `heldBlockLightValue`, `entityColor`, `alphaTestRef`, `chunkOffset`, `renderStage`.

Check the current Iris uniform reference before relying on a type, range, or Iris-exclusive tag.

## Built-in buffers

Typical samplers include `colortex0` through `colortexN`, `depthtex0`, `depthtex1`, `shadowtex0`, `shadowtex1`, `shadowcolor0`, and `noisetex`. Color buffers are display-resolution by default; depth and shadow formats/resolution can vary. Iris also supports custom textures, images, and SSBOs.

Declare the sampler you read and explicitly declare outputs. For modern packs prefer:

```glsl
/* RENDERTARGETS: 0,3 */
layout(location = 0) out vec4 sceneColor;
layout(location = 1) out vec4 auxiliary;
```

`DRAWBUFFERS` is the legacy form and cannot address higher buffer indices. Never leave outputs implicit: binding unintended buffers can overwrite data and cost performance.

## Coordinate and color cautions

Confirm whether a calculation is in model, player, view, clip, screen, or world space. Treat depth as non-linear unless linearizing it deliberately. Preserve alpha semantics for cutout/translucent programs and document whether colors are linear or display encoded.

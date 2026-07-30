# Iris pipeline reference

## Program order

Iris executes shader programs in this broad order:

```text
setup -> begin -> shadow -> shadowcomp -> prepare -> gbuffers opaque -> deferred -> gbuffers translucent -> composite -> final
```

Program files use the program name plus stage extension: `.vsh`, `.fsh`, `.gsh`, `.csh`, `.tcs`, or `.tes`.

## Gbuffers

Common programs and geometry:

| Program | Geometry |
|---|---|
| `gbuffers_skybasic` | sky, horizon, stars, void |
| `gbuffers_skytextured` | sun and moon |
| `gbuffers_terrain` | static blocks |
| `gbuffers_terrain_solid` | solid terrain |
| `gbuffers_terrain_cutout` | cutout terrain |
| `gbuffers_entities` | entities |
| `gbuffers_block` | block entities and sign text |
| `gbuffers_textured` / `_lit` | particles and textured geometry |
| `gbuffers_water` | translucent terrain |
| `gbuffers_hand` | first-person hand and held items |
| `gbuffers_weather` | rain and snow |

Iris adds more specific programs such as `gbuffers_particles_translucent`, `gbuffers_entities_translucent`, `gbuffers_block_translucent`, and `gbuffers_lightning`. Use them only when their ordering or geometry distinction is needed.

## Stage constraints

Gbuffers-style programs require vertex and fragment stages and may support geometry and tessellation. Composite-style programs render a fullscreen quad and read textures, buffers, or uniforms; compute runs before the vertex stage when combined. Setup is compute-only. Tessellation is limited to gbuffers-style passes and requires the `TESSELLATION_SHADERS` feature flag.

## Design rule

Prefer the smallest pass set that expresses the effect. Use documented fallback programs instead of copying the same shader into every gbuffers file. Keep opaque/deferred/translucent ordering intentional, especially for lighting, water, particles, and reflections.

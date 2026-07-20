# Client Separation and Rendering

Use this reference for renderers, HUD or GUI drawing, models, screens, key input, and any code importing client-only Minecraft classes.

## Client Boundary

- Put physical-client entrypoints and types in the client source set when Loom split environment sources are enabled.
- Keep entity/block entity renderers, screens, render-state classes, key bindings, client packet receivers, and model-layer registration behind that boundary.
- Pass neutral identifiers/data across common-client boundaries rather than client instances.
- Never reference a client-only class in a common static field, method descriptor, annotation value, superclass, or interface.
- Run a dedicated server after changing common signatures; a guarded branch is insufficient evidence of safe class loading.

## Choose the Highest-Level Supported Hook

Prefer, in order:

1. JSON/resource model, item model, blockstate, tint, or built-in renderer registration.
2. Stable Fabric rendering callback or renderer abstraction for the exact version.
3. A custom render pipeline/state implementation.
4. A narrow client Mixin only when no supported hook exposes the required phase.

Do not issue legacy direct OpenGL calls. Use Minecraft/Fabric render abstractions so ordering, state, batching, and compatibility remain under the engine's control.

## Extraction and Drawing

Modern Minecraft rendering separates gathering renderable state from submitting draw work. Across recent releases, Fabric rendering hooks and Minecraft types have changed substantially.

- Capture immutable render state during the documented extraction/preparation phase.
- Submit drawing in the matching draw phase and avoid mutating world/game state there.
- Reuse buffers, pipelines, and cached immutable geometry where the API permits.
- Avoid per-frame allocations, unbounded caches, synchronous I/O, and repeated registry/resource lookups.
- Invalidate cached resources on resource reload and device/window lifecycle events as documented.
- Restore or scope render state through supported abstractions; do not assume another renderer leaves global state unchanged.

World Render Events were reintroduced for 1.21.10/1.21.11 after rendering changes. Current 26.1 code also uses unobfuscated naming and additional API renames. Never port a renderer by name substitution alone; verify phase semantics and target Javadocs.

## Validation Matrix

- client startup and resource reload;
- the precise world/GUI/HUD context, including resize and GUI scale where relevant;
- integrated server behavior if world state is read;
- dedicated-server startup for any changed common signature;
- multiple renderers/mods when ordering or shared state matters;
- performance under representative entity/particle/geometry counts.

## Official Sources

- [Fabric rendering concepts](https://docs.fabricmc.net/develop/rendering/basic-concepts)
- [1.21.11 world rendering](https://docs.fabricmc.net/1.21.11/develop/rendering/world)
- [Current world rendering](https://docs.fabricmc.net/develop/rendering/world)
- [Fabric 1.21.11 release notes](https://fabricmc.net/2025/12/05/12111.html)
- [Fabric API migration guide](https://docs.fabricmc.net/develop/porting/fabric-api)

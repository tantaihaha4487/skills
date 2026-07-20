# Best Practices and Failure Prevention

Use this reference as the final design and diff review for changes that cross multiple Fabric systems.

## Architecture

- Make entrypoints establish registrations; avoid expensive work or assumptions that resources and other mods have completed initialization.
- Use explicit initialization calls so registry-holder reachability is visible.
- Scope state to its owner and lifecycle; clean up caches on disconnect, unload, reload, or dimension changes.
- Keep common APIs free of client types, including signatures and static initializers.
- Let the logical server decide game state; render and predict on the client without granting authority.

## Compatibility

- Verify exact Minecraft, mapping, Loader, Loom, Fabric API, and dependency versions before selecting a signature.
- Prefer public stable APIs and composable events; isolate experimental APIs.
- Treat Mixins, widened access, injected interfaces, identifiers, packet formats, saved data, and config keys as compatibility surfaces.
- Use namespaced identifiers and unique Mixin/injected method names.
- Compose with loot/resource/event modification hooks rather than replacing shared global definitions.
- Test a dedicated server whenever metadata claims server compatibility.

## Performance and Threads

- Know the documented callback thread. Schedule game-state mutations to the correct server/client thread when necessary.
- Protect truly shared state with an appropriate lock, concurrent structure, immutable snapshot, or copy-on-write strategy; do not add synchronization blindly to game-thread-only state.
- Avoid synchronous disk/network I/O in ticks, render loops, and packet handlers.
- Avoid per-tick/per-frame allocations, full-registry scans, global broadcasts, and repeated resource parsing.
- Bound caches, packet collections, recursion guards, and queues; clear them on lifecycle end.
- Send to tracking players rather than every connection.

## Data and Resources

- Prefer tags/resources for configurable membership and datapack interoperability.
- Use codecs as explicit schemas; report decode failures and provide compatible defaults for additive changes.
- Mark `SavedData` dirty and replace immutable attachment/component values through their APIs.
- Regenerate managed resources and review the diff; do not patch output directories.
- Preserve resource namespaces and case-sensitive paths.

## Common Mistakes

| Mistake | Prevention |
| --- | --- |
| Copying current-doc code into an older target | Lock the version contract and use the documentation selector/Javadocs. |
| Assuming `v0` means experimental | Inspect annotations and module lifecycle metadata. |
| Relying on entrypoint order across mods | Declare dependencies and use lifecycle callbacks. |
| Guarding a client import with `if` in common code | Isolate the type in a client source set/class. |
| Trusting coordinates or IDs from C2S | Validate authority and current server state. |
| Mutating attachment data in place | Replace values through the attachment API. |
| Forgetting `SavedData#setDirty` | Centralize mutations and mark after successful change. |
| Adding a Mixin before searching events | Follow the extension-point decision ladder. |
| Replacing a loot table/global resource | Use the official modify/composition hook. |
| Hand-editing datagen output | Change providers and rerun datagen. |
| Direct legacy OpenGL calls | Use target-version Minecraft/Fabric rendering abstractions. |
| Compiling only | Run the applicable physical environments and inspect packaging. |

## Final Review Questions

- Does every new class/resource have a reachable registration path?
- Can a dedicated server load every common signature?
- Is every state mutation on the owning logical side and thread?
- Are packet inputs, persisted data, and config values bounded and validated?
- Is the API public and stable for the resolved version?
- Could an event/resource/tag preserve composition better?
- Does the change reuse repository utilities instead of creating a parallel abstraction?
- Were generated files regenerated and only intended output changed?
- Do validation claims distinguish compile, test, runtime, and artifact evidence?

## Official Sources

- [Fabric API contributor guidelines](https://github.com/FabricMC/fabric/blob/1.21.11/CONTRIBUTING.md)
- [Fabric events](https://docs.fabricmc.net/develop/events)
- [Fabric networking](https://docs.fabricmc.net/develop/networking)
- [Fabric rendering concepts](https://docs.fabricmc.net/develop/rendering/basic-concepts)
- [Fabric data attachments](https://docs.fabricmc.net/develop/data-attachments)
- [Fabric saved data](https://docs.fabricmc.net/develop/saved-data)

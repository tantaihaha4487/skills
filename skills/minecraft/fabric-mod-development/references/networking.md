# Networking and Synchronization

Use this reference whenever behavior crosses logical sides or a client needs server-owned state.

## Design the Contract First

For each message, write down:

- direction and lifecycle phase (configuration, play, login where supported);
- payload identifier, fields, bounds, and target-version codec type;
- who may send it and under which game-state preconditions;
- server authorization and validation;
- receiving thread and where mutation is scheduled;
- recipients and tracking scope;
- compatibility behavior when peers lack the optional channel.

Packets are commands or observations, not permission. A C2S packet expresses a request; the logical server independently verifies player, target existence, distance/range, permissions, current state, rate/size limits, and expected dimension.

## Registration Flow

Exact classes and method names vary by Minecraft/Fabric API version. Verify the target docs and resolved Javadocs, then preserve this invariant:

1. Define a small immutable custom payload and its identifier/type.
2. Define a stream codec with identical field order and bounds on both ends.
3. Register the payload type in common initialization so both physical environments recognize it.
4. Register the receiver in the entrypoint for the physical environment that receives it.
5. Validate before mutation, then execute game-state changes on the documented game thread.
6. Send only to relevant players, commonly those tracking the entity, chunk, or position.

For 1.21.11 documentation, play-phase registration uses `PayloadTypeRegistry.playC2S` and `playS2C`; newer unobfuscated versions use clientbound/serverbound naming. This is exactly why code must follow the target-version docs rather than a current snippet.

## Synchronization Choices

- Prefer vanilla or Fabric-provided sync for registry entries, data attachments, tracked entity data, screen handlers, or components when it matches the state.
- Use explicit packets for transient actions or state without an existing synchronization channel.
- Send deltas when state is large, but make resynchronization possible after join, dimension change, tracking start, or packet loss assumptions at the application level.
- Use player-tracking helpers instead of broadcasting to every connection.
- Register large-payload support only when the target API supports it and the payload genuinely requires it; redesign unbounded payloads first.

## Review Failures

| Symptom | Inspect first |
| --- | --- |
| Unknown custom payload/disconnect | Type registration on both physical sides and matching mod/API versions |
| Decode exception | Field order, registry-aware codecs, bounds, and target-version API |
| Works in single-player only | Physical/logical side assumptions and dedicated-server class loading |
| Client sees stale state | Initial sync, tracking lifecycle, authoritative mutation, or missing dirty/sync call |
| Server crash or exploit | C2S trust, null/stale targets, range/permission checks, rate and size limits |
| Concurrent modification | Receiver thread guarantee and scheduling to the game thread |

## Official Sources

- [1.21.11 Fabric networking](https://docs.fabricmc.net/1.21.11/develop/networking)
- [Current Fabric networking](https://docs.fabricmc.net/develop/networking)
- [1.21.11 Fabric API release notes](https://fabricmc.net/2025/12/05/12111.html)
- [Fabric player lookup documentation](https://docs.fabricmc.net/develop/networking)

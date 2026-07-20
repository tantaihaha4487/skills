# Entities

Use this reference after identifying entity ownership, delayed work, persistence needs, and target-version API replacements.

## Use when

- Teleport, track, display, target, pathfind, mount, or otherwise mutate an entity.
- Add custom mob goals or temporary visual entities.

## Prefer

- Execute mutations on the entity's owning execution context; under Folia, use its `EntityScheduler`.
- Use `teleportAsync` when the destination may require chunk loading.
- Store UUIDs for durable identity; treat network entity IDs as transient.
- Re-check validity when delayed or asynchronous work resumes.
- Configure display entities in the spawn consumer and explicitly remove temporary displays.
- Use Paper goal and pathfinder APIs instead of NMS when they express the behavior.
- Keep every goal selector and tick method bounded and cheap.

## Avoid and pitfalls

- Never block the server thread with `teleportAsync().get()` or `.join()`; this can deadlock.
- Do not schedule moving entities with a fixed region scheduler under Folia.
- Do not assume `persistent(false)` guarantees timely display removal; a loaded chunk may retain it.
- Do not equate client visibility or interpolation with collision, authority, or server-side state.
- Do not assume pathfinding accepts a destination; check its result and the entity's continued validity.
- Do not keep strong entity references as durable persistence identifiers.

## Replacements and compatibility

- Replace singular passenger APIs with `getPassengers()` and `addPassenger()` where target Javadocs require it.
- Replace generic hand APIs with main-hand and off-hand methods.
- Check current tri-state visual-fire APIs instead of assuming legacy booleans.
- Version-check teleport flags; behavior such as passenger retention has changed across releases.
- Prefer public API over reflection or NMS; if internals are unavoidable, isolate and justify them separately.

## Thread, client, and version boundary

- Apply the shared threading/Folia policy; entity ownership is the decisive boundary.
- Display interpolation, particles, and visibility are client-rendered and may vary by client settings/resources.
- Resolve every deprecated call against the repository's exact Paper Javadocs, not the latest docs alone.

## Validation evidence

- Test loaded- and unloaded-chunk teleport paths without blocking.
- Test delayed actions after death, removal, world change, and plugin disable.
- Confirm temporary displays are removed and goals/pathfinding stop cleanly.
- Run the relevant Paper or Folia server path when compatibility is claimed.

## Official sources

- [Entity API](https://docs.papermc.io/paper/dev/api/entity-api/)
- [Teleportation](https://docs.papermc.io/paper/dev/entity-teleport/)
- [Display entities](https://docs.papermc.io/paper/dev/display-entities/)
- [Mob Goal API](https://docs.papermc.io/paper/dev/mob-goals/)
- [Pathfinder API](https://docs.papermc.io/paper/dev/entity-pathfinder/)
- [`Entity` Javadocs (current index; select the repository target)](https://jd.papermc.io/paper/org/bukkit/entity/Entity.html)

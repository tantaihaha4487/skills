# Folia compatibility

## Scope

Use this reference only when a repository already claims Folia support or the requested change
introduces that support. Use [scheduler.md](scheduler.md) to select APIs and
[thread-safety.md](thread-safety.md) for plugin-owned concurrency.

## Compatibility model

Folia groups nearby loaded chunks into independent regions whose tick loops run in parallel.
There is no single main thread. A region owns its entity, chunk, and point-of-interest state while
it ticks; code in one region must not access or modify another region's state.

This ownership does not make plugin data thread-safe. Commands, events, and scheduled callbacks
from different regions may overlap. Design repository services and invariants for that concurrency.

## Decide support deliberately

1. Inspect existing descriptors, scheduler abstraction, dependency target, and CI/runtime matrix.
2. Map every game-state operation to an entity, location/region, or global owner.
3. Map every shared plugin invariant across those owners.
4. Replace conventional main-thread assumptions with owner-aware scheduling.
5. Test on actual Folia with players or fixtures in separated regions.
6. Add `folia-supported: true` to `plugin.yml` or `paper-plugin.yml` only after those checks pass.

The flag permits loading; Paper's documentation explicitly says it is not proof of compatibility.
Do not add it speculatively or merely because the project compiles against scheduler APIs.

## Ownership rules

- Use `Entity#getScheduler()` for entity work; an entity can cross region and world boundaries.
- Use `RegionScheduler` for a fixed block, chunk, or location.
- Use `GlobalRegionScheduler` only for work that belongs to global server state.
- Use `AsyncScheduler` for tick-independent, non-game-state work, then return to the owner.
- Use `Bukkit.isOwnedByCurrentRegion(...)` as a diagnostic/precondition where useful; it does not
  transfer ownership or make a cross-region call safe.
- Re-resolve delayed targets. Do not read an entity location from a context that does not own it.

Avoid hard-coding lists of "currently broken" Folia APIs from repository prose. Those lists and
future-tense plans age quickly; verify the targeted Paper/Folia Javadocs and release notes.

## Hazards to reject

- Treating Folia as "Paper with more async tasks" or searching for a replacement main thread.
- Reading or mutating entities, chunks, inventories, scoreboards, or world state cross-region.
- Protecting a compound invariant only by replacing `HashMap` with `ConcurrentHashMap`.
- Waiting synchronously for another region, which risks deadlocks and destroys parallelism.
- Testing only one populated region, where cross-region races remain hidden.

## Validation evidence

- Descriptor flag matches the documented support claim and runtime test matrix.
- Every stateful callback has an owner; every cross-owner result is immutable and revalidated.
- Concurrent separated-region scenarios preserve counters, cooldowns, caches, and uniqueness rules.
- Entity migration/removal, teleportation, disable, and late async completion paths are exercised.

## Official sources

- [Supporting Paper and Folia](https://docs.papermc.io/paper/dev/folia-support/)
- [PaperMC Folia repository and regionized model](https://github.com/PaperMC/Folia)
- [Bukkit ownership checks](https://jd.papermc.io/paper/org/bukkit/Bukkit.html)
- [Entity scheduler Javadocs](https://jd.papermc.io/paper/io/papermc/paper/threadedregions/scheduler/EntityScheduler.html)

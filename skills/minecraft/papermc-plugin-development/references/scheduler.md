# Scheduling and task ownership

## Scope

Use this reference to choose an execution context and manage scheduled work. Read
[thread-safety.md](thread-safety.md) for async boundaries and [folia.md](folia.md) when the
repository promises Folia support.

## Decide by owner, then by clock

1. Identify the state the callback will access when it runs, not where it is scheduled.
2. Select the owner-specific scheduler.
3. Decide whether delay means game ticks or elapsed wall time.
4. Make cancellation and plugin shutdown explicit.

| Work | Scheduler |
| --- | --- |
| Paper-only game-state work | Synchronous `BukkitScheduler` task |
| A block, chunk, or fixed location | `RegionScheduler` |
| An entity that may move | `Entity#getScheduler()` |
| Server-global work with no region owner | `GlobalRegionScheduler` |
| Blocking I/O or pure computation | `AsyncScheduler` or a plugin-owned executor |

The region, entity, global, and async schedulers also work on Paper. Prefer them when one
implementation must support Paper and Folia. Do not use a region scheduler for an entity: the
entity scheduler follows the entity across regions and reports retirement.

Ticks are logical game time. The target is 20 ticks per second, with 50 ms available to the
entire tick; lag stretches tick-based delays. Use an async scheduler or a lifecycle-managed
`ScheduledExecutorService` only when elapsed time must not follow tick rate, then return to the
correct owner before touching game state.

## Own the task lifecycle

- Retain task handles when later cancellation matters; cancellation prevents future execution
  but is not a substitute for cooperative cancellation inside already-running work.
- Cancel repeating and delayed work during shutdown and reject new callbacks once stopping.
- Handle scheduling failure and entity retirement. Keep an entity retired callback minimal:
  Paper documents it as critical code where entity removal, world/chunk loads, and ticket
  changes are unsafe.
- Pass the owning plugin to scheduler APIs; do not hide ownership in unmanaged static helpers.
- Prefer one event-driven action to a frequent polling loop when the API exposes an event.

## Hazards to reject

- `Thread.sleep`, file/network/database calls, or future waits on a tick/region thread.
- `.get()` or `.join()` on `teleportAsync` from the main thread; Paper warns this can deadlock.
- Assuming a tick delay is a real-time deadline or that async Bukkit scheduler timing is
  independent of server lag.
- Capturing an entity and later mutating it from a location task without re-establishing owner.
- Fire-and-forget repeating tasks with no stop path, exception reporting, or bounded workload.

## Validation evidence

- Inventory every scheduling site with: owner, clock, period, maximum work, cancellation path.
- Exercise enable, disable, and a second startup; confirm no callback runs after shutdown.
- Test entity removal before a delayed callback and unloaded-chunk teleport completion.
- For Folia claims, execute concurrent work in separated regions; compilation alone is not proof.

## Official sources

- [Scheduling](https://docs.papermc.io/paper/dev/scheduler/)
- [Supporting Paper and Folia](https://docs.papermc.io/paper/dev/folia-support/)
- [Scheduler Javadocs](https://jd.papermc.io/paper/io/papermc/paper/threadedregions/scheduler/package-summary.html)
- [Teleportation](https://docs.papermc.io/paper/dev/entity-teleport/)

# Thread safety and asynchronous boundaries

## Scope

Use this reference for async I/O, computation, futures, asynchronous events, and plugin-owned
shared state. Scheduler selection belongs in [scheduler.md](scheduler.md); Folia region ownership
belongs in [folia.md](folia.md).

## Default rule

Treat Paper/Bukkit game state as confined unless the exact API Javadocs explicitly guarantee
thread safety. On conventional Paper, access or mutate world, entity, player, block, and inventory
state on the main thread. On Folia, use the owning region/entity/global context instead.

An event being asynchronous describes how that event is fired; it does not make arbitrary Bukkit
calls safe. Paper specifically warns that Bukkit API use inside `AsyncChatEvent` is unsafe. Inspect
the concrete event's documentation and `Event#isAsynchronous()` rather than inferring from names.

## Use a split-phase pipeline

1. On the valid owner, capture only immutable inputs: UUIDs, keys, coordinates, strings, numbers,
   or repository-defined DTOs.
2. Run only blocking I/O or pure computation off-thread, with bounded concurrency and timeouts.
3. Surface failures explicitly; never allow an exceptional future to disappear silently.
4. Schedule the result back to the current owner.
5. Re-resolve objects and revalidate plugin state, entity/player presence, world availability,
   permissions, and whether a newer request made the result stale.
6. Apply the result without blocking the owner thread.

Do not carry live `Player`, `Entity`, `World`, `Inventory`, mutable configuration, or NMS objects
through an async phase. A UUID is an identifier, not a guarantee that the object still exists.

## Protect plugin-owned state

- Establish one owner for each mutable invariant, or use explicit synchronization where owners
  may execute concurrently.
- Bound executors, queues, caches, retries, and pending futures. Backpressure is part of safety.
- A concurrent collection protects individual operations, not multi-step invariants. Use an
  atomic operation or a lock for check-then-act behavior.
- Use immutable configuration snapshots and atomically publish a fully validated replacement.
- During disable, close admission first, cancel producers, stop executors, perform only bounded
  finalization, and reject late completions.

## Hazards to reject

- `CompletableFuture#get/join`, synchronous chunk loads, or blocking I/O on an owner thread.
- Calling Bukkit APIs from a generic executor because a nearby operation appeared to work.
- Mutating ordinary maps, lists, or service state from callbacks that may overlap on Folia.
- Unbounded `supplyAsync` fan-out or the common pool for latency-sensitive plugin work.
- Assuming cancellation interrupts database/network work or makes an in-flight callback vanish.

## Validation evidence

- Mark every async boundary in the implementation plan with captured input and return owner.
- Test timeout, cancellation, exception, disable-during-work, and stale-result paths.
- Run concurrency tests for plugin-owned invariants; use a real Folia server for ownership claims.
- Review logs after shutdown for late callbacks, rejected tasks, or surviving plugin threads.

## Official sources

- [Scheduling: synchronous and asynchronous tasks](https://docs.papermc.io/paper/dev/scheduler/)
- [Chat events](https://docs.papermc.io/paper/dev/chat-events/)
- [`Event#isAsynchronous` Javadocs](https://jd.papermc.io/paper/org/bukkit/event/Event.html#isAsynchronous())
- [Teleportation and future deadlock warning](https://docs.papermc.io/paper/dev/entity-teleport/)

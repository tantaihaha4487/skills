# Performance decisions

## Load this reference when

Load this file for tick-time regressions, hot events, repeating tasks, caching, allocation-sensitive paths, database or network work, or a performance claim.

## Diagnose before optimizing

1. Reproduce the issue under a representative workload.
2. Capture a spark profile while the issue is actively occurring.
3. Locate plugin-owned hot frames, call frequency, blocking waits, and allocation or garbage-collection pressure.
4. Form one measurable hypothesis and change the smallest responsible path.
5. Repeat the same workload and compare profiles.

Use TPS or MSPT as symptoms, not attribution. Paper identifies spark as its preferred profiler; Timings is deprecated. Do not optimize from anecdotes or a single slow log line.

## Protect tick-owning threads

- Keep synchronous and region-owned callbacks within the tick budget.
- Move file, network, database, and expensive pure computation off tick-owning threads.
- Never treat asynchronous execution as permission to access Bukkit state; return through the correct server, region, or entity scheduler.
- Bound work per tick. Batch or spread large scans instead of moving an unbounded loop into a repeating task.
- Avoid polling when an event, lifecycle hook, or invalidation signal can express the change.
- Cache only demonstrated expensive, reusable results. Define invalidation, ownership, size bounds, and shutdown behavior first.
- Prefer identifiers or immutable snapshots across async boundaries instead of retaining mutable server objects.
- Reuse repository abstractions before adding pools, queues, caches, or utility layers.

On Folia, select global, region, entity, or async schedulers by data ownership. A global task is not a substitute for entity- or region-confined work.

## Review hot paths

For frequently fired events and scheduled tasks, inspect algorithmic growth, repeated registry or collection scans, object creation, logging volume, serialization, and downstream calls. Guard cheap rejection conditions early, but preserve event semantics and correctness.

Do not trade correctness for micro-optimization. Prefer an API-level solution over reflection or NMS unless profiling proves a gap and the internals decision gate is satisfied.

## Required evidence

- Baseline and post-change spark reports from comparable workloads.
- The plugin-owned frames or waits that supported the hypothesis.
- Runtime behavior and threading validation after the change.
- Memory and cache lifecycle evidence when retaining new state.
- A statement of unmeasured risks; do not claim improvement beyond captured evidence.

## Official sources

- [Paper profiling](https://docs.papermc.io/paper/profiling/)
- [Paper performance commands](https://docs.papermc.io/paper/reference/commands/#performance-profiling)
- [Paper scheduling](https://docs.papermc.io/paper/dev/scheduler/)
- [Supporting Paper and Folia](https://docs.papermc.io/paper/dev/folia-support/)


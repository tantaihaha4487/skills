# Common Reasoning Patterns

Load this reference when a change crosses lifecycle, state, integration, or asynchronous boundaries. These are synthesis patterns, not a Paper-mandated package layout. Apply them only when they fit the repository.

## Compose at the owned lifecycle boundary

Construct the feature graph in the repository's existing bootstrap or enable path. Pass required collaborators explicitly where the codebase already uses constructor injection. Keep one owner for each task, executor, data source, channel, temporary entity set, and external registration. Make cleanup tolerate partial initialization.

Do not introduce a dependency-injection framework, service locator, singleton, or static plugin accessor solely to implement a small change. Paper does not prescribe one. Reuse the project's composition and ownership model.

## Separate domain work from Paper access

Keep calculations, parsing, validation, and persistence DTOs detached from live Bukkit objects when practical. This makes thread boundaries and tests visible without forcing a new architecture. At an async boundary:

1. capture minimal immutable input on the owning server context;
2. perform bounded I/O or pure computation off-thread;
3. return to the correct owner, re-resolve identifiers, and revalidate state before mutation.

## Publish validated configuration snapshots

Parse a candidate configuration, validate all fields and cross-field rules, then publish an immutable runtime view. Retain the previous valid view if reload fails. Rebuild and dispose dependent resources explicitly; `reloadConfig()` alone does not do this.

## Model optional integrations as capabilities

Compile against another plugin's API without bundling it, describe the relationship correctly in the plugin descriptor, and resolve the provider once. Keep absence and provider removal behavior explicit. Use `ServicesManager` for shared capabilities when that is the established interoperability contract.

## Use stable identities across time

Carry UUIDs, namespaced keys, immutable locations, or detached records into delayed work. Re-resolve players, entities, registries, and worlds at execution time and handle absence. Do not retain NMS handles or live inventory views as durable state.

## Isolate version-specific capability

First seek a public API that spans the supported range. If targets genuinely differ, put the smallest varying surface behind the repository's existing adapter/module boundary. Compile and runtime-test every promised target. Do not use reflection as an undocumented universal compatibility layer.

## Keep utilities cohesive

Reuse an existing helper if its contract fits. Add behavior to the owning service or a narrowly named helper instead of creating a generic `Utils` dumping ground. Do not duplicate serializers, key factories, schedulers, log wrappers, or config accessors already present.

## Make null and failure policy explicit

Follow target-version Javadocs for nullable returns. Handle optional dependencies, missing registry entries, retired entities, absent players, invalid config, failed futures, and storage outages at the boundary where they arise. Log actionable context through the plugin logger without secrets; do not swallow asynchronous failures.

## Maintain a validation ledger

For each planned change, map the behavior to its proof: compile gate, artifact inspection, clean startup, functional exercise, shutdown/restart, migration fixture, load profile, or Folia multi-region test. A successful build proves only the build.

Official constraints behind these patterns: [plugin lifecycle](https://docs.papermc.io/paper/dev/how-do-plugins-work/), [scheduling](https://docs.papermc.io/paper/dev/scheduler/), [configuration](https://docs.papermc.io/paper/dev/plugin-configurations/), [ServicesManager Javadocs](https://jd.papermc.io/paper/org/bukkit/plugin/ServicesManager.html), and [internals guidance](https://docs.papermc.io/paper/dev/internals/).


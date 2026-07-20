---
name: papermc-plugin-development
description: Analyze, design, implement, debug, test, migrate, and maintain Java plugins for PaperMC, including new or existing plugins, large suites, multi-module repositories, and Folia-compatible projects. Use for repositories involving plugin.yml or paper-plugin.yml, Paper API, Gradle or Maven, paperweight-userdev, lifecycle, commands, events, entities, inventories, Adventure components, PDC, data components, schedulers, configuration, databases, plugin messaging, registries, recipes, particles, performance, migrations, CI, publishing, or runtime failures.
---

# PaperMC Plugin Development

Develop Paper plugins by discovering the repository's actual architecture, target matrix, lifecycle, and thread-ownership model before changing code. Use the bundled references as decision aids and verify volatile details against official Paper sources for the exact target version.

## Non-negotiable rules

- Read repository instructions and inspect the real build before designing.
- Never invent or replace architecture merely because another layout is common.
- Reuse existing services, helpers, registration paths, module boundaries, and validation tasks when their contracts fit.
- Derive Minecraft/Paper, Java, mappings, Adventure, and Folia targets from repository evidence. Do not assume the current documentation version is the target.
- Prefer supported Paper/Bukkit APIs. Treat NMS, reflection, packet access, and experimental APIs as justified, isolated exceptions.
- Establish lifecycle and thread ownership before adding asynchronous, scheduled, entity, inventory, world, or persistent-state behavior.
- Do not implement a code-changing request before completing stages 1 through 4 below.
- Do not claim runtime, migration, performance, or Folia compatibility without the corresponding evidence.

## Required workflow

Follow this sequence for every implementation. Compress it for a small change, but do not reorder or skip it. For a read-only review or diagnosis, complete the analysis stages and stop before mutation unless the user also authorized a change.

### 1. Repository analysis

1. Read `AGENTS.md`, `CONTRIBUTING.md`, build instructions, support policy, and module-local guidance that applies to the target files.
2. Check worktree state and preserve unrelated user changes.
3. Inspect root and module build files, wrappers, version catalogs, convention plugins, resource processing, shading, publishing, CI, and run-server tasks.
4. Map deployable plugin artifacts versus shared/API/adapter/test modules. Do not assume every module produces a plugin JAR.
5. Locate source or generated `plugin.yml` and `paper-plugin.yml`; identify which file is authoritative and how placeholders are expanded.
6. Locate the `JavaPlugin` entrypoint and any bootstrapper or loader. Trace enable, disable, registration, configuration, persistence, integrations, executors, and cleanup.
7. Locate command and listener registration, scheduler abstractions, PDC/database schemas, tests, fixtures, and runtime smoke tooling.
8. Run `python3 <skill-dir>/scripts/inspect_paper_project.py <repo>` when available, then verify its text matches manually. It reports evidence, not correctness.

Do not edit generated sources, `build/`, `target/`, or a processed descriptor. Find the generator or source resource.

### 2. Architecture summary

Before planning code, state a compact summary with these fields:

```text
Target matrix: Minecraft/Paper, Java, mappings, Adventure, Folia claim
Build/artifact: build system, modules, deployable JAR, shading/resource processing
Plugin model: plugin.yml or experimental Paper plugin; entrypoint/bootstrap/loader
Lifecycle: load/enable/running/disable ownership and partial-init behavior
Registration: commands, listeners, services, messaging, recipes/registries
State: configuration, PDC/data components, files/database, schema/migrations
Thread model: Paper main-thread or Folia owners, async work, executors/tasks
Integrations: hard/soft plugin dependencies and external libraries/services
Validation path: repository tasks, artifact checks, runtime matrix
Unknowns/risks: facts still requiring official lookup or execution
```

Resolve cheap unknowns before continuing. Ask the user only when an unresolved choice would materially alter compatibility, public behavior, data, or architecture.

### 3. Dependency and compatibility analysis

1. Classify each dependency as Paper API/dev bundle, plugin API, bundled library, runtime-loaded library, test tool, or build plugin.
2. Confirm Paper API is compile-only/provided and not packaged. For userdev, confirm the dev bundle owns the Paper API dependency.
3. Match plugin dependencies to descriptor semantics and absence handling. Do not turn an optional integration into a hard dependency accidentally.
4. Inspect shading, relocation, service-file merging, and the final artifact task before adding a library.
5. Identify deprecated, experimental, internal, client-sensitive, and version-specific APIs touched by the request.
6. Open [source-policy.md](references/source-policy.md), then consult current official docs and exact-target Javadocs for volatile signatures or behavior.
7. State the minimum and maximum compatibility actually being preserved. Treat broad compatibility as a test matrix, not an `api-version` claim.

### 4. Implementation plan

Write a minimal, file-specific plan before editing. Include:

- existing abstractions to reuse and why they own the behavior;
- registration and lifecycle timing;
- state/schema/config changes and backward migration;
- execution owner for every callback and async transition;
- cancellation, failure, disable, and late-completion behavior;
- dependency/client interoperability effects;
- validation evidence for each risk.

Challenge scope creep. Avoid package reshuffles, framework migrations, new generic utilities, and unrelated deprecation cleanup unless required by the request.

### 5. Code changes

- Follow repository naming, packaging, nullness, logging, formatting, and test conventions.
- Keep the `JavaPlugin` class a lifecycle/composition boundary when that matches the repository; do not manually instantiate it.
- Keep constructor work independent of server readiness. Put runtime registration and owned-resource startup in the established enable/lifecycle path.
- Make disable cleanup safe after partial initialization. Stop new work, cancel producers/tasks, close owned resources, prevent late mutation, and remove temporary state.
- Use Adventure components at supported Paper boundaries. Keep legacy serialization only at explicit compatibility edges.
- Treat namespaced keys and persisted formats as schemas. Migrate intentionally; do not silently reinterpret stored data.
- Capture immutable/detached input, perform bounded off-thread work, return to the correct owner, and revalidate live state before mutation.
- Keep hot callbacks short. Prefer an event over polling when it represents the transition.
- Add no deprecation suppression, reflection, NMS, experimental API, or Folia descriptor claim without recorded justification and matching validation.

### 6. Validation

Run the narrowest useful checks during development, then the repository's full production gate. Prefer checked-in wrappers over system tools.

1. Run formatting/static analysis, unit tests, compilation, and the production build applicable to changed modules.
2. Review all warnings and deprecations introduced or exposed by the change.
3. Run `python3 <skill-dir>/scripts/validate_paper_project.py <repo>` when applicable. Pass `--build-system` for a mixed-build root, `--build-task` for the repository's actual production task/goal, `--java-home` when the shell JDK differs from the target, and `--artifact` for the exact deployable JAR. For a custom non-Gradle/Maven pipeline, run it first and use `--skip-build --artifact`.
4. Inspect the built descriptor, entrypoint classes, resources, unresolved placeholders, shaded dependencies, service descriptors, and absence of bundled Paper API.
5. Start a clean server on the exact target and inspect full enable logs. Exercise affected commands, permissions, events, config, persistence, and integrations.
6. Stop fully, inspect disable errors and leaked resources, then start again with existing data.
7. Test missing/malformed configuration, missing optional dependencies, failed I/O, cancellation, entity/player disappearance, and partial initialization where applicable.
8. Test old data and every claimed target for migrations or broad compatibility.
9. Use an active spark profile for performance claims.
10. Run actual multi-region Folia scenarios before claiming Folia support. Compilation and Paper runtime are insufficient.

Never use `/reload` as lifecycle acceptance. A plugin-specific configuration refresh is a separate feature and must rebuild only the state it explicitly owns.

### 7. Summary

Lead with the result. Report changed files and behavior, architecture/convention decisions preserved, target compatibility, validation commands and outcomes, runtime evidence, and any unverified gates. Distinguish `compiled`, `built`, `loaded`, `functionally tested`, and `Folia-tested` claims.

## Decision gates

### Choose the plugin model

- Preserve the descriptor model of an existing repository.
- For a normal new plugin, default to `plugin.yml` and one descriptive `JavaPlugin` entrypoint.
- Use experimental `paper-plugin.yml`, bootstrap, or loaders only for an existing architecture or a capability that truly requires early bootstrap/classloading behavior.

### Choose the API surface

- Public Paper/Bukkit API can express the behavior: use it.
- API is deprecated: use the exact-target documented replacement; do not guess.
- API is experimental: pin the target, isolate the surface, and add runtime coverage.
- Public API cannot express a required behavior: document the gap, isolate internals, and use paperweight-userdev with per-target tests.

### Choose the execution context

- Paper-only live game state: use the synchronous server context unless the exact API documents otherwise.
- Folia location/block state: use the owning region scheduler.
- Folia entity state: use the entity scheduler so ownership follows movement.
- Global state: use the global scheduler.
- File, database, HTTP, serialization, or pure computation: use bounded async execution, then return to the correct owner.
- Never block an owner thread waiting for async completion.

## Reference routing

Load only the references required for the request, but always load the source policy for version-sensitive work.

| Concern | Reference |
|---|---|
| Authority, version freshness, source conflicts | [source-policy.md](references/source-policy.md) |
| Repository discovery, modules, artifacts, build conventions | [project-architecture.md](references/project-architecture.md) |
| Constructor/load/enable/disable, ownership, reload | [plugin-lifecycle.md](references/plugin-lifecycle.md) |
| `plugin.yml`, experimental Paper plugins, dependency metadata | [plugin-descriptors.md](references/plugin-descriptors.md) |
| paperweight-userdev, mappings, NMS/reflection boundary | [paperweight-internals.md](references/paperweight-internals.md) |
| Brigadier, BasicCommand, permissions and registration | [commands.md](references/commands.md) |
| Listener semantics, priorities, cancellation, async/custom events | [events.md](references/events.md) |
| Entity identity, teleportation, displays, goals and pathfinding | [entities.md](references/entities.md) |
| Inventory transactions, holders, Menu Type and Dialog APIs | [inventories-dialogs.md](references/inventories-dialogs.md) |
| Adventure, MiniMessage, audiences, translations and signed chat | [components.md](references/components.md) |
| Plugin-owned persistent metadata and schema | [pdc.md](references/pdc.md) |
| Experimental vanilla item data components | [data-components.md](references/data-components.md) |
| Tick semantics, task selection, cancellation | [scheduler.md](references/scheduler.md) |
| Async boundaries, thread confinement and futures | [thread-safety.md](references/thread-safety.md) |
| Region ownership and Folia validation | [folia.md](references/folia.md) |
| Config resources, validation, snapshots and refresh | [configuration.md](references/configuration.md) |
| Storage choice, JDBC, pooling, migrations and shutdown | [database.md](references/database.md) |
| Plugin channels, protocols, ServicesManager interoperability | [plugin-messaging-services.md](references/plugin-messaging-services.md) |
| Registry access/mutation and bootstrap datapacks | [registries-datapacks.md](references/registries-datapacks.md) |
| Recipe authority/discovery and particle presentation | [recipes-particles.md](references/recipes-particles.md) |
| Tick cost, caching, allocation, profiling and leaks | [performance.md](references/performance.md) |
| Logs, stacktraces, reproduction and runtime diagnostics | [debugging.md](references/debugging.md) |
| Version ports, deprecations, compatibility and publishing | [migration-release.md](references/migration-release.md) |
| Test layers, artifact inspection and acceptance evidence | [testing-validation.md](references/testing-validation.md) |
| Reusable composition, state and integration patterns | [common-patterns.md](references/common-patterns.md) |
| Stop conditions and discouraged approaches | [anti-patterns.md](references/anti-patterns.md) |

## Tool boundaries

The inspection script uses deterministic text evidence to accelerate discovery; verify every conclusion in context. The validation script builds through the repository's wrapper when present and performs static artifact checks; it deliberately prints the real-server gates it cannot prove. Read either script before modifying it for unusual layouts.

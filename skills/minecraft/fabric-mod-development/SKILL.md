---
name: fabric-mod-development
description: Analyze, implement, debug, test, and migrate Fabric Minecraft mods while preserving repository conventions and exact Minecraft, mappings, Loader, Loom, and Fabric API compatibility. Use for Fabric projects involving registries, events, mixins or class tweakers, networking, persistence, data generation, client rendering, configuration, tests, builds, releases, or version ports.
---

# Fabric Mod Development

## Overview

Make maintainable changes; never guess APIs or cross client/server boundaries. Use repository and resolved dependency versions as evidence, plus matching official docs/Javadocs to choose an extension point.

## Mandatory Workflow

Follow this sequence without skipping ahead:

**Understand → Analyze → Plan → Implement → Validate → Summarize**

Before editing, require Understand and Analyze evidence to identify the affected lifecycle, logical side, project convention, and exact API version.

### 1. Understand the Repository

1. Read repository instructions, contributor docs, and the request.
2. Inspect working-tree status. Preserve unrelated and user-authored changes.
3. Run `python scripts/inspect_fabric_project.py <project-root>` from this skill directory when available.
4. Inspect rather than list:
   - Gradle settings, wrapper, plugins, properties, repositories, dependencies, source sets, run configurations, and publishing tasks.
   - Every source `fabric.mod.json`, including environment, entrypoints, dependencies, mixins, class tweaker/access widener, and custom lifecycle metadata.
   - Common, client, server, test, game-test, datagen, generated-resource, and resource-pack/data-pack roots.
   - Initializers, registration holders, callbacks, networking setup, persistence, configuration, rendering, mixins, utilities, and tests relevant to the request.
5. Find the nearest analogous feature and trace its complete path from initialization through runtime behavior and resources.
6. Record a version contract: Minecraft version, Java version, mapping namespace, Loader, Loom, Fabric API, relevant third-party modules, and physical/logical side.

Resolve indirect versions from the Gradle model, lock/catalog, or dependency report; never infer them from package names or memory.

### 2. Analyze Before Planning

Build an evidence-backed change model:

- Identify the state owner and lifecycle point that creates, mutates, synchronizes, saves, and disposes it.
- Separate physical environment from logical side. The logical server owns authoritative game state, including in single-player.
- Mark every client-only type and ensure common code cannot load it on a dedicated server.
- Determine which files are source-authored and which are generated.
- Reuse local identifiers, helpers, registration patterns, codecs, packet abstractions, logging, configuration, and test fixtures.
- Check the exact-version official docs, dependency Javadocs, or source for every unfamiliar signature. Never invent or interpolate an API.
- Classify selected APIs from their annotations, Javadocs, module lifecycle metadata, and changelog—not from suffixes such as `v0` or `v1`.

Choose the narrowest supported extension point in this order:

1. Existing project abstraction or utility.
2. Vanilla registry, resource/data-pack mechanism, data component, `SavedData`, or object override.
3. Stable Fabric API callback or event.
4. Version-matched third-party API already used by the project.
5. Experimental API with explicit risk acceptance and containment.
6. Focused Mixin or class tweaker/access widener only when no supported hook exists.

Read [architecture.md](references/architecture.md) for lifecycle and side analysis, and [extension-points.md](references/extension-points.md) before adding a hook, Mixin, or unstable dependency.

### 3. Plan

State behavior, files, initialization path, side/thread ownership, compatibility risks, validation commands, and resource/generated-output changes. Keep the plan within scope.

For risky or ambiguous behavior, establish a failing reproduction or test first. If the API cannot be verified for the version contract, pause implementation and report missing evidence.

### 4. Implement

- Make the smallest coherent change and follow repository naming, packaging, formatting, and initialization conventions.
- Keep bootstrap declarative: register objects, callbacks, payload types, and providers; perform runtime work in the appropriate callback.
- Use namespaced identifiers and explicit initialization paths; never depend on accidental class loading.
- Keep client-only entrypoints, renderers, screens, key bindings, and client receivers in client source sets when the project supports split sources.
- Validate all client-to-server input and mutate game state on the logical server.
- Schedule mutations onto the game thread when callback documentation does not guarantee it.
- Prefer data-driven resources and datagen where the project does; regenerate outputs instead of hand-editing generated files.
- Preserve other mods' behavior: compose through events and resource mechanisms instead of replacing global behavior.
- Keep Mixins narrow, uniquely named, documented by missing hook, and free of copied vanilla logic when an injection suffices.

Load only task-relevant references:

| Task | Reference |
| --- | --- |
| Build/source layout, manifest, datagen | [project-workflow.md](references/project-workflow.md) |
| Items, blocks, entities, resources, state, config | [content-and-data.md](references/content-and-data.md) |
| Blocks and creative inventory | [content-and-data.md](references/content-and-data.md) + [extension-points.md](references/extension-points.md) |
| Packets, synchronization, authority | [networking.md](references/networking.md) |
| Client-only code and rendering | [client-rendering.md](references/client-rendering.md) |
| Tests, diagnosis, production artifact, release | [testing-debugging-release.md](references/testing-debugging-release.md) |
| Version upgrades or mapping changes | [versions-and-migrations.md](references/versions-and-migrations.md) |
| Cross-cutting review checklist | [best-practices.md](references/best-practices.md) |
| Unfamiliar Fabric terms | [glossary.md](references/glossary.md) |

### 5. Validate in Risk Order

Use the repository wrapper and existing tasks; list Gradle tasks instead of assuming names.

1. Run the narrowest relevant unit or compilation check.
2. Run format/static analysis configured by the repository.
3. Run datagen when providers or generated resources changed; inspect generated diff.
4. Run unit tests and applicable server/client game tests.
5. Run the full build and inspect the production JAR's manifest, entrypoints, mixins, class tweaker/access widener, and resources when packaging changed.
6. Exercise affected environments: dedicated server for common/server or cross-side work; physical client and integrated server for client/cross-side work.
7. Review the final diff for unintended generated files, stale resources, duplicate registration, client leakage, and unrelated changes.

Do not claim runtime paths were tested based on compilation alone; explain checks that could not run.

## Debugging and migration

For failures, reproduce the smallest case, classify it, trace the first project-owned frame against resolved dependencies, test one hypothesis, then rerun the failing path and nearest regression check. Read `references/testing-debugging-release.md` for symptom routing and evidence.

For version ports, read `references/versions-and-migrations.md`. Keep build contract, names/signatures, behavior, and validation separate; never mix source and target mapping names. Remove temporary diagnostics and rerun the regression path.

For block additions, check the creative inventory callback in `references/extension-points.md`; packet and renderer requests use task-specific routes above.

## Important Rules

- Use exact-version official sources; record conflicts; local style cannot justify removed, internal, or wrong-version APIs.
- Keep Fabric implementation packages out of public APIs unless the task requires it and the repository accepts that coupling; never suppress deprecation/experimental warnings without documenting acceptable risk.
- Do not add dependencies, repositories, global hooks, Mixins, or duplicated utilities when an existing supported path solves the task.
- Summarize changed behavior, architectural fit, validation evidence, and remaining risks.

---
name: fabric-mod-development
description: Analyze, implement, debug, test, and migrate Fabric Minecraft mods while preserving repository conventions and exact Minecraft, mappings, Loader, Loom, and Fabric API compatibility. Use for Fabric projects involving registries, events, mixins or class tweakers, networking, persistence, data generation, client rendering, configuration, tests, builds, releases, or version ports.
---

# Fabric Mod Development

## Overview

Make maintainable changes to unfamiliar Fabric repositories without guessing APIs or crossing client/server boundaries. Treat the repository and its resolved dependency versions as evidence, then use matching official documentation and Javadocs to choose an extension point.

## Mandatory Workflow

Follow this sequence without skipping ahead:

**Understand → Analyze → Plan → Implement → Validate → Summarize**

Do not edit code until the Understand and Analyze evidence is sufficient to name the affected lifecycle, logical side, existing convention, and exact API version.

### 1. Understand the Repository

1. Read repository instructions, contributor documentation, and the current request.
2. Inspect working-tree status. Preserve unrelated and user-authored changes.
3. Run `python scripts/inspect_fabric_project.py <project-root>` from this skill directory when available.
4. Inspect, rather than merely list:
   - Gradle settings, wrapper, plugins, properties, repositories, dependencies, source sets, run configurations, and publishing tasks.
   - Every source `fabric.mod.json`, including environment, entrypoints, dependencies, mixins, class tweaker/access widener, and custom lifecycle metadata.
   - Common, client, server, test, game-test, datagen, generated-resource, and resource-pack/data-pack roots.
   - Initializers, registration holders, callbacks, networking setup, persistence, configuration, rendering, mixins, utilities, and tests relevant to the request.
5. Find the nearest analogous feature and trace its complete path from initialization through runtime behavior and resources.
6. Record a version contract: Minecraft version, Java version, mapping namespace, Loader, Loom, Fabric API, relevant third-party modules, and physical/logical side.

If any version is indirect, resolve it from the Gradle model, lock/catalog, or dependency report. Do not infer it from package names or memory.

### 2. Analyze Before Planning

Build an evidence-backed change model:

- Identify the owner of state and the lifecycle point that creates, mutates, synchronizes, saves, and disposes it.
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

State the intended behavior, files, initialization path, side/thread ownership, compatibility risks, and validation commands. Include resource or generated-output changes. Keep the plan no broader than the request.

For risky or ambiguous behavior, establish a failing reproduction or test first. If the API cannot be verified for the version contract, pause implementation and report what evidence is missing.

### 4. Implement

- Make the smallest coherent change and follow repository naming, packaging, formatting, and initialization conventions.
- Keep bootstrap code declarative: register objects, callbacks, payload types, and providers; do runtime work in the appropriate callback.
- Use namespaced identifiers and explicit initialization paths. Do not depend accidentally on class loading.
- Keep client-only entrypoints, renderers, screens, key bindings, and client receivers in client source sets when the project supports split sources.
- Validate all client-to-server input and mutate game state on the logical server.
- Schedule mutations onto the game thread when callback documentation does not guarantee it.
- Prefer data-driven resources and datagen where the project does. Regenerate outputs rather than hand-editing generated files.
- Preserve other mods' behavior: compose through events and resource mechanisms instead of replacing global behavior.
- Keep Mixins narrow, uniquely named, documented by missing hook, and free of copied vanilla logic when an injection suffices.

Load only task-relevant references:

| Task | Reference |
| --- | --- |
| Build, source layout, manifest, datagen | [project-workflow.md](references/project-workflow.md) |
| Items, blocks, entities, resources, state, config | [content-and-data.md](references/content-and-data.md) |
| Packets, synchronization, authority | [networking.md](references/networking.md) |
| Client-only code and rendering | [client-rendering.md](references/client-rendering.md) |
| Tests, diagnosis, production artifact, release | [testing-debugging-release.md](references/testing-debugging-release.md) |
| Version upgrades or mapping changes | [versions-and-migrations.md](references/versions-and-migrations.md) |
| Cross-cutting review checklist | [best-practices.md](references/best-practices.md) |
| Unfamiliar Fabric terms | [glossary.md](references/glossary.md) |

### 5. Validate in Risk Order

Use the repository's wrapper and existing tasks. Do not assume task names when Gradle can list them.

1. Run the narrowest relevant unit or compilation check.
2. Run format/static analysis configured by the repository.
3. Run datagen when providers or generated resources changed; inspect the generated diff.
4. Run unit tests and applicable server/client game tests.
5. Run the full build and inspect the production JAR's manifest, entrypoints, mixins, class tweaker/access widener, and resources when packaging changed.
6. Exercise the affected environment: dedicated server for common/server work, physical client and integrated server for client or cross-side work.
7. Review the final diff for unintended generated files, stale resources, duplicate registration, client leakage, and unrelated changes.

Do not claim a runtime path was tested if only compilation succeeded. Explain any check that could not run.

## Debugging Workflow

1. Reproduce with the smallest relevant run configuration and capture the full crash report or `latest.log` context.
2. Classify the failure: version/mapping mismatch, initialization order, registry/resource error, physical-side class loading, logical-side authority, wrong thread, Mixin application, packet registration, stale generated data, or dependency conflict.
3. Trace the first project-owned frame and verify its API against the resolved dependency, not current documentation by default.
4. Reduce to one hypothesis; add targeted logging, breakpoint, assertion, or test.
5. Fix the cause, remove temporary diagnostics, and rerun the failing path plus the nearest regression check.

Use [testing-debugging-release.md](references/testing-debugging-release.md) for symptom routing.

## Migration Workflow

Treat migration as four explicit passes:

1. Build contract: wrapper, Java, Loom, Loader, Fabric API, dependencies, and repositories.
2. Names and signatures: target mapping namespace, official migration guide, compiler failures, and deprecated replacements.
3. Behavior: lifecycle, networking, rendering, registries, persistence, resources, and side assumptions.
4. Validation: datagen, tests, dedicated server, client/integrated server, and production JAR.

Do not combine source and target mapping names. Upgrade in reviewable stages and keep mechanical renames separate from behavior changes where practical. The 1.21.11-to-26.1 transition changes obfuscation, mappings, Loom configuration, and Java requirements; always read [versions-and-migrations.md](references/versions-and-migrations.md) before crossing it.

## Behavioral Examples

- **Add a block:** first find the repository's block/item holders, identifier helper, creative-tab event, datagen providers, and initializer call; then mirror that path and validate generated assets and both runtime sides.
- **Fix a packet bug:** verify payload registration on both physical sides, receiver placement, logical-server validation, and game-thread mutation before changing the codec or handler.
- **Port a renderer:** lock the target Minecraft/Fabric versions, read the matching rendering migration notes, keep client code isolated, and validate extraction/draw phases in a client run.

## Important Rules

- Prefer exact-version official documentation, official examples on the matching branch/tag, resolved Javadocs/source, migration guides, and changelogs—in that order. Community examples are leads, not authority.
- If official guidance conflicts with community code, follow the official source and record the discrepancy when it affects the result.
- Existing project style governs structure, but it cannot make a removed, internal, or wrong-version API valid.
- Never use Fabric implementation packages as public API unless the repository deliberately accepts that coupling and the task requires it.
- Never suppress deprecation or experimental warnings without documenting why the risk is acceptable.
- Never add a dependency, repository, global hook, Mixin, or duplicated utility when an existing supported path solves the task.
- Summarize changed behavior, architectural fit, validation evidence, and remaining risks—not a diary of edits.

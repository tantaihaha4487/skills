# Project and Build Workflow

Use this reference when creating or restructuring a project, changing Gradle or metadata, generating resources, or inspecting an artifact.

## Establish the Build Contract

Read these as one contract rather than in isolation:

- Gradle wrapper and settings.
- Root and included build scripts.
- `gradle.properties`, version catalog, locks, and CI overrides.
- Loom plugin ID/version and mapping declaration.
- Java toolchain and compiler target.
- Loader, Fabric API, Minecraft, mappings, and mod dependencies.
- `fabric.mod.json` version placeholders and Gradle resource expansion.

Use the wrapper (`./gradlew`) so the repository-selected Gradle version runs. Ask Gradle for tasks or dependencies rather than guessing custom task names.

Do not add repositories casually. Loom supplies the standard Minecraft/Fabric/Mojang and central dependency sources needed by ordinary projects; additional repositories should correspond to a real dependency and existing policy.

## Creation and Layout

For a new repository, start from the official Fabric template generator or the matching branch of the official example mod. For an existing repository, preserve its established packages, source sets, identifier helper, registration holders, and generated-resource policy.

Keep `fabric.mod.json` in a source resources root. Verify:

- `id`, `version`, `environment`, entrypoints, dependencies, and contact/license metadata.
- Mixin configuration paths and client/common partitioning.
- The manifest field for the class tweaker/access widener when one exists.
- Resource expansion matches actual Gradle property names.

Never edit `build/resources`, `.gradle`, remapped caches, IDE output, or JAR contents as source.

## Mapping and Loom Modes

The plugin and tasks are version-sensitive:

| Target | Typical Loom plugin | Mappings | Production task |
| --- | --- | --- | --- |
| 1.21.11 and older | `net.fabricmc.fabric-loom-remap` | Yarn or another mapping dependency | `remapJar`/`build` |
| 26.1 and newer | `net.fabricmc.fabric-loom` | Minecraft official names; no mappings dependency | `jar`/`build` |
| Legacy projects | `fabric-loom` | Inspect project | Inspect project |

This table is a routing rule, not a reason to rewrite a working legacy build during an unrelated change.

## Data Generation

Inspect Loom's datagen configuration, the `fabric-datagen` entrypoint, provider registration, and output directory together. Add a provider to the existing pack rather than creating a parallel pipeline.

When data-driven content changes:

1. Modify providers or source resources according to repository policy.
2. Run the configured datagen task, commonly `runDatagen`.
3. Review generated JSON semantically and for unintended deletions.
4. Ensure the generated directory is included as a resources source set.

Do not hand-maintain a generated file unless the repository explicitly treats it as source.

## Artifact Inspection

The full build should produce the distributable JAR under the configured build directory, commonly `build/libs`. When packaging changes, inspect the JAR rather than assuming source layout survived processing:

- expanded `fabric.mod.json`;
- entrypoint class names;
- Mixin JSON and refmaps where applicable;
- class tweaker/access widener;
- assets, data, and generated resources;
- nested JARs and dependency inclusion policy;
- accidental development-only files.

## Official Sources

- [Creating a Fabric project](https://docs.fabricmc.net/develop/getting-started/creating-a-project)
- [Fabric project structure](https://docs.fabricmc.net/develop/getting-started/project-structure)
- [Building a Fabric mod](https://docs.fabricmc.net/develop/getting-started/building-a-mod)
- [Fabric Loom documentation](https://docs.fabricmc.net/develop/loom/)
- [1.21.11 Loom documentation](https://docs.fabricmc.net/1.21.11/develop/loom/)
- [Data generation setup](https://docs.fabricmc.net/develop/data-generation/setup)
- [Official Fabric example mod](https://github.com/FabricMC/fabric-example-mod)

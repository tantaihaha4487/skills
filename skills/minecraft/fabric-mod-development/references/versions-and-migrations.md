# Versions, Deprecations, and Migrations

Use this reference for every Minecraft, Java, mapping, Loom, Loader, or Fabric API upgrade and whenever an example's names differ from the project.

## Source Resolution Order

1. Exact target-version official Fabric documentation.
2. Official example on a matching branch/tag.
3. Resolved dependency Javadocs and source JARs.
4. Official migration guide, release announcement, changelog, and repository history.
5. Existing repository conventions after confirming they remain valid.

Current docs may default to a newer Minecraft release. Use the documentation version selector and check the version banner on every copied signature. Documentation examples can also be rendered in a different mapping namespace; identify the project's namespace before translating names.

## API Status Workflow

For every compiler deprecation or proposed new module:

1. Read the annotation and complete Javadoc, including replacement and removal timing.
2. Inspect the owning Fabric API module's lifecycle metadata.
3. Search the exact target branch's official migration notes and changelog.
4. Find a matching official example or source use.
5. Prefer the supported replacement and add a compatibility abstraction only when the repository genuinely spans versions.

Do not equate a `v0` suffix with experimental status. Do not import `net.fabricmc.fabric.impl` to bypass a missing public API.

## Migration Passes

### 1. Build Contract

Update one coherent matrix: Gradle wrapper, Java toolchain, Minecraft, Loom, Loader, Fabric API, mappings, and third-party dependencies. Refresh dependencies only when needed and inspect the resolved graph.

### 2. Mappings and Compilation

Run Loom's mapping migration tool when supported, but treat output as a draft. Compile early. Keep mechanical symbol changes separate from behavioral fixes where practical. Kotlin and complex Mixins may need specialized tooling or manual inspection.

### 3. Behavioral Ports

Review registries, events, packets/codecs, rendering phases, resources/data components, persistence, commands, Mixins, and class tweakers. A compiling callback can still execute on a different phase or side.

### 4. Runtime and Artifact Validation

Regenerate data, run tests, launch a dedicated server and client/integrated server, and inspect the production JAR. Test migration of old saves/config where the schema changed.

## The 1.21.11 → 26.1 Boundary

Minecraft 1.21.11 is the final obfuscated release supported by the traditional Yarn/Intermediary pipeline. Minecraft 26.1 begins the unobfuscated era. Treat this as a build-system and source-contract migration, not an ordinary version bump.

| Concern | 1.21.11 and older | 26.1 and newer |
| --- | --- | --- |
| Java | Commonly Java 21 for 1.21.x; verify exact target | Java 25 for 26.1 |
| Loom plugin | `net.fabricmc.fabric-loom-remap` (legacy `fabric-loom` exists) | `net.fabricmc.fabric-loom` |
| Names | Yarn/selected mapping dependency | Official unobfuscated Minecraft names |
| Dependency config | `modImplementation` common | Normal `implementation`/`api` patterns |
| Production task | Remapping, commonly `remapJar` | Normal `jar` |
| Class-tweaker namespace | Commonly `named` | `official` |

Recommended path: first migrate the 1.21.11 project from Yarn to Mojang names while still on 1.21.11, validate, then port to 26.1 using the official guide. All code interacting with Minecraft must be recompiled; an older binary is not forward-compatible merely because source names look similar.

## Selected 1.21.11 Review Areas

Official 1.21.11 notes call out changes including game-rule registration, renewed World Render Events, larger custom-payload support, and recipe synchronization. Use the release notes as a routing index, then inspect the exact API source/Javadocs for the feature being ported.

## Official Sources

- [Fabric porting overview](https://docs.fabricmc.net/develop/porting/)
- [Migrating mappings for 26.1](https://docs.fabricmc.net/develop/porting/mappings)
- [Fabric API 26.1 migration guide](https://docs.fabricmc.net/develop/porting/fabric-api)
- [1.21.11 Loom documentation](https://docs.fabricmc.net/1.21.11/develop/loom/)
- [Current Loom documentation](https://docs.fabricmc.net/develop/loom/)
- [Fabric 1.21.11 release announcement](https://fabricmc.net/2025/12/05/12111.html)
- [Fabric API source and changelog](https://github.com/FabricMC/fabric)

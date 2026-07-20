# Project architecture

## Load this reference when

Load this file before creating a plugin, changing module boundaries, adding dependencies, altering build logic, or choosing an output artifact. For lifecycle-only or descriptor-only work, load the narrower reference instead.

## Preserve the repository as the authority

Paper defines plugin entrypoints, descriptors, lifecycle contracts, and API dependencies. It does not prescribe a universal package tree, dependency-injection framework, command architecture, or test framework.

Before proposing architecture:

1. Identify the Gradle or Maven wrapper and required Java toolchain.
2. Map root and module build files, convention plugins, buildSrc or build-logic, and version catalogs.
3. Distinguish deployable plugin modules from shared API, common, platform-adapter, and test modules.
4. Locate the descriptor source or generator, resource processing, and placeholder expansion.
5. Trace the runtime plugin-dependency graph separately from Java library dependencies.
6. Identify shading, relocation, service-file merging, remapping, and the final publishable artifact task.
7. Record existing package, ownership, configuration, logging, testing, CI, and release conventions.

Do not migrate Maven to Gradle, flatten modules, add a framework, or replace established abstractions unless the task requires it. Paper recommends Gradle and develops Gradle-oriented tooling, but Maven remains supported.

## Official baseline for a new plugin

For a greenfield plugin with no repository conventions, start from Paper's minimal build shape rather than inventing feature layers:

```text
project/
├── settings.gradle.kts
├── build.gradle.kts
├── gradlew and gradle/wrapper/
└── src/
    ├── main/
    │   ├── java/<unique reverse-domain package>/DescriptivePlugin.java
    │   └── resources/plugin.yml
    └── test/java/                         # only when tests are added
```

Use the Java toolchain required by the selected Paper target, declare Paper API as `compileOnly`, and keep a single descriptive `JavaPlugin` entrypoint. Gradle Kotlin DSL is the documented default; use Maven with `provided` scope when project constraints choose Maven. Add packages and modules only when feature ownership or target separation requires them. For an existing repository, this scaffold is context, not a migration instruction.

## Architecture summary

Produce this evidence before implementation:

- **Build:** wrapper, build system, Java toolchain, relevant plugins, and repository declarations.
- **Artifacts:** modules that produce plugin JARs, their descriptors, and the task that creates each deployable artifact.
- **Entrypoints:** JavaPlugin, bootstrap, loader, commands, listeners, and services already present.
- **State ownership:** configuration, caches, databases, tasks, executors, and external integrations.
- **Compatibility:** declared Paper/Minecraft range, API version, mappings strategy, optional dependencies, and Folia claim.
- **Extension point:** existing abstraction to reuse and the smallest coherent change boundary.
- **Unknowns:** facts that require build output or runtime verification.

If the repository contradicts a generic layout, follow the repository unless it violates a current API contract.

## Build and dependency decisions

| Requirement | Default decision |
| --- | --- |
| Public Paper API | Declare compile-only in Gradle or provided in Maven. Never package Paper or Bukkit into the plugin. |
| Runtime plugin API | Compile against it without bundling it, and represent required or optional availability in the plugin descriptor. |
| Ordinary third-party library | Preserve the repository's existing runtime-library or shade/relocate strategy. |
| Maven Central library without self-contained-JAR requirement | Consider plugin.yml libraries if runtime resolution is acceptable. |
| Self-contained artifact | Use the repository's shading and relocation conventions; verify the final artifact and service metadata. |
| Paper or Minecraft internals | Stop and apply the decision gate in paperweight-internals.md. |
| Cross-plugin service | Prefer an explicit shared interface and Bukkit ServicesManager when that matches the repository. |

Dependency declarations, descriptor relationships, and runtime behavior must agree. An optional integration must survive absence. A hard dependency should prevent startup when absent rather than fail later.

## Multi-module rules

- Do not assume every module is independently deployable.
- Keep shared modules free of accidental server-version coupling unless they are explicit adapters.
- Keep descriptors at the root of the plugin artifact, not merely in a source module.
- Apply build plugins where their tasks are needed; do not duplicate versions across modules when the repository centralizes them.
- Verify which JAR is consumed by run tasks, CI, and publishing. Intermediate plain JARs may not contain shaded dependencies or remapped classes.
- When version-specific internals are unavoidable, prefer a stable common contract plus isolated adapter modules over conditional NMS references throughout the codebase.

Official Paper examples use both filtered resource descriptors and generated descriptors. Inspect processResources, resource generators, and generated-source directories before editing. Modify the source of truth, never build or target output.

## Traps

- Creating command, listener, manager, or utility packages because they are conventional rather than because the repository uses them.
- Naming the only entrypoint Main or making multiple ordinary classes extend JavaPlugin.
- Packaging Paper API or a runtime plugin API into the output.
- Adding global static access when the repository already has explicit ownership or composition.
- Copying current documentation dependency literals into a long-lived reference.
- Assuming the plain jar task is the release artifact.
- Editing a generated descriptor.
- Treating a successful compile as proof that the artifact loads.

## Required evidence

Architecture work is ready only when:

- the relevant wrapper resolves the project;
- every affected module compiles;
- the production artifact task succeeds;
- the selected JAR contains the intended root descriptor and entrypoint classes;
- resource placeholders are resolved;
- Paper/Bukkit API is absent from bundled classes;
- shaded libraries, relocation, and META-INF services match the build design;
- a real target server loads the artifact when runtime behavior changed.

## Official sources

- [Paper project setup](https://docs.papermc.io/paper/dev/project-setup/)
- [How Paper plugins work](https://docs.papermc.io/paper/dev/how-do-plugins-work/)
- [plugin.yml](https://docs.papermc.io/paper/dev/plugin-yml/)
- [Paper plugins](https://docs.papermc.io/paper/dev/getting-started/paper-plugins/)
- [Paperweight test plugin](https://github.com/PaperMC/paperweight-test-plugin)
- [Paperweight multi-project example](https://github.com/PaperMC/paperweight-test-plugin/tree/multi-project)
- [Paper test-plugin build](https://github.com/PaperMC/Paper/blob/main/test-plugin/build.gradle.kts)

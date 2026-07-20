# Migration, compatibility, and release

## Contents

[Scope](#load-this-reference-when) · [Version authorities](#establish-version-authorities) · [Sources](#migration-source-order) · [Workflow](#migration-workflow) · [Boundaries](#dated-compatibility-boundaries) · [Release](#release-decisions) · [Traps](#traps) · [Evidence](#required-evidence)

## Load this reference when

Load this file for a Paper or Minecraft version change, Java toolchain change, API deprecation, Adventure migration, mapping transition, compatibility claim, version bump, CI release, or Hangar publication.

## Establish version authorities

Keep these concepts separate:

- **Plugin version:** repository-defined release identity.
- **Paper API dependency:** compile target.
- **api-version:** minimum server API accepted by the descriptor.
- **Java toolchain or release:** bytecode and build requirement.
- **Runtime test matrix:** server versions actually exercised.
- **Distribution platform range:** compatibility claimed to users.
- **Mappings or remapping target:** relevant only when internals are used.

Do not make one value imply the others. Preserve the repository's version source, tagging scheme, and release channel unless the task explicitly changes them.

## Migration source order

Resolve migration decisions in this order:

1. Repository support policy and currently declared versions.
2. Javadocs and deprecated list for each target version.
3. Official documentation, including any page version banner.
4. Official Paper release announcements and migration material.
5. Official Paper source or history when documentation does not settle behavior.
6. Compile and runtime evidence across the claimed matrix.

Never update an old maintenance branch to the newest API merely because it exists.

## Migration workflow

1. Record the current and target Paper, Minecraft, Java, API, mappings, and plugin versions.
2. Inventory public API, internal API, descriptor, dependency, resource, and CI surfaces affected.
3. Read the target deprecated list and replacements before changing calls.
4. Migrate public APIs first; isolate target-specific internal changes.
5. Update build and descriptor source-of-truth values together.
6. Compile with deprecation warnings visible.
7. Test the minimum and latest claimed targets, not only the compile target.
8. Update publication ranges only after runtime proof.

Do not suppress a deprecation without a documented compatibility reason. Scheduled-for-removal APIs need a migration plan.

## Dated compatibility boundaries

These are historical boundaries, not floating current defaults:

- **Minecraft 1.20.5:** Paper moved to a Mojang-mapped runtime and removed CraftBukkit package version relocation.
- **Paper 26.1:** API artifact versions changed to include an explicit build component, server JARs became unobfuscated, and the old reobfuscation release path ceased to work.
- **Paper 26.2:** previously deprecated Adventure APIs and other deprecated surfaces were removed; consult the release announcement and target Javadocs rather than assuming source compatibility.

For current dependency or tooling literals, consult the live official setup pages during the task. Do not freeze latest build numbers in the skill.

## Release decisions

- Run repository-native verification and produce the actual deployable artifact.
- Inspect the JAR before publication.
- Ensure build version, expanded descriptor version, artifact, tag, and release metadata agree where the repository expects them to.
- Keep credentials only in CI secrets.
- Publish snapshots or ongoing builds through a snapshot channel, not as stable releases.
- Set Hangar platform ranges and dependencies from tested behavior.
- Preserve the project's existing artifact selection: plain, shaded, or target-specific. Never infer it from filename alone.
- Re-read current Hangar documentation before editing workflow action or Java-version literals because examples age independently from the plugin.

Paper does not mandate semantic versioning, tag format, branch model, or a universal CI workflow. Reuse repository policy.

## Traps

- Raising api-version to the compile target while still claiming older servers without testing.
- Treating api-version as a maximum or as the plugin's own version.
- Updating the API dependency without reviewing Java requirements and deprecations.
- Publishing an intermediate plain JAR instead of the shaded or target-specific artifact.
- Publishing a reobfuscated artifact for Paper 26.1 or later.
- Broadening a Hangar compatibility range based only on compilation.
- Copying an old workflow's Java or action versions.
- Claiming backward compatibility while classes or descriptor metadata require a newer API.
- Using current Paper behavior to reason about an older supported target.

## Required evidence

Before release, retain:

- clean wrapper-based checks and production build;
- warning and deprecation review;
- artifact inspection results;
- real-server startup, feature, disable, and restart results;
- minimum/latest target results for a compatibility range;
- separate Folia result if claimed;
- dependency-present and optional-dependency-absent results;
- final version agreement across build, descriptor, artifact, tag, and publication metadata;
- publication or workflow URL and resulting artifact identity when release was requested.

## Official sources

- [Paper project setup](https://docs.papermc.io/paper/dev/project-setup/)
- [Paper Java requirements](https://docs.papermc.io/paper/getting-started/)
- [Paper roadmap and deprecation policy](https://docs.papermc.io/paper/dev/roadmap/)
- [Paper Javadocs version index](https://jd.papermc.io/paper/) — select each target and open its deprecated list
- [Adventure migration index](https://docs.papermc.io/adventure/migration/) — select the source and target major versions
- [Paper 26.1 announcement](https://papermc.io/news/26-1/)
- [Paper 26.2 announcement](https://papermc.io/news/26-2/)
- [Hangar publishing](https://docs.papermc.io/misc/hangar-publishing/)

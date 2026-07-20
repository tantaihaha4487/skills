# paperweight and Minecraft internals

## Load this reference when

Load this file only when a task touches net.minecraft classes, CraftBukkit implementation details, mappings, reflection over internals, version adapters, remapping, or a paperweight-userdev build.

## Apply the internals decision gate

Before accepting an internal dependency:

1. Search the target Paper API and Javadocs for a supported equivalent.
2. Check whether a lifecycle, registry, data-component, entity, inventory, or Adventure API removes the need.
3. State the behavior that cannot be implemented through public API.
4. Isolate the smallest internal boundary and define a public project-owned interface around it.
5. Determine the exact supported server line and mapping/runtime requirements.
6. Add focused compile and real-server validation for that boundary.

If a public API works, use it. Paper explicitly treats NMS as unstable and unsupported.

## paperweight-userdev rules

paperweight-userdev is Paper's supported Gradle development path for internals.

- Use the dev bundle appropriate to the repository's target version.
- The dev bundle already supplies the Paper API; do not add a duplicate direct API dependency.
- Follow the repository's plugin-management and version-centralization conventions.
- Paper supports only the current userdev line; refresh plugin setup from official documentation during maintenance.
- For older bundles whose setup needs a different JDK, configure paperweight's Java launcher separately from the project's compile toolchain.
- In a multi-project build, centralize the paperweight plugin version and apply it only to adapter modules that need internals.

If a Maven repository requires internals, do not silently migrate its build. Explain that Paper's supported userdev tooling is Gradle-based and ask for an architecture decision.

## Mapping and artifact decisions

Mapping behavior depends on the target, not on current defaults.

- Since Minecraft 1.20.5, Paper runs Mojang mappings and the CraftBukkit package is no longer version-relocated.
- Before 1.20.5, runtime mappings and CraftBukkit relocation require target-specific handling.
- Since Paper 26.1, server artifacts are unobfuscated and reobfJar no longer produces a usable release strategy. Do not publish a reobfuscated plugin for 26.1 or later.
- For earlier targets, determine whether the repository requires Mojang-mapped Paper-only output or a reobfuscated artifact for a broader server target.

Never infer the server version from a versioned CraftBukkit package. Use the public version APIs.

## Contain instability

- Put NMS access in a narrow adapter, not domain, command, listener, or configuration code.
- Keep common modules independent of internal class names.
- Select adapters through an explicit compatibility mechanism already used by the project.
- Avoid caching mutable internal player or entity objects across lifecycle boundaries.
- Treat constructors, fields, methods, enum values, and serialization formats as version-specific.
- Cache reflective Field, Method, or MethodHandle lookups if reflection is unavoidable; paperweight cannot remap string-based reflective names.
- Do not use reflection solely to avoid compile-time evidence of an unsupported dependency.

The official paperweight multi-project example demonstrates common hooks plus version-specific modules, shading, service-file merging, and differing Java release targets. Reuse the idea only when the repository's support matrix warrants it.

## Traps

- Adding NMS before exhausting public APIs.
- Depending directly on a server implementation JAR without userdev.
- Keeping both a direct Paper API dependency and a dev bundle.
- Assuming current mappings apply to an older maintenance branch.
- Publishing reobfuscated output for 26.1 or later.
- Letting reflection or NMS spread through feature code.
- Assuming paperweight remaps reflection strings.
- Loading every possible version adapter into the same classloader without isolation.
- Copying a current userdev or dev-bundle literal into long-term skill instructions.

## Required evidence

For every internal change:

- compile the exact target adapter with the official dev bundle;
- run the repository's full production artifact task;
- inspect the artifact selected for that target and confirm its mapping strategy;
- start the exact target Paper line and execute the affected path;
- verify class loading before considering feature behavior;
- test clean disable and restart when internal objects are cached;
- compile and run every claimed target adapter after shared-interface changes;
- record the public-API search and why internals remain necessary.

## Official sources

- [Minecraft internals policy](https://docs.papermc.io/paper/dev/internals/)
- [paperweight-userdev](https://docs.papermc.io/paper/dev/userdev/)
- [paperweight test plugin](https://github.com/PaperMC/paperweight-test-plugin)
- [paperweight multi-project example](https://github.com/PaperMC/paperweight-test-plugin/tree/multi-project)
- [Paper 26.1 mapping and artifact changes](https://papermc.io/news/26-1/)
- [Bukkit version API](https://jd.papermc.io/paper/org/bukkit/Bukkit.html)

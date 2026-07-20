# Testing, Debugging, and Release

Use this reference to select evidence proportional to a change, diagnose runtime failures, and prepare a production artifact.

## Validation Layers

| Layer | Best for | Limitation |
| --- | --- | --- |
| Java compile/static checks | Signatures, mapping names, source-set isolation | Does not prove registration, resources, Mixins, or behavior |
| Loader-aware unit test | Codecs, algorithms, data transforms using Minecraft classes | Requires Fabric Loader JUnit/bootstrap for runtime-transformed classes and registries |
| Server game test | World interaction, registries, commands, persistence, server callbacks | Does not cover physical-client behavior |
| Client game test | Screens, input, rendering, end-to-end client behavior | API may be experimental for the target version; slower and environment-sensitive |
| Dedicated-server run | Client leakage, server initialization, resources, networking | Manual smoke run is not a behavioral assertion |
| Client/integrated run | Client initialization and both logical sides | Can hide dedicated-server-only class-loading failures |
| Full build/JAR inspection | Packaging, remapping, expanded metadata, resources | Does not execute the artifact's behavior |

Use Fabric Loader JUnit rather than plain JUnit when tests load Minecraft classes affected by the Loader/Mixin runtime. Bootstrap required vanilla registries exactly as the target test docs specify. Keep pure logic independent enough for ordinary unit tests where practical.

## Debugging Router

1. Capture the full crash report or `run/logs/latest.log`, resolved mod list, and the run configuration.
2. Find the earliest meaningful `Caused by` and first project-owned frame.
3. Route by signature:

| Evidence | Likely area |
| --- | --- |
| `ClassNotFoundException`/`NoClassDefFoundError` on server | Client-only type leaked into common code or missing runtime dependency |
| `NoSuchMethodError`/`NoSuchFieldError` | Compile/runtime dependency mismatch, wrong mapping-era snippet, or incompatible mod |
| Mixin target/injection failure | Wrong target version/mappings, conflicting transform, changed bytecode, or overly brittle injection |
| Duplicate/unbound registry key | Repeated registration, unstable identifier, or initializer path error |
| Missing model/texture/recipe/tag | Namespace/path, resource source set, generated output, or pack reload error |
| Unknown payload/decode failure | Packet type/codec registration or peer version mismatch |
| State resets after restart | Missing codec field, wrong storage scope, or missing `setDirty()` |
| Concurrent modification/wrong-thread exception | Callback thread assumption or unsafely shared state |

Use breakpoints and targeted debug logging. Include the mod ID in logger names/messages and keep noisy diagnostics at debug level. Remove temporary logs after the hypothesis is resolved.

Resource reload can refresh assets/data in supported contexts, but Java, Mixin, registry, and many initialization changes require a restart. Do not mistake a stale run for a failed source fix.

## Release Gate

Before publishing or handing off an artifact:

- confirm version, supported Minecraft/Loader ranges, environment, license, and dependency metadata;
- run the repository's full verification and production build;
- test the distributable JAR, not only development classes;
- inspect packaged metadata, Mixins/tweaker, nested dependencies, assets, data, and generated resources;
- verify dedicated-server and client compatibility claimed by metadata/README;
- review changelog and migration notes for user-visible or compatibility changes;
- use existing CI/publishing automation and repository credentials policy;
- do not publish externally without explicit authorization.

## Official Sources

- [Automatic testing with Fabric](https://docs.fabricmc.net/develop/automatic-testing)
- [Debugging Fabric mods](https://docs.fabricmc.net/develop/getting-started/debugging)
- [Launching the game](https://docs.fabricmc.net/develop/getting-started/launching-the-game)
- [Building a Fabric mod](https://docs.fabricmc.net/develop/getting-started/building-a-mod)
- [Fabric Loader JUnit repository](https://github.com/FabricMC/fabric-loader-junit)

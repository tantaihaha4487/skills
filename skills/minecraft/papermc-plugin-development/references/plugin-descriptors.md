# Plugin descriptors

## Load this reference when

Load this file when creating or changing plugin.yml, paper-plugin.yml, command or permission declarations, plugin dependencies, bootstrap or loader classes, library resolution, load order, or Folia metadata.

## Choose the descriptor deliberately

Use plugin.yml for an ordinary plugin unless the repository already uses the experimental Paper-plugin model or the feature requires an early bootstrap capability such as supported registry mutation or datapack discovery.

Do not introduce paper-plugin.yml merely because the server is Paper. Paper plugins remain experimental and are not drop-in replacements for Bukkit-style plugins.

Both descriptors can coexist for distinct purposes, but never duplicate metadata or entrypoints without confirming the official loading model and the repository's intent.

## plugin.yml decision rules

| Field | Decision |
| --- | --- |
| name, version, main | Required. Ensure the expanded version and named JavaPlugin class exist in the built JAR. |
| api-version | Set the minimum Paper API the code actually requires. Servers below it refuse the plugin. It is not the plugin version. |
| load | Keep the default post-world phase unless startup loading is required and all early lifecycle assumptions are valid. |
| depend | Use when absence must prevent plugin loading. |
| softdepend | Use when integration is optional; code must handle absence and late availability safely. |
| loadbefore | Use for ordering without declaring a hard dependency. |
| provides | Use only for an intentionally provided plugin capability or alias. |
| commands | Declare legacy command roots, descriptions, usage, aliases, and permissions consistently with executors. |
| permissions | Match runtime permission checks and defaults. |
| libraries | Consider for Maven Central runtime libraries when server-side resolution fits deployment policy. |
| folia-supported | Set true only after regionized-threading design and separate Folia validation. |

Check for dependency cycles. A descriptor cannot compensate for code that assumes an optional plugin is always present.

## Paper-plugin differences

paper-plugin.yml changes the loading model:

- bootstrap and server dependencies are separate;
- each dependency declares load ordering, requiredness, and classpath joining;
- omitted ordering is not deterministic;
- dependency cycles are fatal;
- classloader access is isolated and asymmetric unless explicitly joined;
- commands are registered programmatically through the command API;
- custom Bukkit serialization classes are not automatically registered;
- Paper plugins do not support server /reload.

Use PluginBootstrap only for work supported in the early bootstrap phase. General Bukkit calls can be unavailable there. BootstrapContext supplies the supported logger, data directory, configuration, and lifecycle access.

Use PluginLoader only when dynamic classpath construction is necessary. It is experimental and runs in a different classloader; static values written by the loader do not become plugin static state. For Maven Central dependencies, use Paper's documented mirror rather than treating Maven Central as a general runtime CDN.

## Descriptor source of truth

The checked-in YAML may be filtered, copied, or generated. Inspect:

- Gradle processResources or Maven resources configuration;
- generated-resource plugins;
- project version and API-version properties;
- the source set or module contributing the descriptor;
- shading and aggregation tasks.

Edit the upstream template or generator. Do not edit build output.

## Traps

- Treating api-version as the Minecraft versions the plugin promises to support.
- Declaring an optional dependency as hard, or softening one whose classes load unconditionally.
- Duplicating YAML commands after moving to Paper's programmatic command registration.
- Joining plugin classpaths without understanding which plugin can access which classes.
- Using paper-plugin.yml as an automatic modernization.
- Setting folia-supported to silence a loader warning.
- Leaving unresolved placeholders in the release JAR.
- Shipping multiple unintended descriptors from dependency or module aggregation.

## Required evidence

Inspect the final deployable JAR and prove:

- exactly the intended root descriptor or descriptors are present;
- all placeholders are resolved;
- main, bootstrap, and loader classes named by metadata exist;
- the plugin version matches the build's release authority;
- commands, permissions, dependency relationships, and libraries agree with code;
- a clean server accepts the descriptor and enables the plugin;
- required dependency absence fails as intended;
- optional dependency absence remains functional;
- Folia accepts and runs the plugin only when folia-supported is claimed.

## Official sources

- [plugin.yml reference](https://docs.papermc.io/paper/dev/plugin-yml/)
- [Paper-plugin model](https://docs.papermc.io/paper/dev/getting-started/paper-plugins/)
- [PluginBootstrap Javadocs](https://jd.papermc.io/paper/io/papermc/paper/plugin/bootstrap/PluginBootstrap.html)
- [PluginLoader Javadocs](https://jd.papermc.io/paper/io/papermc/paper/plugin/loader/PluginLoader.html)
- [Command registration](https://docs.papermc.io/paper/dev/command-api/basics/registration/)
- [Supporting Folia](https://docs.papermc.io/paper/dev/folia-support/)
- [Paper-plugin reload decision](https://github.com/PaperMC/Paper/issues/11743)

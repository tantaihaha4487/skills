# Plugin lifecycle and owned resources

## Contents

[Scope](#load-this-reference-when) · [Phases](#model-lifecycle-before-writing-code) · [Ownership](#ownership-rules) · [Services](#services-and-integrations) · [Configuration](#configuration-and-resources) · [Lifecycle API](#lifecycle-api) · [Traps](#traps) · [Evidence](#required-evidence)

## Load this reference when

Load this file for entrypoint changes, initialization, services, configuration ownership, schedulers, background work, reload behavior, or shutdown logic.

## Model lifecycle before writing code

| Phase | Safe purpose | Do not assume |
| --- | --- | --- |
| JavaPlugin construction | Ordinary Java field initialization and dependency storage only | A usable server API, worlds, services, or manually constructed plugin instances |
| Bootstrap | Early Paper-plugin registration explicitly supported by BootstrapContext | General Bukkit readiness; bootstrap APIs are experimental |
| onLoad | Minimal in-memory setup that does not require the running server | Most Bukkit operations; other plugins being enabled |
| onEnable | Compose owned services, load validated state, register listeners and commands, and open necessary resources | The server is already ticking or every world-dependent operation is appropriate |
| Running callbacks | Perform work in the callback's documented execution context | Main-thread safety for async callbacks or global-thread safety on Folia |
| onDisable | Stop intake, cancel or signal work, flush state, close resources, and detach external hooks | Complete initialization or automatic cleanup of plugin-created resources |

Paper constructs the JavaPlugin. Never instantiate it manually. Keep only the actual entrypoint subclassed from JavaPlugin.

## Ownership rules

The component that creates a resource must have an explicit shutdown path for it. Track:

- scheduler handles and lifecycle registrations;
- plugin-created threads and executor services;
- database connections and pools;
- files, sockets, clients, and other closeables;
- caches or pending write queues that require flushing;
- globally registered translation sources or external callbacks;
- services exposed to or acquired from other plugins.

Make shutdown idempotent and safe after partial enable failure. Do not dereference fields merely because normal startup assigns them.

Use the plugin logger. Prefer current plugin metadata APIs over deprecated description accessors.

## Services and integrations

Use ServicesManager when plugins exchange an interface implementation and the repository does not already define another integration mechanism.

- Register the provider with its owning plugin and priority.
- Load once and handle a null result.
- Do not check isProvidedFor and then call load; the provider can change between those calls.
- Represent required versus optional provider plugins in the descriptor.
- Release consumers and provider-owned resources during shutdown even when Paper also removes plugin registrations.

Avoid static plugin singletons as a substitute for ownership. If legacy code exposes one, do not expand its role without a repository-wide reason.

## Configuration and resources

- Store packaged defaults under the normal resource tree.
- Use saveDefaultConfig or saveResource with replacement disabled when preserving user edits.
- Validate required values before publishing configuration to live services.
- Explicitly save in-memory changes.
- Keep substantial file I/O off a tick-owning thread, then re-enter the correct server execution context before accessing Bukkit state.
- For Paper plugins, register custom ConfigurationSerializable classes before loading them.

reloadConfig only replaces the cached file configuration. It does not reconstruct commands, listeners, tasks, databases, services, or caches.

For a plugin-specific reload:

1. Parse into a candidate configuration.
2. Validate it completely.
3. Prepare replacement state without disturbing the live state.
4. Publish the new state atomically in the correct execution context.
5. Dispose replaced resources.
6. Keep the previous state active on failure.

Do not advertise support for server /reload. Paper plugins specifically do not support it, and ordinary plugins should not rely on it as a lifecycle test.

## Lifecycle API

Use Paper's Lifecycle API when the API being registered is lifecycle-aware, especially commands and registries. A handler registered through the plugin lifecycle manager follows plugin lifetime. Bootstrap registration is appropriate only for a Paper-plugin entrypoint that genuinely needs the earlier phase.

Lifecycle event monitors observe only; do not mutate from a monitor.

## Traps

- Calling server APIs from the constructor.
- Doing expensive network, database, or disk work on a tick-owning thread.
- Starting work before failure-safe cleanup has been established.
- Capturing entities, worlds, inventories, or plugin instances in long-lived asynchronous closures without an ownership plan.
- Treating async computation as permission to access Bukkit objects asynchronously.
- Registering duplicate listeners, commands, or tasks on a plugin-specific reload.
- Assuming scheduler cancellation closes executors, database pools, or external clients.
- Throwing from shutdown before later resources are released.

## Required evidence

For lifecycle-affecting changes, capture:

- clean startup and enable logs on a real target Paper server;
- registration evidence for changed commands, listeners, services, or lifecycle handlers;
- successful behavior after dependencies are present and, for optional integrations, absent;
- clean disable and restart without leaked tasks, threads, ports, or connection pools;
- persisted state reloaded after restart;
- failure-path behavior for invalid configuration or partial initialization;
- a distinct Folia runtime result when Folia is claimed.

## Official sources

- [How plugins work](https://docs.papermc.io/paper/dev/how-do-plugins-work/)
- [JavaPlugin Javadocs](https://jd.papermc.io/paper/org/bukkit/plugin/java/JavaPlugin.html)
- [Plugin Javadocs](https://jd.papermc.io/paper/org/bukkit/plugin/Plugin.html)
- [Lifecycle API](https://docs.papermc.io/paper/dev/lifecycle/)
- [Command lifecycle registration](https://docs.papermc.io/paper/dev/command-api/basics/registration/)
- [Plugin configuration](https://docs.papermc.io/paper/dev/plugin-configurations/)
- [ServicesManager Javadocs](https://jd.papermc.io/paper/org/bukkit/plugin/ServicesManager.html)
- [Paper-plugin reload decision](https://github.com/PaperMC/Paper/issues/11743)

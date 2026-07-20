# Architecture and Lifecycle

Use this reference to locate a change in Fabric's loading model and to prevent environment, lifecycle, and ownership errors.

## System Model

Fabric projects combine three independently versioned concerns:

- **Fabric Loader** discovers mods, resolves metadata/dependencies, transforms classes, and invokes entrypoints.
- **Fabric API** supplies opt-in modules containing interoperable hooks, events, helpers, and conventions.
- **Fabric Loom** configures the Gradle development environment, mappings/remapping where applicable, runs, Mixins, and production artifacts.

Do not treat “Fabric version” as a single value. Record Minecraft, Java, mappings, Loader, Loom, Fabric API, and relevant library versions separately.

## Initialization Flow

1. Loader discovers source-set output and nested dependency JARs.
2. It reads `fabric.mod.json`, resolves dependency and environment constraints, and discovers entrypoints, Mixins, and the class tweaker/access widener.
3. Class transforms are prepared before affected classes load.
4. Common `main` entrypoints initialize in every allowed physical environment.
5. Client entrypoints initialize only on a physical client; dedicated-server entrypoints initialize only on a physical dedicated server.
6. Registered callbacks execute later at their documented lifecycle points.

Initializers are bootstrap locations, not a signal that every other mod or every resource is ready. Entrypoint order between mods is generally not a dependency mechanism; declare dependencies and use lifecycle-specific callbacks instead.

## Physical Environment vs Logical Side

Analyze both dimensions:

| Runtime | Physical environment | Logical sides present |
| --- | --- | --- |
| Dedicated server | Server | Server |
| Multiplayer client | Client | Client |
| Single-player client | Client | Client and integrated server |

The logical server owns authoritative game state. A physical client is not equivalent to a logical client because it may host an integrated server. Use packets to cross logical sides; never mutate server-owned state directly from client input.

Client-only class isolation is a class-loading constraint, not just a runtime branch. A common class that mentions a client-only type can crash a dedicated server before the branch is evaluated. Prefer Loom split environment source sets and client entrypoints. Treat `@Environment` as documentation and stripping support, not a substitute for sound source-set boundaries.

## Common Repository Shapes

With split environment sources:

```text
src/main/java/          common code
src/main/resources/     shared metadata, assets, and data
src/client/java/        physical-client code
src/client/resources/   client-only resources when needed
src/test/java/          unit tests
src/gametest/java/      game tests when configured
src/main/generated/     common datagen output by convention
```

Older or unsplit repositories may keep client packages under `src/main/java`. Preserve the local layout unless restructuring is requested, but recognize that the compiler then cannot enforce client isolation.

## Ownership Questions

Before editing, answer:

- Which initializer makes the feature reachable?
- Which registry or event owns discovery?
- Which side owns the state?
- Which callback/thread may mutate it?
- Which codec/resource saves or transmits it?
- What unload, disconnect, dimension change, or reload invalidates it?
- Which other mods can observe or compose with it?

## Official Sources

- [Fabric Loader development documentation](https://docs.fabricmc.net/develop/loader/)
- [`fabric.mod.json` specification guide](https://docs.fabricmc.net/develop/loader/fabric-mod-json)
- [Fabric project structure](https://docs.fabricmc.net/develop/getting-started/project-structure)
- [Fabric networking and logical sides](https://docs.fabricmc.net/develop/networking)
- [Fabric example mod](https://github.com/FabricMC/fabric-example-mod)
- [`@Environment` Loader API Javadoc](https://maven.fabricmc.net/docs/fabric-loader-0.18.4/net/fabricmc/api/Environment.html)

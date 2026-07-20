# Fabric Terminology

Load this reference only when terminology in a repository or migration is ambiguous.

- **Access widener:** Older Fabric mechanism for widening access or mutability of vanilla members. Supported by older Loader/Loom stacks and generalized by class tweakers in newer stacks.
- **Class tweaker:** Loader 0.18+ transform description that can widen access and inject interfaces; configured through historically named access-widener manifest/Gradle fields.
- **Common code:** Code intended to load in every physical environment. It can contain logical-server and shared behavior but must not reference client-only types.
- **Data attachment:** Fabric API mechanism for attaching data to entities, block entities, worlds/levels, and chunks, optionally with persistence or synchronization. Its API lifecycle must be checked for the target version.
- **Data component:** Structured value associated with component-bearing objects such as `ItemStack`; modern replacement for many raw custom-NBT patterns.
- **Datagen:** A development run that executes providers to generate JSON/resources such as recipes, models, loot tables, and tags.
- **Entrypoint:** A `fabric.mod.json`-declared object Loader constructs and invokes for bootstrap, such as `main`, `client`, `server`, or `fabric-datagen`.
- **Environment:** The physical distribution running the code: client or dedicated server. Distinct from logical side.
- **Fabric API:** Modular public APIs and interoperability hooks maintained by Fabric. Module stability must be checked independently of its versioned suffix.
- **Fabric Loader:** Mod discovery, dependency resolution, class transformation, and entrypoint runtime.
- **Intermediary:** Stable obfuscated-era mapping layer historically used between Minecraft runtime names and development mappings; the traditional pipeline ends after 1.21.11.
- **Logical client:** Game logic presenting and predicting the player's local view.
- **Logical server:** Authoritative game simulation, present in both dedicated and integrated servers.
- **Loom:** Fabric's Gradle plugin for workspace setup, dependencies, mappings/remapping where needed, run configurations, Mixins, and packaging.
- **Mapping namespace:** Naming scheme used for Minecraft symbols, such as Yarn `named`, Intermediary, or post-26.1 `official` names.
- **Mixin:** Bytecode transformation system used to inject into or modify classes when supported extension points do not expose the required seam.
- **Mod ID:** Lowercase namespaced identity used by metadata, identifiers, resources, logging, and compatibility surfaces.
- **Physical client:** Minecraft client process. In single-player it contains both a logical client and an integrated logical server.
- **Physical server:** Dedicated-server process containing only the logical server.
- **Registry:** Namespaced mapping through which Minecraft/Fabric discover content and other extensible types.
- **Resource reload:** Rebuild of selected asset/data resources; it does not reload Java classes, registry bootstrap, or ordinary Mixins.
- **Saved data (`SavedData`):** Vanilla persistent state scoped through a data storage owner; mutations must be marked dirty.
- **Split environment source sets:** Loom configuration separating common and client compilation to catch client-only references while still producing one mod JAR.
- **Yarn:** Fabric community mappings used in the obfuscated era through Minecraft 1.21.11; exact build numbers are part of the source contract.

## Official Sources

- [Fabric development documentation](https://docs.fabricmc.net/develop/)
- [Fabric Loader documentation](https://docs.fabricmc.net/develop/loader/)
- [Fabric Loom documentation](https://docs.fabricmc.net/develop/loom/)
- [Fabric class tweakers](https://docs.fabricmc.net/develop/class-tweakers/)
- [Fabric mapping migration](https://docs.fabricmc.net/develop/porting/mappings)

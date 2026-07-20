# Extension Points and API Stability

Use this reference when choosing between vanilla behavior, Fabric API, another dependency, an event, a Mixin, or a class tweaker/access widener.

## Decision Ladder

1. **Reuse the repository.** Search for a local facade, registry holder, callback, helper, or Mixin targeting the same behavior.
2. **Use vanilla extension and data mechanisms.** Registries, tags, resources, codecs, data components, `SavedData`, and object overrides usually survive ecosystem composition better.
3. **Use a stable Fabric API hook.** Prefer events and callbacks designed to compose listeners.
4. **Use an existing third-party abstraction.** Verify its exact resolved version and side rules.
5. **Contain experimental API use.** Put it behind a project-owned boundary, document the version risk, and test upgrade-sensitive behavior.
6. **Transform only the missing seam.** Use a narrow Mixin or class tweaker/access widener after documenting why supported hooks are insufficient.

Prefer an event over a Mixin when both expose the required behavior. Events reduce target-method coupling and allow other mods to participate. Do not replace a global object or resource when a modify callback exists; replacement discards other contributors.

## Registries and Initialization

Registry entries normally use static holders plus an explicit `initialize`/`register` call from an entrypoint. The call makes the loading path visible even when registration occurs in static initializers.

Check companion obligations:

- a block often needs a `BlockItem`;
- an entity needs attributes and a client renderer;
- content needs models, translations, loot, recipes, tags, or data components;
- creative inventory integration should use the relevant callback/event;
- synced registries and data-driven registries may have reload or network implications.

## Stability Classification

Do not infer stability from a module suffix (`v0`, `v1`, `v2`) or package age. Verify all of:

- package boundary: public API normally lives under `net.fabricmc.fabric.api`, not implementation packages;
- `@Deprecated` and Javadoc replacement guidance;
- `@ApiStatus.Experimental` or related annotations;
- the Fabric API module's `fabric.mod.json` `custom.fabric-api:module-lifecycle` value;
- target-version migration notes and changelog.

Fabric API aims for compatibility, but Minecraft changes, experimental modules, and documented deprecations can require ports. A deprecated module may remain present solely to ease migration; do not start new work on it when a supported replacement exists.

## Mixins

Before adding one:

- verify no official event, object override, resource mechanism, or existing Mixin solves the need;
- inspect the exact target-version bytecode/source and mapping namespace;
- choose the least invasive injection point and narrowest local capture;
- keep client Mixins in a client-only configuration;
- use unique, namespaced method names where collisions are possible;
- avoid copied vanilla methods and broad `@Overwrite` unless unavoidable;
- add a failure strategy appropriate to the importance of the hook;
- run the affected client and/or dedicated server, because compilation does not prove injection success.

## Class Tweakers and Access Wideners

Class tweakers generalize access wideners in Loader 0.18+ with Loom 1.12+. Older target stacks may support only access wideners. Both should expose only the minimum vanilla member needed by maintained code.

The manifest and Gradle property may retain `accessWidener`/`accessWidenerPath` names even when the file uses class-tweaker capabilities. The file header's mapping namespace is version-sensitive: older remapped projects commonly use `named`, while 26.1+ official-mapped projects use `official`. Use Loom's validation task when configured.

Injected interfaces are public compatibility commitments. Namespace injected method names with the mod ID and provide default methods so other implementations remain valid.

## Official Sources

- [Fabric events](https://docs.fabricmc.net/develop/events)
- [Fabric class tweakers](https://docs.fabricmc.net/develop/class-tweakers/)
- [Class-tweaker interface injection](https://docs.fabricmc.net/develop/class-tweakers/interface-injection)
- [Fabric API contributor stability guidelines](https://github.com/FabricMC/fabric/blob/1.21.11/CONTRIBUTING.md)
- [Registering an item](https://docs.fabricmc.net/develop/items/first-item)
- [Registering a block](https://docs.fabricmc.net/develop/blocks/first-block)
- [Creating an entity](https://docs.fabricmc.net/develop/entities/first-entity)

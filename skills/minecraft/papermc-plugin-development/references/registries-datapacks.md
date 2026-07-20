# Registries and Datapacks

## Load this reference when

Use this file for keyed game data, registry lookups, custom registry entries, or datapack discovery. Registry mutation and bootstrap datapacks are experimental, early-lifecycle features.

## Registry reads

- Resolve registries through `RegistryAccess` and `RegistryKey` on targets that support them.
- Use `TypedKey` when both registry identity and entry identity matter.
- Handle absence for operator/user-provided keys; reserve `getOrThrow` for repository-controlled invariants.
- Store keys, tags, or `RegistryKeySet` rather than long-lived snapshots of registry values that can change across reloadable data.
- Parse a namespaced key and resolve server-side when a client does not know that registry well enough for a native command argument.

Avoid deprecated `Server#getRegistry(Class)` and `UnsafeValues` when the target supplies the supported registry API.

## Mutation and bootstrap

- Mutate only officially supported registries during the registry lifecycle from a Paper-plugin bootstrapper.
- Namespace custom entries under the plugin; never register into `minecraft` or `papermc`.
- Validate all source data before registration. A registration exception can intentionally stop startup to prevent corrupt or incomplete registry state.
- Do not introduce experimental `paper-plugin.yml` solely for an ordinary lookup.
- Determine whether a registry is synchronized to clients; a server entry is not automatically meaningful in every client UI or protocol.

## Datapack discovery

Use the lifecycle discovery API only when the target supports it and the feature requires data before normal enable. Package an embedded datapack in the form required by the current docs (a source directory rather than assuming a distributable zip), register from bootstrap, and keep identifiers stable. Bootstrap failure can halt the server.

## Traps

- Mutating registries in `onEnable`.
- Caching mutable registry objects across reloadable data changes.
- Assuming client awareness because server registration succeeded.
- Swallowing bootstrap errors and continuing with partial content.
- Shipping an embedded datapack without verifying that the server enabled it.

## Required evidence

Test a clean boot, duplicate/invalid data failure, lookup and serialization by key, client interaction where relevant, `/datapack list enabled` for discovered packs, full restart, and the exact target version.

## Official sources

- [Registry API](https://docs.papermc.io/paper/dev/registries/)
- [Registry lifecycle](https://docs.papermc.io/paper/dev/lifecycle/)
- [Datapack discovery](https://docs.papermc.io/paper/dev/lifecycle/datapacks/)
- [Paper plugins and bootstrap](https://docs.papermc.io/paper/dev/getting-started/paper-plugins/)
- [Registry command arguments](https://docs.papermc.io/paper/dev/command-api/arguments/registry/)


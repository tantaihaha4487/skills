# Persistent Data Container

## Load this reference when

Use this file for plugin-owned metadata on supported holders such as items, entities, chunks, worlds, or tile states. Use configuration for operator settings, a database for large/queryable records, Data Components for vanilla item behavior, and PDC for namespaced plugin data.

## Decide the persisted schema first

- Define stable, reusable `NamespacedKey` constants under the plugin namespace.
- Treat the key, primitive type, encoding, and semantic version as a durable schema.
- Read nullable values deliberately or use `getOrDefault` when a default is valid.
- Validate content and length inside a custom `PersistentDataType`; a matching primitive type does not prove custom bytes are semantically valid.
- Add explicit, idempotent migration when a key, type, holder, or meaning changes.

Prefer PDC over lore, display names, scoreboards, NBT reflection, or NMS tags for identity and plugin metadata. Do not use PDC to change vanilla item mechanics.

## Holder and lifetime rules

- Re-check exact-target Javadocs because holder support and ItemStack convenience methods have changed across releases.
- Use read-only views when only reading. Keep edit-callback containers inside the callback; they are invalid afterward.
- On older targets, edit an ItemStack through `ItemMeta`; on supported newer targets, prefer direct ItemStack PDC access to avoid unnecessary full metadata snapshots.
- Call `TileState#update` after mutating a placed tile state's PDC.
- Copy or translate PDC manually when data moves between holders. Item data does not automatically become placed-block data.
- Treat `OfflinePlayer` PDC as read-only where documented; synchronous offline persistence would otherwise require disk access.
- Do not retain live holders across asynchronous boundaries. Capture detached data, then re-resolve and mutate on the owning context.

## Traps

- Recreating keys dynamically in hot paths.
- Treating `has(key, customType)` as payload validation.
- Changing a primitive type without migrating existing data.
- Storing large documents or relational state in PDC.
- Assuming clone, place, break, transform, or version upgrade semantics without a test.

## Required evidence

Test absent, valid, malformed, legacy, and migrated values; item/block/entity round trips; save plus full restart; holder-copy behavior; and every supported target whose holder API differs.

## Official sources

- [Persistent Data Container guide](https://docs.papermc.io/paper/dev/pdc/)
- [PersistentDataContainer Javadocs](https://jd.papermc.io/paper/org/bukkit/persistence/PersistentDataContainer.html)
- [PersistentDataContainerView Javadocs](https://jd.papermc.io/paper/io/papermc/paper/persistence/PersistentDataContainerView.html)


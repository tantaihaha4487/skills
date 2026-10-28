# Content, Resources, Persistence, and Configuration

Use for registry-backed content, data-driven resources, durable state, item state, codecs, and project configuration.

## Content Change Checklist

Trace every new content type through:

1. namespaced identifier and registry holder;
2. explicit initializer reachability;
3. common/server behavior;
4. client representation: model, color provider, screen, or renderer;
5. assets and data: translation, model, blockstate, loot, recipe, tag, advancement, or component defaults;
6. datagen provider when generating that resource;
7. tests or focused client/server run.

Use tags and data resources, not hard-coded lists, for membership or tunable behavior when datapacks may participate.

## State Mechanism Selection

| Need | Prefer | Key rule |
| --- | --- | --- |
| Per-`ItemStack` structured data | Data component | Register a `DataComponentType`; use a `Codec` for persistence and a stream codec when network serialization is needed. |
| World/server-scoped durable state | Vanilla `SavedData` | Use a codec/factory and call `setDirty()` after every mutation. |
| Data attached to an entity, block entity, level/world, or chunk | Fabric Data Attachments when target lifecycle accepts experimental API | Use API mutation methods; immutable values make dirty tracking and synchronization reliable. |
| Native object state with an established save format | The object's existing serialization path | Preserve backward-compatible field defaults and migrations. |
| Cross-side transient state | A packet or an API-provided sync mechanism | Keep the logical server authoritative. |

Do not store per-world or per-player state in unbounded global static collections. Scope it to the owning object or lifecycle and define invalidation.

### Data Components

Modern item state belongs in components, not ad hoc raw stack NBT. Reuse vanilla components with matching semantics. Custom components should be small immutable values with explicit equality/serialization. Copy-on-write avoids invisible in-place mutation.

### Data Attachments

The Fabric Data Attachment API is experimental in relevant 1.21.x Fabric API releases. Confirm target module lifecycle before adoption. Persisted or synced attachments require codecs; in-place mutation can bypass change detection; replace values through attachment APIs.

### Saved Data

Choose the narrowest storage scope. Stable keys prevent duplicate stores. Codecs should tolerate compatible older data via optional/default fields. Forgetting `setDirty()` can make correct in-memory behavior disappear after restart.

## Codec Discipline

- Treat the codec as the schema boundary, not boilerplate.
- Return and inspect `DataResult` errors; do not silently substitute corrupt data.
- Use optional fields/defaults for additive migrations.
- Keep persisted identifiers stable and namespaced.
- Bound collections and validate untrusted network-decoded values separately.
- Test round trips and at least one older-data case when changing a schema.

## Configuration

Do not assume a universal Fabric configuration API. Inspect dependencies and local conventions, then reuse the existing config library, screen integration, path, serializer, defaults, and reload policy. If none exists, justify whether a config is needed before adding a dependency.

For a simple project-owned file, obtain the directory from `FabricLoader.getInstance().getConfigDir()`, use an established serializer/codec, write atomically, preserve unknown or older fields when appropriate, and define whether changes require restart. Never expose secrets in logs or commit machine-local config.

## Official Sources

- [Custom item data components](https://docs.fabricmc.net/develop/items/custom-data-components)
- [Fabric data attachments](https://docs.fabricmc.net/develop/data-attachments)
- [Vanilla saved data](https://docs.fabricmc.net/develop/saved-data)
- [Codecs](https://docs.fabricmc.net/develop/codecs)
- [Data generation](https://docs.fabricmc.net/develop/data-generation/)
- [`FabricLoader#getConfigDir` Javadoc](https://maven.fabricmc.net/docs/fabric-loader-0.18.4/net/fabricmc/loader/api/FabricLoader.html#getConfigDir())

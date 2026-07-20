# Data Components

## Load this reference when

Load this file only when an ItemStack requirement needs vanilla prototype or patch data beyond stable `ItemMeta`. The API is experimental and version-locked.

## Choose the right surface

| Need | Prefer |
| --- | --- |
| Common name, lore, enchantment, attribute, or other supported item metadata | `ItemMeta` for broader compatibility |
| Plugin-owned identity or payload | PDC |
| Inspect a vanilla prototype, set a complex component, or remove a prototype component | Data Components after exact-target verification |

Do not migrate ordinary ItemMeta code merely because Data Components are newer.

## Respect prototype and patch semantics

- An ItemStack resolves effective data from its prototype plus a mutable patch.
- `unsetData` removes the effective component, including a prototype-provided value.
- `resetData` removes the patch entry so prototype behavior applies again.
- `getData` can be null, including when the patch removes a component.
- Complex returned values are immutable; build a replacement and set it back.
- Use `matchesWithoutData` only when the comparison intentionally ignores the named component set.

Confirm component type, nullability, builder, validation, and client behavior in the Javadocs for the repository's exact Paper version. The API explicitly does not promise backward compatibility between Minecraft versions.

## Thread and client boundary

Treat ItemStacks and builders as owner-confined mutable state. Do not share them across async tasks. Components describe server-authoritative vanilla item data, but their presentation and accepted values can be client/version dependent.

## Traps

- Using a Data Component as a replacement for plugin PDC.
- Assuming a component exists on every material or target.
- Mutating an immutable returned component instead of replacing it.
- Copying current component constants into a multi-version module.
- Claiming backward compatibility from compilation on one target.

## Required evidence

Test prototype, set, unset, reset, copy/serialize, inventory/client display, full restart where persisted, and every claimed Paper target. Keep experimental use behind a narrow boundary.

## Official sources

- [Data Component API](https://docs.papermc.io/paper/dev/data-component-api/)
- [Paper roadmap and deprecations](https://docs.papermc.io/paper/dev/roadmap/)


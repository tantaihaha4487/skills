# Inventories and dialogs

Use this reference after identifying the existing GUI abstraction, ownership rules, and minimum server version.

## Inventories: prefer

- Identify plugin GUIs with a custom `InventoryHolder`, not title equality.
- Treat `InventoryView` as a top inventory plus the player's bottom inventory.
- Distinguish raw slots, unique across the view, from local inventory slots.
- Handle clicks and drags, including shift, number-key, offhand, and outside-click paths.
- Cancel a conflicting transaction before applying state, or schedule view changes for the next tick.
- Persist contents separately from a live player-bound view.

## Inventories: avoid and pitfalls

- Do not open, close, or replace the current view inside click/drag transaction handling; defer it.
- Do not assume `getClickedInventory()` is non-null.
- Do not directly modify slots that the active transaction will overwrite.
- Do not cache a persistent view after its player quits.
- Do not use `updateInventory()` as routine synchronization.
- Replace deprecated cursor, string-title, and generic view-property APIs using target-version Javadocs.

## Dialog API — experimental and version-sensitive

- Use dialogs for client-rendered information, confirmation, and structured input on supported clients.
- Show dynamic dialogs through `Audience#showDialog`; register reusable dialogs during bootstrap when registry identity matters.
- Give actions stable namespaced keys and bound local callbacks with explicit use count and lifetime.
- Validate returned inputs and custom click payloads before applying server state.
- Treat configuration-phase connections separately from fully joined `Player` instances.
- Do not assume escape-disabled or blocking presentation is a security boundary; enforce decisions server-side.

## Thread, client, and version boundary

- Apply the shared threading/Folia policy to inventory and player mutation.
- Inventory events occur inside an active transaction; this local boundary explains next-tick deferral.
- Menu Type and Dialog APIs are experimental. Dialog API began in Paper 1.21.7; the official guide is written for 1.21.8.
- Dialogs and menus are client UI; always retain server-side validation and authorization.

## Validation evidence

- Exercise all click/drag transfer paths and verify the client does not desynchronize.
- Prove reopen/close behavior, quit cleanup, and persistence across restart if claimed.
- Test dialog accept, decline, escape, timeout, malformed input, and unsupported-version behavior.
- Confirm experimental calls compile against the repository's exact Paper API.

## Official sources

- [Inventory API](https://docs.papermc.io/paper/dev/api/inventories/)
- [Custom inventory holders](https://docs.papermc.io/paper/dev/custom-inventory-holder/)
- [Menu Type API](https://docs.papermc.io/paper/dev/menu-type-api/)
- [`InventoryClickEvent` Javadocs (current index; select the repository target)](https://jd.papermc.io/paper/org/bukkit/event/inventory/InventoryClickEvent.html)
- [`InventoryDragEvent` Javadocs (current index; select the repository target)](https://jd.papermc.io/paper/org/bukkit/event/inventory/InventoryDragEvent.html)
- [Dialog API](https://docs.papermc.io/paper/dev/dialogs/)

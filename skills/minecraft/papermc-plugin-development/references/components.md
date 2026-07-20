# Adventure components

Use this reference when producing, parsing, storing, translating, or delivering player-visible text.

## Use when

- Send messages, titles, boss bars, sounds, or other output through an `Audience`.
- Parse administrator-authored templates or preserve signed-message semantics.

## Prefer

- Use Adventure `Component` overloads instead of legacy strings, `ChatColor`, or Bungee chat components.
- Use `Audience` to avoid duplicating sender-, player-, world-, and server-specific delivery code.
- Reuse one deliberately configured `MiniMessage` instance.
- Use MiniMessage for editable templates and Gson serialization for lossless machine persistence.
- Insert untrusted data with `Placeholder.unparsed` or `Placeholder.component`.
- Use component builders for complex trees to reduce immutable intermediate allocations.
- Preserve `SignedMessage` handling when authenticity or message deletion matters.

## Avoid and pitfalls

- Do not concatenate untrusted values into MiniMessage input; that grants markup and click-event capabilities.
- Do not use plain or legacy serializers when a lossless round trip is required.
- Do not shade or relocate Adventure types across Paper API signatures without a deliberate compatibility boundary.
- Do not claim modified content retains the original message signature.
- Do not assume `GlobalTranslator` applies to ItemStack display name and lore rendering.
- Do not treat visual `run_command` links as authorization; the command must enforce permission.

## Thread, client, and version boundary

- Components are immutable values, but delivery targets and callbacks still follow shared threading/Folia rules.
- Translatable, keybind, hover, and click behavior is rendered by the client and varies with language, resources, and version.
- Paper natively implements Adventure; normally depend on `paper-api` rather than bundling another copy.
- Align with the Adventure version bundled by the target Paper release and consult its migration guide.

## Validation evidence

- Test plain, styled, translated, hover, click, and fallback rendering on the target client/server pair.
- Test templates with literal `<`, user-supplied tags, and unexpected placeholders.
- Verify serialized data round-trips without losing events, colors, or nested structure where required.
- Confirm command permissions independently from component click presentation.

## Official sources

- [Component API introduction](https://docs.papermc.io/paper/dev/component-api/introduction/)
- [Audiences](https://docs.papermc.io/paper/dev/component-api/audiences/)
- [Internationalization](https://docs.papermc.io/paper/dev/component-api/i18n/)
- [Signed messages](https://docs.papermc.io/paper/dev/component-api/signed-messages/)
- [MiniMessage API](https://docs.papermc.io/adventure/minimessage/api/)
- [Dynamic replacements](https://docs.papermc.io/adventure/minimessage/dynamic-replacements/)
- [Adventure migration index](https://docs.papermc.io/adventure/migration/) — select the source and target major versions

# Commands

Use this reference after identifying the repository's existing command framework and exact Paper version.

## Use when

- Add or change command trees, arguments, permissions, suggestions, aliases, or registration.
- Decide between Paper Brigadier commands and the legacy Bukkit command path.

## Prefer

- Preserve the existing command architecture unless migration is an explicit requirement.
- For new Paper-only commands, register Brigadier trees through `LifecycleEvents.COMMANDS`.
- For `paper-plugin.yml` plugins, prefer bootstrap lifecycle registration; otherwise use the plugin lifecycle manager.
- Use `BasicCommand` only for genuinely simple, free-form commands.
- Put permissions and stable availability predicates in `.requires`.
- Use native argument types; wrap their parsing when a custom domain value is needed.
- Treat `CommandSourceStack#getSender()` as the invoker and permission subject. Treat nullable `getExecutor()` as an `/execute as` target.

## Avoid and pitfalls

- Do not migrate a mature Bukkit-compatible framework merely because Brigadier is newer.
- Do not perform filesystem, database, or network work synchronously in an executor.
- Do not call Paper API from an async suggestion computation; snapshot plain input first.
- Do not assume player-profile arguments are cheap: an unseen profile may require Mojang lookup.
- Do not use a registry-backed argument when the client lacks that registry; parse a key and resolve it server-side.
- Do not model dynamic state with `.requires` without planning command-tree refreshes.

## Thread, client, and version boundary

- Apply the skill's shared threading and Folia rules to command side effects.
- Brigadier supplies client parsing, suggestions, and validation; custom arguments cannot reproduce every native client error state.
- `Player#updateCommands()` is thread-safe but bandwidth-expensive; call it only after meaningful state changes.
- `plugin.yml` commands remain supported for Bukkit compatibility. `paper-plugin.yml` has no `commands` field.
- Version-gate newer helpers such as `Commands.restricted(...)` against target-version Javadocs.

## Validation evidence

- Start the target server and prove every root, alias, permission denial, console/player path, and invalid argument.
- Verify suggestion behavior without blocking and confirm the client tree updates only when intended.
- Inspect the built JAR descriptor and confirm registration occurs exactly once across lifecycle reloads.

## Official sources

- [Command API introduction](https://docs.papermc.io/paper/dev/command-api/basics/introduction/)
- [Registration](https://docs.papermc.io/paper/dev/command-api/basics/registration/)
- [Requirements](https://docs.papermc.io/paper/dev/command-api/basics/requirements/)
- [Suggestions](https://docs.papermc.io/paper/dev/command-api/basics/argument-suggestions/)
- [Bukkit and Brigadier comparison](https://docs.papermc.io/paper/dev/command-api/misc/comparison-bukkit-brigadier/)
- [`plugin.yml`](https://docs.papermc.io/paper/dev/plugin-yml/)
- [Paper plugins](https://docs.papermc.io/paper/dev/getting-started/paper-plugins/)

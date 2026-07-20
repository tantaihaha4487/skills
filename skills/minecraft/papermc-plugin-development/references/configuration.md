# Configuration and reload

## Scope

Use this reference for packaged defaults, files in the plugin data directory, validation,
persistence, custom serialization, and plugin-specific configuration reload.

## Separate three representations

1. Treat `src/main/resources/config.yml` as a packaged default, not writable runtime state.
2. Preserve the operator's existing file with `saveDefaultConfig()` or
   `saveResource(path, false)`; `true` overwrites it.
3. Parse runtime YAML into a typed, validated, preferably immutable settings object used by the
   rest of the plugin.

Follow repository conventions before introducing another configuration library or wrapper. Keep
file paths under `JavaPlugin#getDataFolder()`. Register custom `ConfigurationSerializable`
classes before loading or saving them in Paper plugins.

Calling `Configuration#set` changes only the in-memory configuration; call a save method when the
change must persist. Never perform config load or save I/O on the main/region thread: Paper
explicitly directs these operations to run asynchronously.

## Load without losing known-good state

`YamlConfiguration.loadConfiguration(file)` returns an empty configuration when the file is
missing **or when reading fails**. Distinguish first-run creation from malformed or unreadable
input before accepting the result.

Use this publication sequence:

1. Read and parse off-thread without mutating the live settings object.
2. Validate required keys, ranges, enum/key formats, cross-field rules, and schema version.
3. Log actionable paths and expected values without printing secrets.
4. Publish the complete immutable snapshot atomically only after all validation succeeds.
5. Keep the previous valid snapshot when a plugin-specific reload fails.

Make settings that require rebuilding executors, database pools, commands, listeners, or other
lifecycle resources explicitly restart-required unless the repository already owns a safe swap.
Do not design around server `/reload`; Paper deprecates it and recommends a restart for plugins.
`/paper reload` concerns Paper configuration and is unsupported, not a plugin reload mechanism.

## Hazards to reject

- Copying defaults with replacement enabled on every startup.
- Treating an empty configuration as proof that the operator supplied no values.
- Returning nullable/raw config values throughout business logic instead of validating once.
- Sharing or mutating `FileConfiguration` across async and owner contexts.
- Writing the full file on a hot event path or racing two saves to the same file.
- Silently defaulting invalid security, storage, permission, or economy settings.

## Validation evidence

- Test first run, existing file preservation, malformed YAML, missing keys, invalid ranges, and
  unwritable files.
- Prove `set` plus save survives a full stop and second startup.
- If plugin-specific reload exists, prove invalid input retains old settings and valid input swaps
  once without duplicate tasks/listeners/resources.
- Inspect startup and shutdown logs for config I/O on owner threads or leaked secrets.

## Official sources

- [Plugin configuration](https://docs.papermc.io/paper/dev/plugin-configurations/)
- [`JavaPlugin` configuration/resource Javadocs](https://jd.papermc.io/paper/org/bukkit/plugin/java/JavaPlugin.html)
- [Paper command reference and reload warnings](https://docs.papermc.io/paper/reference/commands/)

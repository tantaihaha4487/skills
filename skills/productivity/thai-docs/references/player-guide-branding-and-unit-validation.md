# Player-guide branding and unit validation

Use this reference when turning verified server/project configuration into a public player guide and publishing it as DOCX/PDF/Google Docs.

## Audience gate

Before drafting, define the reader. For a player-only guide, include connection details, required/recommended client assets, normal use paths, player commands, gameplay limits, schedules, and troubleshooting. Exclude administrator commands, internal filesystem paths, monitoring tools, implementation architecture, dependency inventories, database details, and raw configuration unless the player must act on them.

Run a forbidden-content check after export (for example: admin-only command roots, internal home paths, monitoring component names, and stale section titles). A stale manually coded table of contents can leak deleted admin sections even when the body is clean; derive the TOC from current headings.

## Normalize configuration units before writing

Do not copy a user's informal unit directly into a config value. Read the config comment/source and map:

1. Config storage unit.
2. Game/API base unit.
3. UI display unit.

Example: if a LifeSteal setting counts whole hearts, `20` whole hearts equals `40` Minecraft health points and displays as two rows. Setting the config to `40` would instead produce 40 whole hearts / 80 health points. State both units in the guide when ambiguity is likely.

After edits, parse the real config and assert the intended semantic value; then assert that the exported document contains the correct UI wording and no stale value.

## Logo and palette workflow

1. Resolve the exact requested asset when near-duplicate filenames exist (for example, prefer the unsuffixed file when the user explicitly says “without (1)”).
2. Validate format, dimensions, alpha channel, and visible content before generation.
3. Sample dominant colors from the real logo instead of inventing a palette.
4. Use a dark sampled color for headings/table headers, a pale sampled color for fills, and reserve a vivid accent for small elements. Maintain readable contrast on white.
5. Insert the logo at preserved aspect ratio on the cover; render the cover and inspect for clipping, distortion, or overflow.
6. Render a contact sheet of all pages after theme changes to catch low-contrast text and inconsistent colors.

## Updating an existing Google Doc

When a stable Google Docs URL must be preserved, upload the revised DOCX through Drive `files.update` against the existing Google Docs file ID rather than creating a duplicate. Verify through the Docs API that:

- required corrected text is present;
- stale text is absent;
- requested font families remain present;
- at least one `inlineObject` exists when a logo was required;
- styled foreground colors exist when a themed document was requested.

Also query Drive metadata to confirm the same file ID, Google Docs MIME type, modified time, edit capability, and final `webViewLink`.
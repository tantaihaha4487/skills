---
name: expressive-motion
description: Apply a measured Material 3 Expressive style (dark media-app shell, shaped artwork, spring cards, layered color roles, settings-aware motion) to any UI platform. Use when building or porting an interface in this style; its recorded values and behavior take precedence over generic design-system defaults.
---
# Expressive motion

Replicate the style across web, Qt Quick/QML, and other toolkits with its exact tokens, component grammar, motion wrappers, springs, and settings policy. Don't import design rules, motion defaults or reduced-motion policies from other skills. Explicit user changes override; otherwise keep recorded behavior.

## Start

Read host instructions, framework, tokens and components. Before changes, write a parity contract listing the target, style sections, geometry/state, wrappers/parameters, settings, platform adaptations and evidence. Preserve host framework/data/behavior; review doesn't authorize redesign or dependency migration.

Load only what the task needs:
- [tokens.md](references/tokens.md): rounding, sizes, type, fonts, color roles, palette, shapes
- [layout.md](references/layout.md): shell geometry, fit rules, component specs, thresholds
- [motion.md](references/motion.md): wrappers, springs, settings, ambient loops, reveal, hero, page navigation
- [platforms.md](references/platforms.md): web, QML and other-toolkit adapters
- [media.md](references/media.md): optional media-player components (play button, procedural covers, lyrics, spectrum, immersive view, liquid backdrop)
- [text-surfaces.md](references/text-surfaces.md): optional strict Qt-glyph text surfaces for web

[assets/tokens.json](assets/tokens.json) pins the numeric tokens and curves. The bundle needs neither network access nor other skills.

## Reproduce the style

Use named rounding/size/type tokens, semantic color roles, component hierarchy, shaped artwork/play controls and recorded hover/press/selected states. Don't replace them with a generic dashboard, utility motion, arbitrary green palette or universal mobile breakpoints. Keep content-fit equations, minimum window and crowding rules. At launch, show the side panel when it fits, setup is complete and immersive is closed; crowding clears it without reopening on widening. Re-evaluate local thresholds (spotlight, top bar, player bar, hero) whenever panel/sidebar width changes, not only on window resize. Hovered square covers scallop and round covers squiggle; the edge is part of hover. Use the content-sized snackbar; record narrow-sheet adaptations.

Choose animations by wrapper/caller, not Material token names. Keep recorded curves, durations and local Qt `SpringAnimation` values; they aren't portable. `scripts/tokens.py` converts single segments exactly; preserve multi-segment curves piecewise or label the 201-stop approximation. Live springs use the canonical [web-adapter/spring.mjs](assets/web-adapter/spring.mjs) implementation (re-exported by [card-spring.mjs](assets/card-spring.mjs)) with its presets/callback lifecycle or declare an approximation boundary.

**Settings are part of the style:** `reduceMotion = reduceMotionSetting || performanceMode` stops autonomous loops but keeps interaction growth, hover, press and reveal under reduceMotion alone. performanceMode also zeros helper timing and snaps Reveal; inspect fixed-duration callers. Immersive fades under reduceMotion and snaps in performanceMode (see `media.md`). Keep this policy; don't replace it with no-spatial-motion or claim full accessibility conformance.

Lifecycle: idle/hidden work stops; one shared ambient clock replaces per-element timers. Shelves keep geometry/scroll across delegate unloads. Follow motion.md for hero handoff, loader readiness, timeout cleanup and immersive reversal. Completion callbacks may own transient presentation cleanup; retain them when needed.

## Port and prove

Preserve semantic outcomes and appearance before platform mechanics. Use native input/focus semantics without changing visual/interaction policy. Record adaptations instead of claiming exact parity. Don't add narrow-screen overlays or keep a crowded queue open.

Run [offline checks](references/evaluation.md#offline-checks-from-the-skill-folder); use evaluation.md for tests, measured adapter accuracy and evidence rules; get motion values from `python scripts/tokens.py --platform css|qml`; never guess.

Validate endpoints/states, hover/press, rapid reversal, settings, documented widths and hidden/rest work in the actual host. Compare screenshots/trajectories to references when available. Report structural, style-parity, runtime, visual and performance evidence separately. Deterministic exports prove data conversion, not model output or pixel-identical spring physics; isolated UI fixtures don't prove account/provider/playback behavior.

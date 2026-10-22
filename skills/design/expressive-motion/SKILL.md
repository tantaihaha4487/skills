---
name: expressive-motion
description: Apply a measured Material 3 Expressive style (dark media-app shell, shaped artwork, spring cards, layered color roles, settings-aware motion) to any UI platform. Use when building or porting an interface in this style; its recorded values and behavior take precedence over generic design-system defaults.
---
# Expressive motion

A reusable visual and motion language with exact tokens, component grammar, motion wrappers, springs and settings policy, plus tools to reproduce them faithfully on web, Qt Quick/QML or another toolkit. Do not import design rules, motion defaults or reduced-motion policies from other skills. A user's explicit change overrides the baseline. Otherwise keep the recorded behavior.

## Start

Read the host project's instructions and identify its framework, existing tokens and components. Before changing an interface, write a short parity contract that lists the target view/component, the style sections it uses, the geometry/style/state to keep, the motion wrapper and its parameters, the settings policy, platform conversions and the evidence you need. Keep the host's framework, data and app behavior. Studying or reviewing a UI does not authorize a redesign or a dependency migration.

Load only what the task needs:
- [tokens.md](references/tokens.md): rounding, sizes, type, fonts, color roles, palette, shapes
- [layout.md](references/layout.md): shell geometry, fit rules, component specs, thresholds
- [motion.md](references/motion.md): wrappers, springs, settings, ambient loops, reveal, hero, page navigation
- [platforms.md](references/platforms.md): web, QML and other-toolkit adapters
- [media.md](references/media.md): optional media-player components (play button, procedural covers, lyrics, spectrum, immersive view, liquid backdrop)
- [text-surfaces.md](references/text-surfaces.md): optional strict Qt-glyph text surfaces for web
- [evaluation.md](references/evaluation.md): tests, measured adapter accuracy and evidence rules

[assets/tokens.json](assets/tokens.json) pins the numeric tokens and curves. The bundle needs no network access and no other skill.

## Reproduce the style

Use the named rounding/size/type tokens, layered semantic color roles, the real component hierarchy, shaped artwork and play controls, and the recorded hover/press/selected states. Do not swap them for a generic card dashboard, a standard-motion utility theme, an arbitrary green palette or universal mobile breakpoints. Keep the content-fit equations, the minimum window, crowded-panel closing and the start state: the side panel opens at launch whenever it fits. Component thresholds (spotlight, top bar, player bar, hero) follow the component's own width, so they must re-evaluate when the side panel opens or the sidebar moves, not only when the window resizes. Hovered covers change shape (square covers get scallops, round covers a squiggle), and that edge is part of the hover state. Errors use the content-sized snackbar, never a message squeezed into a narrow column.

Choose each animation by its wrapper and caller, not by what a similarly named Material token suggests. Keep the mixed expressive/legacy curves, the custom durations and the local springs. These springs are Qt `SpringAnimation` numbers and do not transfer to CSS or other spring engines. `scripts/tokens.py` converts single-segment curves exactly. Multi-segment emphasized curves get a labeled sampled linear approximation. Live springs need the bundled recurrence ([card-spring.mjs](assets/card-spring.mjs), with scale, tilt and side-panel presets and explicit callback-lifecycle modes) or a declared approximation boundary.

**Settings are part of the style:** reduceMotion (also implied by performanceMode) stills autonomous loops but keeps interaction growth, hover and press motion. performanceMode suppresses most interaction helpers, so inspect callers for exceptions. The immersive view uses fades under reduced motion. Do not silently substitute a generic no-spatial-motion policy, and do not claim full accessibility conformance from it.

Lifecycle: idle or hidden work stops, and shared ambient motion runs on one clock, not a timer per element. Shelves keep their geometry and scroll when delegates unload. Hero handoff, loader readiness, timeout cleanup and immersive reversal follow motion.md. Completion callbacks may own transient presentation cleanup; do not remove them just because another skill discourages animation-event logic.

## Port and prove

Preserve semantic outcomes and appearance before optimizing platform mechanics. Use the host's native input and focus semantics without changing the visual or interaction policy. Record every necessary adaptation instead of presenting it as exact parity. Do not add a narrow-screen overlay, and do not keep a crowded queue open when the style closes it.

From the skill folder, run `node scripts/test_card_spring.mjs`, `node scripts/test_card_edge.mjs`, `node scripts/test_motion_engine.mjs`, `node scripts/test_source_adapters.mjs`, `python scripts/check_bundle.py` and `python -m unittest discover -s scripts -p 'test_*.py'`. Get motion values from `python scripts/tokens.py --platform css|qml`; never guess them.

Validate endpoints and states, hover/press, rapid reversal, settings combinations, the documented widths, and hidden/rest work in the actual host. When a reference implementation exists, compare screenshots and trajectories against it. Report structural, style-parity, runtime, visual and performance evidence separately. Repeated deterministic exports prove stable data conversion, not deterministic model output or pixel-identical spring physics. An isolated UI fixture does not prove account, provider or playback behavior.

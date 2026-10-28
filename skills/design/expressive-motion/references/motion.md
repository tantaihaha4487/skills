# Motion

Read wrapper and caller. Names don't guarantee official Material tokens. `python scripts/tokens.py --platform css|qml` emits exact curves.

| Wrapper | Duration (helper) | Curve |
|---|---|---|
| ElementMove | 500 (motion) | expressiveDefaultSpatial |
| ElementMoveEnter / Exit | 400 / 200 (motion) | emphasizedDecel / emphasizedAccel |
| ElementMoveFast | 200 (motion) | expressiveEffects |
| ElementMoveFastColor | 200 (duration) | expressiveEffects |
| ElementMoveSmall | 350 (motion) | expressiveFastSpatial |
| ElementResize | 300 (motion) | emphasized, two cubic segments (12 numbers) |
| HoverFade | 350 (duration) | standard |
| ClickBounce | 400 (motion) | expressiveDefaultSpatial |
| SidebarSlideEnter / Exit | 300 / 250 (motion) | standardDecel / standardAccel |

Springs are Qt `SpringAnimation` values, not portable physics: Bounce spring 7, damping .24, epsilon .002 (card scale, cover waviness); card tilt 4 / .3 / .01; hero flight 3.4 / .27 / .002; side-panel width 4 / .32 / .5. Don't replace them with guessed M3 physics, treat `damping` as a damping ratio, or treat velocity as an initial velocity.

## Settings policy

reduceMotion = reduceMotionSetting || performanceMode. Both `duration(ms)` and `motion(ms)` return 0 only in performanceMode, so under reduceMotion alone, reveals still grow and fade and hover/press still animate. That is intentional, and it isn't an accessibility-compliance claim. performanceMode collapses helper timing and snaps Reveal. Fixed-duration callers need separate inspection. noShapes is independent (see tokens.md). Inspect the specific paths instead of asserting one global stop-all rule.

## Ambient loops

- One shared ambient clock ticks at 33 ms (30 Hz) and subscribes only while speed is nonzero. Never run one timer or RAF per element.
- Spin speed targets .9 rad/s while playing/spinning and not reduceMotion, easing over 900 ms InOutSine. It is gated on window visibility.
- Drift: rate = active && !reduceMotion && !pointerResting ? speed : 0, eased over 650 ms InOutSine. It runs while |rate| > .0001; phase += rate·frameTime modulo the period. The brief settle after a stop is part of the style.

## Cover edge

Hover springs waviness 0→3.5 on Bounce, and the spring snaps in performanceMode. While waviness > .01, a Drift turns the scallops at 2π/2.4 rad/s. Scallop count is round(perimeter/22) on the item's own edge, so it doesn't change while waviness springs. Peaks touch the edge and valleys cut in by waviness·(.5+.5cos…). A round cover of 40 px or more draws a squiggle instead: thickness max(2, size·.02), amplitude max(1.4, .7·thickness), waves max(8, round(2π·middle/(8·thickness))), with the cover cut two line widths inside the line. Spin advances frameTime·speed·waves·.075, with speed easing 0↔1 over 700 ms InOutSine and coasting to a stop on leave. reduceMotion and a resting pointer stop drift and spin, but the waviness spring still animates. performanceMode snaps waviness and stops the loops. noShapes flattens both edges. Cover scale 1.015, the badge (opacity, scale .82→1) and shadow blur 7→13 use 160 ms OutCubic.

## Reveal

The first assignment applies immediately, and performanceMode always snaps opacity, visibility and scale. Later changes set visibility first, then fade in for min(200, duration) or out for min(150, duration). Scale enters from .85 over the requested duration (default 440 ms OutBack overshoot 2.2) and exits over min(170, duration) InCubic. The item stays visible until the exit animation completes, and the completion callback hides it. Rapid changes stop and rebuild from current properties. Don't replace this with display:none or destroy-on-hide.

## Page navigation

The page host keeps one built page behind the active page. Older slots unload into cheap placeholders and rebuild when history returns. Entering stops the previous entry animation, fades 0→1 over 210 ms OutCubic and rises y 14→0 over 400 ms emphasizedDecel. This local fade/rise doesn't hold the old page or use generic fade-through. Back restores the kept page and may return a matching visible hero. On the web this needs explicit page-stack ownership; a router that rebuilds every page loses scroll and hero targets.

## Hero flight

Launch is refused in performanceMode and for zero-size covers or empty sources. Launch stores the card's window rect, size, radius, source and circular flag, and arms them for 600 ms. The destination claims the armed state. The flight maps the destination every visible frame in common scene coordinates, springs progress (3.4 / .27 / .002), and ends once the spring settles and the hero is ready, with a 2200 ms deadline. It layers a card-size cached image under the hero-size image. On return, the card is hidden until landing and its opacity is restored after the target clears. Keep the destination handoff and the original image source. A new target resets progress directly, which isn't velocity-continuous retargeting.

## Shape burst

10 pieces have a 720 ms linear lifetime with random directions, shapes and tones. Production randomness is intentional. Regression tests inject a seed or compare ranges and endpoints instead of removing it.

The immersive reveal and lyric motion are covered in [media.md](media.md).

# Platform adapters

Keep the parity contract on every platform: same tokens, geometry equations, state machines and settings policy. Change only mechanics; record each adaptation.

## Shared rules

- Curves: a six-number Qt BezierSpline segment [x1,y1,x2,y2,1,1] equals cubic-bezier(x1,y1,x2,y2) exactly. The 12-number emphasized curve is two cubic segments. Evaluate it piecewise (as `curve_y` in scripts/tokens.py does) or use the labeled 201-stop sampled approximation. Never substitute a familiar OutCubic because it looks similar.
- Springs: port the Qt recurrence in the canonical [web-adapter/spring.mjs](../assets/web-adapter/spring.mjs) (16 ms step, epsilon settle, fractional frame accumulation, retained velocity); [card-spring.mjs](../assets/card-spring.mjs) re-exports it for compatibility. Or compare against a sampled Qt trajectory with the same start, target and elapsed times. A native spring API (CSS, Compose `spring()`, SwiftUI `.spring`, Flutter `SpringSimulation`) is an approximation until measured. Record the maximum position and settle error and test reversals separately.
- Thresholds: observe the component's own size (web ResizeObserver, Compose `onSizeChanged`/`BoxWithConstraints`, Flutter `LayoutBuilder`, SwiftUI `GeometryReader`, QML width bindings), never only window resize.
- Settings: expose reduceMotion and performanceMode separately with the policy in motion.md. Mapping an OS reduced-motion preference into the reduceMotion flag is a platform adaptation; don't upgrade it to a stronger policy without a product decision.
- Scheduling: one ambient clock owner per window. Stop it when hidden. Keep near-screen loading, offscreen placeholders and scroll restoration.
- Units: map logical px 1:1 to CSS px/dp/pt at 1×, then check actual font/DPI metrics. Don't multiply values by devicePixelRatio.
- Fonts and shapes: ship the real font files and the shape catalogue. Exported tokens alone don't supply fonts, shapes, the theme engine or the app.

## Web

Use the existing framework. Grid/Flexbox may own outer geometry while an inner wrapper owns card transforms. Pointer hover maps card states, and buttons and links keep native keyboard semantics. Get values with `python scripts/tokens.py --platform css`.

Copy `assets/web-adapter/` as a directory, keeping `assets/source-shaders/` paths; this full-directory copy contract includes the canonical `spring.mjs` implementation. Import only what you need:
- `spring.mjs`: the scale, tilt and side-panel springs.
- `source-layout.mjs`: `sourceLayout(physicalW,physicalH,{zoom,sidebarWidth})` returns logical geometry, the clamped sidebar, panel fit and physical minimums. `sourceZoomCommand` and `sourceZoomForKey(event,zoom)` handle the Control zoom shortcuts (dispatch the value and prevent the browser default), and `applySourceZoom` applies one top-left scale to content and overlay. `new SourcePanels(fits)` handles the start-shown, exclusive and clear-when-crowded panel state: call `setFits()` from the same width source as the layout, and use `shown({immersiveOpen,needsSetup})` for the inspector. A page that loads already narrow starts cleared; record that as standing in for the 1280 start shrinking.
- `card-edge.mjs`: hovered cover scallops and squiggle (see below).
- `hero-flight.mjs`: the hero flight. Use one viewport coordinate system and don't apply scroll twice. Hero overlays use physical DOM rects outside the zoom layers. On a zoom change mid-flight, call `HeroFlight.rescale(new/old)` and keep progress and velocity. Keep readiness, the 2200 ms cleanup and teardown cancellation.
- `dialog-focus.mjs`: a modal traps Tab, makes the background inert and restores focus to the connected opener.
- `renderer-closure.mjs`, `artwork.mjs`, `immersive-controller.mjs`, `liquid-backdrop.mjs`, `spectrum.mjs` and the lyrics modules are covered in [media.md](media.md).

Card edges: spring waviness 0→`CARD_EDGE.hoverWaviness` with `CARD_SPRING`. Advance the scallop phase from the shared clock at `driftSpeed` (rate eased over 650 ms; zero under reduce, performance or a resting pointer), then apply `scallopClipPath(w,h,{radius,waviness,phase})` and clip the shadow and border with the same path. For round covers, use `squiggleGeometry`, `squiggleCoverClipPath` and `squiggleOutline` (primary color, stroke width `thickness`) and advance the spin with `advanceSquiggle`. Remove the clip at waviness 0 and under noShapes. The tests prove the contour, not antialiased pixels; use `SourceRenderer` for exact edge pixels.

Host fonts can override bundled ones. Record the resolved face, axes, Thai fallback and baselines. A family-name match plus `document.fonts.ready` proves neither metrics nor rasterization. Keep semantic DOM text. For strict Qt glyph parity, see [text-surfaces.md](text-surfaces.md). Read rendered width after a spring starts; a same-task read can precede its first frame.

## Qt Quick / QML

Build the style as a singleton (tokens, curves, `duration()`/`motion()` helpers), a shared UI-state singleton (ambient clock, hero arming), motion wrapper components named as in motion.md, and a shape item backed by the catalogue. Use `pragma ComponentBehavior: Bound`, typed properties and the project's Qt 6 version. Check the executable path, because `/usr/bin/qml` may be Qt 5. Get values with `python scripts/tokens.py --platform qml`, which keeps every curve segment. Use `SpringAnimation` with the recorded numbers.

Read how each existing item is positioned before changing it. Don't refactor anchors, Columns or ListViews into Layouts for style reasons. A new Layout must be the sole owner of its direct children's geometry, and motion should stay inside a wrapper or overlay. Honor noShapes, pointerResting, onScreen and nearScreen where the style uses them. Run the matching qmllint/qmltestrunner. An isolated shim test proves only the included wrappers and equations, and offscreen software rendering proves neither GPU performance nor desktop accessibility.

## Other toolkits (Compose, Flutter, SwiftUI, native)

No measured evidence exists for these, so state that boundary. Map tokens to the theme object (`MaterialTheme`/`ThemeData`/environment values) under their style names, not standard M3 roles. Implement the two-segment emphasized curve as a custom easing (Compose `Easing { }`, Flutter `Curve.transformInternal`, SwiftUI `UnitCurve`/custom `Animation`). Drive springs with the ported recurrence on a frame clock (Compose `withFrameNanos`, Flutter `Ticker`, SwiftUI `TimelineView`/`CADisplayLink`). Render shapes from the polar params, and clip covers with a path from card-edge.mjs's equations. Keep the Reveal state machine (visible until exit completes) and the hero arming/claim protocol. Validate with trajectory samples against card-spring.mjs and screenshots against a web or QML reference build.

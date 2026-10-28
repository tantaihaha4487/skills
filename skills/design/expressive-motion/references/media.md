# Optional media components

Load only for music/media UIs. Web modules live in `assets/web-adapter/`. Each module needs host elements, real data, one scheduling owner, and disposal on teardown. No account data or reference screenshots are included.

## Play button

Shape goes softCookie→cookie9 while playing, with spin rate 25. Icon size is round(width·.52). The glyph pops .55→1 over 480 ms OutBack overshoot 2.6, and a shape burst fires on start.

## Procedural covers (`artwork.mjs`)

Missing artwork becomes a deterministic sleeve, not a gradient or a random placeholder. Hash the identity's UTF-8 bytes with unsigned 32-bit FNV-1a (offset 2166136261, multiplier 16777619, uint32 overflow), pick one of six palettes and six compositions, and paint a 256-unit scene at the requested size in dark or light mode. Clip it with the same layer, radius and border as real art. Real loaded art wins. Cards and heroes default the identity to the title, navigation items to their text, and playlists use their stable id. Share one identity across card, hero and navigation. JS code points or a runtime-seeded hash produce different pictures (Thai included). Never use a screenshot of a reference component as the candidate in a pixel comparison.

## Player scheme

The player has its own scheme owner. Its palette comes from the current artwork and cross-fades over 600 ms InOutQuad. It follows the app's light/dark mode, and an always-dark scheme serves the immersive player. With no cover it falls back to the theme; in light mode the dark roles are re-seeded from the theme primary. Don't recolor player surfaces with the app scheme. Per-surface visualizer switches (player bar, song row, immersive) apply in addition to the master flag.

## Immersive reveal (`immersive-controller.mjs`, `renderer-closure.mjs`)

Opening picks a shape from a 12-shape list (circle under noShapes; `DEFAULT_REVEAL_SEED` is the default seed, and a string key is FNV-hashed). Spin turns 1.6π over 600 ms. Reach goes .01→.2 in 260 ms OutBack 2.4, holds 60 ms, then goes to 1 in 280 ms InBack 1.2. Normal close takes 520 ms OutCubic with spin +1.4. Reduced motion uses fades instead (240 ms open, after loader readiness; 200 ms close). Performance snaps. The shader clamps to at most five lobes, and reach is computed from the window diagonal. The loader is asynchronous and keeps a layer only while reveal is between 0 and 1. The CSS clip polygon samples the analytic mask with 1024 vertices. CSS antialiasing is an adaptation; use the shader renderer for exact edge pixels.

`SourceRenderer`: `new SourceRenderer(canvas,{alpha:true,premultipliedAlpha:true})` when the host needs transparency (the default is opaque), then `render(programKey, shaderText, uniforms, {textureSource})`. Set backing dimensions explicitly, and use `{capture:true}` only for offline PNG readback, not every live frame. Await `image.decode()`. For ImageBitmap, use `{premultiplyAlpha:'premultiply',colorSpaceConversion:'none',imageOrientation:'none'}`. Rows start at the top-left, and alpha is premultiplied. `textureSmooth:true` (LINEAR) is the default; use false only where a caller disables smooth. Same-size in-place pixel changes need `textureVersion++` or `forceTextureUpload`. `sourceRevealUniforms(shape,reach,spin,w,h)` covers the 12 reveal shapes with the five-lobe clamp. `RendererClosureSession` wraps shown/settings. Always `dispose()`.

## Liquid backdrop (`liquid-backdrop.mjs`)

`await LiquidBackdrop.create(canvas)`, then `resize(w,h)` and `setState({shown,playing,reduced,living,blur,palette,energy,lead})`. Supply real normalized RGBA palette and real audio energies; never invent analyzer data. `reduced` includes performanceMode. While paused, elapsed time holds. Reduced or non-living fields render the still time 37. `LiquidBackdrop` is a shared-clock exception: each instance owns one 33 ms timer only while shown, playing, non-reduced and living; hiding or disposal cancels it. Hidden fields release framebuffer storage. Call `resetClock()` after a loader-style teardown so the next instance starts at zero. Pixel evidence is DPR 1 only.

## Spectrum (`spectrum.mjs`)

`SpectrumRenderer.create(canvas)` loads the bar and halo shaders. Supply real `levels`, `palette`, `kind`, `wave`, `width` and `height`. `spectrumStyle`/`spectrumTargets` implement the band mapping, and `advanceSpectrum` returns smoothed levels and velocities for the caller's step. The host owns the scheduling and analyzer connection. Synthetic bands are test inputs, never evidence of live audio.

## Lyrics (`lyrics-panel.mjs`, `lyrics-closure.css`)

`createLyricsView` takes lines, sync, the active index and `onSeek`. The host calls `advance(ms)` from its scheduler, sets `suspended` while the immersive view covers the panel, and resumes with `setState({suspended:false})`. Scale keeps separate `springing` and `eased` channels: switching the reduce/performance flags selects a channel while an already-running hidden spring continues. Don't cancel opacity or lag on suspension or performance toggles. Logical scroll = scrollTop − topMargin. Count the footer in content height, excluding list margins, instead of using viewport-clamped scrollHeight.

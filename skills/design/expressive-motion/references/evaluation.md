# Evaluation and evidence

The oracle is this style's recorded values plus an in-style reference implementation when available. It isn't another skill or generic design score. Freeze every fixture input: view, data, font, theme, window, settings, runtime version and random seed. Never refresh goldens to make failures pass.

## Offline checks (from the skill folder)

```sh
python scripts/check_bundle.py
node scripts/test_card_spring.mjs
node scripts/test_card_edge.mjs
node scripts/test_motion_engine.mjs
node scripts/test_source_adapters.mjs
python -m unittest discover -s scripts -p 'test_*.py' -v
python scripts/tokens.py --platform css
python scripts/tokens.py --platform qml
```

`test_source_adapters.mjs` checks 336 numeric values across ten zoom/fit cases, six spectrum band mappings and panel-state semantics. Stable bytes across repeated exports prove deterministic conversion only.

## Measured adapter accuracy (against Qt 6.12 reference builds)

- Springs: `card-spring.mjs` reproduces Qt's 16 ms recurrence. Card press/release matches 81 samples with max error 0 and settles in 592 ms. `test_motion_engine.mjs` adds 210 SpringAnimation comparisons across 16 ms, split 8 ms and uneven callbacks (max 5.69e-14). Its Qt-driver mode keeps the first-callback registration delay. The browser's fixed-step immediate mode is a host adaptation. None of this proves compositor onset or pacing, or other Qt versions.
- Immersive controller: 740 property comparisons over interrupted and reversed segments (max 4.44e-16). Hero DOM geometry: 282 comparisons, max .0156 CSS px (gate .02).
- Procedural covers: SSIM ≥ .98 and mean ΔE2000 ≤ 2 across all 144 palette × composition × mode × size cases.
- Rounded-image and reveal shaders: 85/85 at SSIM ≥ .98 and max ΔE2000 ≤ 2 on matched Qt XCB vs Chromium ANGLE GL. SwiftShader passes 73/85. Smooth (LINEAR) is the default; nearest differs in 18,280 pixels.
- Liquid backdrop (320×180, t=37): SSIM .992, mean ΔE2000 .37. Spectrum: 6/6 on the same GPU (min SSIM .9999987). SwiftShader fails the strict color gate, so pin the backend.
- Text: pure HTML card typography failed (.965). Font-derived Qt text surfaces pass full-card SSIM .983 at the .98 gate. A whole-view shell fixture passes .981 (526×410), .988 (988×410) and .995 (1280×780), byte-identical across three fresh Chromium processes.
- Native raster repeatability needs QT_HASH_SEED=0, 64 warm-up frames, an injected drift phase and every nonempty image Ready before capture. A QAnimationDriver doesn't freeze FrameAnimation time.

These results bound shipped adapters; they don't prove every GPU, viewport, provider route or browser version.

## Image comparison

`python scripts/compare_images.py ref.png candidate.png --output result.json --preview cmp.png` (Pillow and NumPy; sizes must match). SSIM uses an 11 px Gaussian window with sigma 1.5. The script also reports the CIEDE2000 distribution, RMSE and differing pixels. `--color-roi x,y,w,h` adds named regions without masking the full SSIM. The CIEDE2000 implementation passes all 34 Sharma reference pairs (https://hajim.rochester.edu/ece/sites/gsharma/ciede2000/). These thresholds are research gates, not universal quality standards.

For batch runs whose downstream step reads the saved JSON, add `--quiet` to print only its JSON-quoted result path.

## Behavioral trials

Give fresh, bounded evaluators the skill and a raw request without the intended answer. Run at least three independent runs, plus equivalent English and Thai prompts. Example task: build the media card hover/press plus the shell's sidebar and side-panel fit and the motion flags on the host platform, with no new dependencies. Score the decisions: scales 1/1.03/.95, pressed opacity .86, sidebar clamp 132/28%, panel 320, reserve 404+32, reduceMotion keeps interaction, performance collapses helpers, crowded panels close.

Fail critical parity if an evaluator:
- imports standard utility motion
- removes all interaction motion under reduceMotion
- keeps queue state through crowding
- starts with the panel closed when it fits
- drops the scallop/squiggle hover edge
- leaves a component on the wrong side of its threshold after the panel opens
- squeezes the snackbar into a column
- treats springs as portable physics
- calls a sampled approximation exact

Fix the smallest ambiguous instruction and rerun the affected cases.

## Runtime and visual evidence

Test normal, reversed and rapid input, the settings combinations, the 526×410 minimum, the fit boundary ±1 at several sidebar widths, hidden/rest scheduling and disposal. For curves, compare normalized trajectories. For springs, compare position, settle and reversal against the recurrence or Qt. Wait for every image (including fallbacks) to be ready before a fixed warm-up. Sample reversal before and after the toggle in one browser task. Compare angles modulo 2π. Report structural checks, deterministic data tests, independent trials, real runtime behavior, screenshots and measured performance separately. Never average away a critical mismatch.

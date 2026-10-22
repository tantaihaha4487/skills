# Qt font surfaces for strict web text parity

Use ordinary semantic DOM text when the contract permits host font rasterization. When matching Qt Quick glyph pixels is part of the contract, `scripts/export_qt_text.cjs` and its adjacent `font-raster-adapter.qml` can generate a text-only surface from a caller-supplied string. This is a build-time Qt dependency, not an image of an existing interface. It is optional for ports that do not require that pixel contract.

The helper needs Node, a matching Qt Quick `qmlscene`, `xvfb-run` on Linux and the actual reference fonts. `fc-scan` supplies file family metadata when the Qt release build suppresses QML console logs. Override `QT_QMLSCENE` for another Qt installation. Supply `--font-file` (or `EXPRESSIVE_FONT_FILE`) to load the intended primary file through FontLoader. With no file, `--family` uses the host's Qt font database; a nominal family name is weaker provenance. Fonts are not included in this skill. Record the resolved reference files/hashes, variable axes, fallback availability and Qt/GPU version. The manifest tags whether family/status came from QML logs, the successful FontLoader.Ready export gate or fc-scan metadata. Keep those inferred fields distinct from observed glyph-run provenance. Loading a primary file does not establish which fallback face supplies every Thai glyph.

```sh
node scripts/export_qt_text.cjs \
  --text 'ข้อความใหม่ / New title' \
  --font-file /absolute/path/reference-font.ttf \
  --width 176 --height 42 --pixel-size 15 --weight Font.Medium \
  --wrap Text.Wrap --maximum-line-count 2 --background '#121212' \
  --output /tmp/title-surface.png
```

The generated PNG has an adjacent JSON manifest containing the input text/hash, font file/hash and layout contract. Preserve both. Publication uses a fresh staged image; failure returns nonzero and retains the previous successful caller output. Do not consume an old output after a failed invocation. Choose the caller's weight/axes/wrapping/elision/alignment rather than copying this example universally. An opaque flat background must be part of the grabbed Item. Export a transparent surface when required by the host, and measure that separate blend/raster path; a Window color alone does not make an Item capture opaque. Phase offsets belong to a recorded subpixel placement contract, not arbitrary per-string tuning.

Import `applyFontRasterAdapter` from `assets/web-adapter/fullpage-font-raster-adapter.mjs`. Supply `{text,surface:{src}}` and retain its default semantic DOM text. The image is decorative with `aria-hidden`; the host CSS should position it at the measured text baseline and hide the duplicate visual DOM glyphs while preserving the text for accessibility. Keep text selection, focus and accessible names appropriate to the host. This module supplies text/image association, not a whole layout or theme.

Never substitute a captured reference UI, crop away failing text from a whole-view comparison, or label a two-string raster cache as arbitrary-text proof. Test new Thai/Latin strings chosen after the exporter is frozen, regenerate them from font inputs, compare decoded dimensions/alpha and repeat independent processes. A passing representative full-page fixture is bounded to its components, inputs and backend; it does not establish every provider route or a universally identical browser font engine. See [evaluation.md](evaluation.md) for measured acceptance and renderer limits.

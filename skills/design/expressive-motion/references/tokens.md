# Tokens, type, color and shapes

Values are logical px (dp/pt at 1:1), chosen by this style rather than generic Material. Use named values; don't round to multiples of 4.

## Numeric tokens (assets/tokens.json)

| Family | Values |
|---|---|
| Rounding | unsharpen 2, unsharpenMore 6, verySmall 8, small 12, normal 17, large 23, veryLarge 30, full 9999, window 18 |
| Font sizes | smallest 10, smaller 12, smallie 13, small 15, normal 16, large 17, larger 19, huge 22, hugeAss 23, title 22, headline 30, display 36 |
| Sizes | elevationMargin 10, pageMargin 32, sectionGap 32, shelfGap 16, cardSize 176, headerArtwork 232, artworkRadius 12, smallArtworkRadius 7, sideSheetWidth 320, topBarHeight 64, playerBarClearance 120 |

Keep role names; don't rename them to standard Material typography roles and assume parity.

## Type and icons

Body text defaults to the interface family, 15 px, onSurface, with optional tabular numbers. Titles use Google Sans Flex Bold with variable axes ROND 100 / wdth 110 / wght 720: display 36, headline 30, otherwise title 22, and display tracking −0.4. Interface fallback order: Google Sans Flex, Google Sans, Rubik, Inter, Noto Sans, then the platform font. Load bundled fonts only when the family is absent. Icons are Material Symbols Rounded glyphs from a pinned font with variable axes. SVG sets or Unicode fallbacks change ink and measured layout. Substitute fonts change metrics (Thai included), so inspect the actually loaded faces before comparing screenshots.

## Color roles

Colors come from a role scheme, not literals. A palette variant (lowest, window, page, raised, raisedMore, line, text, subtext, muted, primary, secondary, tertiary, error) maps to roles:

- background=window, onBackground=text, surface=page, surfaceContainerLowest=lowest, surfaceContainerLow=page, surfaceContainer=mix(page,raised,.5), surfaceContainerHigh=raised, surfaceContainerHighest=raisedMore.
- onSurface=text, onSurfaceVariant=subtext, outline=muted, outlineVariant=line, shadow/scrim=black, surfaceTint=primary.
- Each accent gets its tone, an `on` color picked for WCAG contrast, and a container wash mix(tone,page, .3 dark / .22 light). On-container ink mixes toward text until contrast ≥ 4.5.
- Fixed roles mix the tone toward white (.3/.6) and black (.2/.5).

Layers: layer0=background, layer1=surfaceContainerLow, layer2=surfaceContainer, layer3=surfaceContainerHigh, layer4=surfaceContainerHighest, each with a paired onLayer role. Examples of derived states: layer1Hover=mix(layer1,onLayer1,.92), layer1Active=mix(layer1,onLayer1,.85), layer2Disabled=mix(layer2,background,.8), tooltip=inverseSurface, scrimOverlay=black@.5, shadowColor=black@.3. `mix(a,b,t)` weights a by t. Keep the derivation; don't flatten primaryContainer, secondaryContainer or the hover layers into one accent or one grey.

Default palette (the theme source can replace it; don't hardcode one theme as every theme):

- Dark: #000000, #000000, #121212, #1f1f1f, #2a2a2a, #3e3e3e, #ffffff, #b3b3b3, #7c7c7c, #1ed760, #b3b3b3, #1db954, #f3727f
- Light: #ffffff, #f0f0f0, #ffffff, #f6f6f6, #ededed, #dedede, #121212, #6a6a6a, #8f8f8f, #1aa34a, #6a6a6a, #169c46, #e91429

Theme mode defaults to system. Seeded/system schemes use a fidelity content scheme for a builtin seed and a tonal-spot scheme otherwise. Player surfaces have their own scheme owner, described in [media.md](media.md).

## Shapes

Shapes are distance-field shapes from a versioned catalogue, not CSS border-radius. The catalogue order is a compatibility boundary (37 names): circle, square, slanted, arch, fan, arrow, semiCircle, oval, pill, triangle, diamond, clamShell, pentagon, gem, sunny, verySunny, cookie4, cookie6, cookie7, cookie9, cookie12, ghostish, clover4, clover8, burst, softBurst, boom, softBoom, flower, puffy, puffyDiamond, pixelCircle, pixelTriangle, bun, heart, softCookie, squircle. Unknown names resolve to circle.

Polar/superellipse params include cookie4=(4,.12,1,0), softCookie=(5,.06,1.15,0), clover4=(4,.42,.55,0), sunny=(8,.14,2.2,0), burst=(12,.24,2.8,0) and squircle=(0,0,4,1); unlisted names default to (0,0,1,0). Keep named geometry through the atlas or an authorized derived export. Turning every shape into a circle loses parity.

The `noShapes` setting is independent of the motion settings. It turns every shape into a circle except items marked `keepsShape` (shape icons, heart), and it flattens wavy pills/clips, squiggle rings and cover edges. Fonts and artwork carry their own licences; this skill doesn't grant redistribution rights.

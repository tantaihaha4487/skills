# Layout and component grammar

All values are logical px. Keep them as constants in a portability layer. Replacing them with rem values, a standard sidebar breakpoint or a generic container query changes the behavior.

## Shell

- Window opens at 1280×780. Minimum is ceil(526·zoom)×ceil(410·zoom). Work in logical layoutWidth=width/zoom and layoutHeight=height/zoom. UI zoom is 0.5..2 with keyboard steps of 0.1, rounded to tenths. Content and the popup overlay are sized to logical dimensions and scaled once from the top-left. Apply zoom once to menus and hero coordinates too.
- Sidebar starts at 232, and the user can drag it within 132..270. Effective width is max(132, min(sidebarWidth, layoutWidth·0.28)). Left margin is 8, the drag gutter is 8, and the top gutter is 8 + titleBarInset (macOS max(28, safe-area top); in-app window controls 36; otherwise 0). Hosts with window controls on the right reserve their own chrome insets.
- Sheet: 8 gutters on all sides, radius large 23, layer1, and page content clipped inside.
- Side panel (lyrics/queue inspector): 320 wide, inset 8. It fits only when layoutWidth − effectiveSidebar − 320 − 32 ≥ 404. With the default sidebar the boundary is 988 logical. Lyrics start shown and the queue hidden; the two are mutually exclusive. When the panel stops fitting, both clear. The crowded-panel check runs on every fit change and every panel toggle, so a toggle pressed while it does not fit opens nothing, and widening the window again does not reopen it. Do not start with the panel closed, and do not add a modal queue or state retention unless asked. The width opens with spring 4 / damping .32 / epsilon .5, which is disabled in performanceMode. The panel shows only when setup is complete and the immersive view is closed.
- Floating player: 12 above the sheet bottom, width max(0, min(720, sheet.width − 36)).
- Top bar: 64 high with no background; content scrolls underneath. Pages start at top margin 64, use page margin 32 and reserve 120 bottom player clearance.
- The shell draws only while the window is on screen and the immersive reveal is below 1. Hidden windows stop drawing and animating.

## Navigation and controls

- Navigation item: 40 high. Content starts at 16+indent with a 12 gap and an 8 right margin. Selected state is a secondary-container wavy pill that grows from 35% to full width. Hover/press use layer1Hover/layer1Active. Icon box 24, glyph 22; the selected shape icon is 30/17.
- Section label: 36 high, label at x 16 in 12 px text, with a wavy divider filling the rest. Sidebar list spacing is 2, top padding 8, and the bottom settings item is anchored with 8 margins.
- Icon button: 40 by default, 24 icon, full radius, with filled, tonal, standard and outlined role pairs. Text button: 40 high (compact when icon-only), full pill, gap 8, icon 18, label 15 DemiBold, padding 16/24 with a leading icon and 24/24 without.
- Search field: 260×40 full pill. On focus the fill becomes surfaceContainerHighest@.5 with a 2 px primary border. Magnifier 20 at left 12, input 10 after it, clear button 32 with a 4 right margin.
- Segmented control: 36 segments, 14 horizontal padding, 20 icons, 4 outer inset, 6 icon/text gap, and a sliding secondary-container indicator. Cache the selected segment and keep its placement when items are added or removed.
- Menu: enters with opacity 150 ms OutCubic and exits with opacity 100 ms (no scale). Pressing the opener of an open menu closes it. Snapshot the anchor's logical position into a stationary anchor; do not track a moving toolbar button. Close on Escape or an outside press. Size overflow from window height and zoom.

## Cards, shelves, rows, grids

- Media card: 176 wide with a square cover and an 8 column gap. Title is up to 2 lines at 15 DemiBold with wrap/elide; subtitle is 12 px onSurfaceVariant, right-elided. Circular cards center the text and square cards left-align it. Scale is 1 idle, 1.03 on hover and .95 on press with opacity .86. Pointer tilt spans 12° across and 10° down.
- Cover hover: square covers get scallops (waviness 3.5, wavelength 22) and round covers a turning squiggle line. The cover scales to 1.015, the shadow goes blur 7→13, y 3→6 and alpha .11→.22, and a 34 px badge (black .58, inset 10) fades in. Artwork radius is 12. The edge is part of the hover state; see motion.md.
- Shelf: 13 heading/row gap, row height cardSize+64=240, 16 list gap, 32 page margins. Delegates load asynchronously near the screen and draw only on screen, with reused items and no cache buffer. The holder keeps its geometry while delegates unload. Save horizontal scroll (contentX+leftMargin) before delegates disappear and restore it afterwards.
- Song row: 58 high, padding 14, number slot 22, art 44×44 at radius 6 with a 12 gap. The text column starts 12 after the art with a 3 gap; title 15 and subtitle 12. Duration sits in a right-aligned 42 slot. Actions are 28 icon buttons, right to left, with a 2 gap. The current row is primary@.07 with a primary DemiBold title; hover is onSurface@.05.
- Playlist grid: available=width−2·32+20, columns=max(1, floor(available/200)), tile=available/columns−20, side margins 22, top 88, cell height tile+86, tile x 10.

## Hero, spotlight, snackbar

- Collection hero: artwork at (32,40). sideArtworkSpace = width − 64 − 24 − 220. It stacks when that is below 160 (about 468 wide), with artwork min(176, .5·(width−64)); otherwise artwork is min(232, sideArtworkSpace). Details sit 24 after side artwork or 20 below stacked artwork, with 9 spacing. Kind chip: 26 high, 15 icon, 10 bold label, tracking .8. Fact chips are 24 high with a 6 flow gap. Actions have 6 top padding and a 10 gap, actionSize=max(28, min(48, (width−30)/4)), and switch to icon-only only below an action width of 130. A 480 hero is side-by-side and 430 is stacked; Play/Shuffle stay pills.
- Home: top 64, content y 24. The spotlight width is pageWidth − 2·32. It stacks below 460 (inset 20, artwork min(144, width·.4), details below); otherwise it is side-by-side (inset 26, artwork 176, details 24 to the right). With the default sidebar and the panel open at 988, the spotlight is about 338 wide and stacks. The title is one line, headline 30 Bold, tracking −.5, eliding right across whatever width the layout gives it. Home has a loading state (spinner plus a loading line) and hidden empty shelves, but no empty or error placeholder. Label any extra empty/error view as host content.
- Snackbar (the only error banner): centered, top at topBar.bottom+4, content-sized: width min(560, row+32), height row+24. The row holds a softBoom shape icon (32, warning glyph 18), the message, and a 32 close button, with spacing 12 and x 16. The message is selectable text of width min(implicit, 440), wrapping only past 440, in small 15 on errorContainer at radius 17. It is not clamped to the sheet. It fades in 200 / out 150, scales .94→1 with ElementMoveSmall, and dismisses after 8000 ms. If the host must fit it inside a narrow sheet, record that as an adaptation.

## Component thresholds

Top bar cuts over at 600 and 420, the player bar at 560 and 400, the collection hero at sideArtworkSpace < 160, the spotlight at 460, and the playlist grid uses 200 columns. These are component-local, not a global mobile scheme. Read the caller to see what each cutover changes. Each one binds to the component's own width, so it re-evaluates on every frame of the side-panel spring and on sidebar drags, not only on window resize. Keep the truncation policy unless the user asks to change it.

Probe widths 526, 780, 988 and 1280, the fit boundary ±1 at several sidebar widths, a resized sidebar, minimum height 410, theme variants, and long and Thai labels. These are style probes, not proof of a 320-wide mobile design.

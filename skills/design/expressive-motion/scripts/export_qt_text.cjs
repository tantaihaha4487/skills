#!/usr/bin/env node
/*
 * Generic Qt font-surface exporter for the bounded full-page proof.
 *
 * The caller supplies the string and its layout contract.  The helper asks
 * the same QtQuick Text.QtRendering path used by the source build to export a
 * glyph surface (transparent by default, with an optional flat background);
 * it never reads or embeds a UI screenshot.  It
 * intentionally keeps the Qt build-time dependency explicit so a browser
 * run cannot silently claim universal raster parity.
 *
 * Example:
 *   node regenerate-font-surface.cjs \
 *     --text 'ประเทศไทย · unseen' --width 144 --height 19 \
 *     --pixel-size 15 --weight Font.Medium --output /tmp/unseen.png
 *
 * Variable font axes are optional, for example
 * `--axes FILL=0,GRAD=0,opsz=24,wght=400` for a Material Symbols glyph.
 */
const crypto = require('node:crypto');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { spawnSync } = require('node:child_process');

const sourceDir = __dirname;
const defaults = {
  width: 176,
  height: 42,
  pixelSize: 15,
  weight: 'Font.Medium',
  color: '#ffffff',
  family: 'Google Sans Flex',
  output: path.resolve(process.cwd(), 'font-surface.png'),
  elide: 'Text.ElideNone',
  wrap: 'Text.NoWrap',
  renderType: 'Text.QtRendering',
  background: 'transparent',
  maximumLineCount: 1,
  phaseX: 0,
  phaseY: 0,
  // A caller may pin a build font, but the reusable helper has no machine-
  // specific path baked into its defaults.  An empty path means resolve the
  // requested family through Qt's normal font database.
  fontFile: process.env.EXPRESSIVE_FONT_FILE || '',
  axes: '',
  horizontalAlignment: 'Text.AlignLeft',
  verticalAlignment: 'Text.AlignTop',
};

function usage(message) {
  if (message) console.error(`error: ${message}`);
  console.error('usage: regenerate-font-surface.cjs --text STRING --output PNG [--width N --height N --pixel-size N --weight Font.Medium --color #fff --family "Google Sans Flex" --elide Text.ElideRight]');
  process.exit(2);
}

function parseArgs(argv) {
  const options = { ...defaults };
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith('--')) usage(`unknown argument ${token}`);
    const key = token.slice(2).replaceAll('-', '_');
    if (key === 'help') {
      usage();
    }
    if (index + 1 >= argv.length) usage(`missing value for ${token}`);
    const value = argv[++index];
    const target = {
      text: 'text', output: 'output', width: 'width', height: 'height',
      pixel_size: 'pixelSize', weight: 'weight', color: 'color', family: 'family',
      elide: 'elide', wrap: 'wrap', render_type: 'renderType', font_file: 'fontFile', axes: 'axes',
      background: 'background', maximum_line_count: 'maximumLineCount', max_lines: 'maximumLineCount',
      phase_x: 'phaseX', phase_y: 'phaseY',
      horizontal_alignment: 'horizontalAlignment', vertical_alignment: 'verticalAlignment',
    }[key];
    if (!target) usage(`unknown argument ${token}`);
    options[target] = value;
  }
  if (typeof options.text !== 'string') usage('--text is required');
  for (const key of ['width', 'height', 'pixelSize']) {
    options[key] = Number(options[key]);
    if (!Number.isFinite(options[key]) || options[key] <= 0 || !Number.isInteger(options[key])) usage(`--${key} must be a positive integer`);
  }
  options.maximumLineCount = Number(options.maximumLineCount);
  if (!Number.isInteger(options.maximumLineCount) || options.maximumLineCount < 1) usage('--maximum-line-count must be a positive integer');
  for (const key of ['phaseX', 'phaseY']) {
    options[key] = Number(options[key]);
    if (!Number.isFinite(options[key]) || options[key] < 0 || options[key] >= 1) usage(`--${key === 'phaseX' ? 'phase-x' : 'phase-y'} must be in [0,1)`);
  }
  return options;
}

function qmlString(value) {
  return JSON.stringify(value);
}

function qmlWeight(value) {
  const weights = {
    'Font.Normal': 400, 'Font.Medium': 500, 'Font.DemiBold': 600,
    'Font.Bold': 700, 'Font.Black': 900,
  };
  if (weights[value] !== undefined) return weights[value];
  const numeric = Number(value);
  if (Number.isInteger(numeric) && numeric >= 1 && numeric <= 1000) return numeric;
  usage(`unsupported --weight ${value}`);
}

function qmlAxes(value) {
  if (!value) return '({})';
  const axes = {};
  for (const part of String(value).split(',')) {
    const [tag, raw] = part.split('=');
    const number = Number(raw);
    if (!tag || !Number.isFinite(number)) usage(`invalid --axes entry ${part}`);
    axes[tag.trim()] = number;
  }
  return `(${JSON.stringify(axes)})`;
}

function sha256(file) {
  if (!file || !fs.existsSync(file)) return null;
  return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
}

function resolvedFontFile(value) {
  if (!value) return null;
  const file = path.resolve(value);
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) usage(`--font-file does not exist: ${file}`);
  return file;
}

function parseFontMetadata(run) {
  const output = `${run?.stdout || ''}\n${run?.stderr || ''}`;
  const matches = [...output.matchAll(/FONT_EXPORT_METADATA\s+(\{[^\r\n]*\})/g)];
  if (!matches.length) return null;
  try {
    return JSON.parse(matches[matches.length - 1][1]);
  } catch {
    return null;
  }
}

function fontFamilyFromFile(file) {
  if (!file) return null;
  const scan = spawnSync('fc-scan', ['--format=%{family}\n', file], {
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'ignore'],
    timeout: 5_000,
    killSignal: 'SIGTERM',
  });
  if (scan.error || scan.status !== 0) return null;
  return (scan.stdout || '').split('\n').map((line) => line.trim()).find(Boolean) || null;
}

function main() {
  const options = parseArgs(process.argv.slice(2));
  options.fontFile = resolvedFontFile(options.fontFile);
  const output = path.resolve(options.output);
  fs.mkdirSync(path.dirname(output), { recursive: true });
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'expressive-font-surface-'));
  // Accept only a fresh image from this invocation, never an older caller output.
  const renderedOutput = path.join(tempDir, 'rendered.png');
  const adapter = fs.readFileSync(path.join(sourceDir, 'font-raster-adapter.qml'), 'utf8');
  fs.writeFileSync(path.join(tempDir, 'FontRasterAdapter.qml'), adapter);
  const qmlFile = path.join(tempDir, 'Export.qml');
  const useSuppliedFont = Boolean(options.fontFile);
  const suppliedFontSource = useSuppliedFont ? pathToFileURL(options.fontFile).href : '';
  const qml = `import QtQuick 2.15
import QtQuick.Window 2.15

Window {
    id: exportWindow
    visible: true
    width: ${options.width}
    height: ${options.height}
    color: ${qmlString(options.background)}
    flags: Qt.FramelessWindowHint | Qt.Tool

    property bool useSuppliedFont: ${useSuppliedFont ? 'true' : 'false'}
    property bool exportStarted: false

    FontLoader {
        id: suppliedFont
        // The caller's fontFile is loaded before the export frame is accepted.
        source: /* fontFile supplied by caller */ ${qmlString(suppliedFontSource)}
    }

    function fontReady(): bool {
        return !exportWindow.useSuppliedFont || suppliedFont.status === FontLoader.Ready
    }

    function fontStatusName(value): string {
        if (value === FontLoader.Null) return "Null"
        if (value === FontLoader.Loading) return "Loading"
        if (value === FontLoader.Ready) return "Ready"
        if (value === FontLoader.Error) return "Error"
        return "Unknown"
    }

    function logFontMetadata(): void {
        console.log("FONT_EXPORT_METADATA " + JSON.stringify({
            status: suppliedFont.status,
            statusName: exportWindow.fontStatusName(suppliedFont.status),
            name: suppliedFont.name || "",
            actualFamily: raster.font.family || "",
            actualRenderType: raster.renderType
        }))
    }

    function exportWhenRendered(): void {
        // Local file failures can happen before Connections is constructed.
        // Check the current status as well as observing later changes.
        if (exportWindow.useSuppliedFont && suppliedFont.status === FontLoader.Error) {
            Qt.callLater(function() { Qt.exit(4) })
            return
        }
        if (exportWindow.exportStarted || !exportWindow.fontReady()) return
        exportWindow.exportStarted = true
        exportWindow.logFontMetadata()
        Qt.callLater(function() {
            raster.exportImage(function(result) {
                if (!result || !result.saveToFile(${qmlString(renderedOutput)})) Qt.exit(3)
                else Qt.exit(0)
            })
        })
    }

    onAfterRendering: exportWhenRendered()

    Connections {
        target: suppliedFont
        function onStatusChanged() {
            if (suppliedFont.status === FontLoader.Error) Qt.exit(4)
            else if (suppliedFont.status === FontLoader.Ready) Qt.callLater(exportWindow.exportWhenRendered)
        }
    }

    FontRasterAdapter {
        id: raster
        anchors.fill: parent
        text: ${qmlString(options.text)}
        color: ${qmlString(options.color)}
        wrapMode: ${options.wrap}
        elide: ${options.elide}
        renderType: ${options.renderType}
        backgroundColor: ${qmlString(options.background)}
        horizontalAlignment: ${options.horizontalAlignment}
        verticalAlignment: ${options.verticalAlignment}
        maximumLineCount: ${options.maximumLineCount}
        textOffsetX: ${options.phaseX}
        textOffsetY: ${options.phaseY}
        font.family: exportWindow.useSuppliedFont && suppliedFont.status === FontLoader.Ready ? suppliedFont.name : ${qmlString(options.family)}
        font.pixelSize: ${options.pixelSize}
        font.weight: ${qmlWeight(options.weight)}
        font.variableAxes: ${qmlAxes(options.axes)}
    }

    Component.onCompleted: Qt.callLater(exportWindow.exportWhenRendered)
}
`;
  fs.writeFileSync(qmlFile, qml);
  const environment = {
    ...process.env,
    QT_QPA_PLATFORM: 'xcb',
    QSG_RHI_BACKEND: 'opengl',
    // Keep Qt hash iteration deterministic for atlas/font lookup and record
    // the effective seed below. A caller may override it explicitly.
    QT_HASH_SEED: process.env.EXPRESSIVE_QT_HASH_SEED || '0',
  };
  const command = process.env.QT_QMLSCENE || '/usr/lib/qt6/bin/qmlscene';
  try {
    const run = spawnSync('xvfb-run', ['-a', command, qmlFile], {
      env: environment,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
      timeout: 30_000,
      killSignal: 'SIGTERM',
    });
    if (run.error || run.status !== 0 || !fs.existsSync(renderedOutput)) {
      process.stderr.write(run.stdout || '');
      process.stderr.write(run.stderr || '');
      if (run.error) process.stderr.write(`${run.error.message}\n`);
      if (run.error?.code === 'ETIMEDOUT') process.stderr.write('font export timed out after 30000 ms\n');
      process.exitCode = run.error ? 1 : (run.status || 1);
      return;
    }
    const fontLoader = parseFontMetadata(run);
    // qmlscene does not forward QML console output on all Qt release builds.
    // Successful export itself proves the FontLoader.Ready gate was crossed;
    // use fontconfig metadata for the loaded family when that log is absent.
    const scannedFontFamily = fontFamilyFromFile(options.fontFile);
    const fontLoaderStatus = fontLoader?.statusName || (useSuppliedFont ? 'Ready' : 'NotRequested');
    const fontLoaderName = fontLoader?.name || scannedFontFamily || null;
    const actualFontFamily = fontLoader?.actualFamily || scannedFontFamily || null;
    const imageHash = sha256(renderedOutput);
    const manifest = {
      text: options.text,
      text_sha256: crypto.createHash('sha256').update(options.text, 'utf8').digest('hex'),
      output: path.basename(output),
      image_sha256: imageHash,
      width: options.width,
      height: options.height,
      pixel_size: options.pixelSize,
      weight: options.weight,
      color: options.color,
      background: options.background,
      background_in_surface: options.background !== 'transparent',
      maximum_line_count: options.maximumLineCount,
      phase_x: options.phaseX,
      phase_y: options.phaseY,
      opaque_background: options.background !== 'transparent',
      font_family: options.family,
      font_resolution: options.fontFile
        ? 'FontLoader source pinned to font_file; Text.font.family uses suppliedFont.name after FontLoader.Ready'
        : 'Qt font database lookup for requested family; no external font file pinned',
      font_loader_status: fontLoaderStatus,
      font_loader_status_code: fontLoader?.status ?? null,
      font_loader_status_source: fontLoader ? 'QML FontLoader.status' : (useSuppliedFont ? 'FontLoader.Ready export gate' : 'not requested'),
      font_loader_name: fontLoaderName,
      font_loader_name_source: fontLoader?.name ? 'QML FontLoader.name' : (scannedFontFamily ? 'fc-scan font file metadata' : 'unavailable'),
      actual_font_family: actualFontFamily,
      actual_render_type: fontLoader?.actualRenderType ?? options.renderType,
      variable_axes: options.axes || null,
      font_file: options.fontFile,
      font_sha256: sha256(options.fontFile),
      font_loader_used: Boolean(options.fontFile),
      fallback_family: options.family,
      layout_contract: {
        wrap: options.wrap,
        elide: options.elide,
        render_type: options.renderType,
        horizontal_alignment: options.horizontalAlignment,
        vertical_alignment: options.verticalAlignment,
      },
      renderer: 'QtQuick Text.QtRendering',
      backend: `QSG_RHI_BACKEND=opengl; QT_QPA_PLATFORM=xcb; QT_HASH_SEED=${environment.QT_HASH_SEED}; xvfb-run`,
      qt_hash_seed: environment.QT_HASH_SEED,
      publication: 'Fresh staged render; previous caller output retained on failure; manifest published last',
      source_screenshot_used: false,
    };
    const pendingImage = `${output}.${process.pid}.pending`;
    const pendingManifest = `${output}.json.${process.pid}.pending`;
    try {
      fs.copyFileSync(renderedOutput, pendingImage);
      fs.writeFileSync(pendingManifest, `${JSON.stringify(manifest, null, 2)}\n`);
      fs.renameSync(pendingImage, output);
      fs.renameSync(pendingManifest, `${output}.json`);
    } finally {
      fs.rmSync(pendingImage, {force:true});
      fs.rmSync(pendingManifest, {force:true});
    }
    process.stdout.write(`${JSON.stringify(manifest)}\n`);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
}

main();

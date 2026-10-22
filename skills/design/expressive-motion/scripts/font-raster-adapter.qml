import QtQuick 2.15

// Reusable source-font exporter. Any caller may supply arbitrary Thai/Latin
// text, dimensions, weight and color; this component never embeds a known
// string or samples a UI screenshot. The calling Qt build provides the same
// font files/renderer as the source capture, which is an intentional
// build-time dependency for glyph metrics and raster parity.
Item {
    id: root

    property alias text: label.text
    property alias font: label.font
    property alias color: label.color
    property alias wrapMode: label.wrapMode
    property alias maximumLineCount: label.maximumLineCount
    property alias elide: label.elide
    property alias horizontalAlignment: label.horizontalAlignment
    property alias verticalAlignment: label.verticalAlignment
    property alias renderType: label.renderType
    property alias textOffsetX: label.x
    property alias textOffsetY: label.y
    // Keep the surface contract self-contained.  An opaque export must carry
    // its flat source background inside the grabbed Item; grabbing only this
    // transparent Item would otherwise omit the Window's color.
    property color backgroundColor: "transparent"

    implicitWidth: label.implicitWidth
    implicitHeight: label.implicitHeight

    Rectangle {
        anchors.fill: parent
        color: root.backgroundColor
        z: -1
    }

    Text {
        id: label
        width: root.width
        height: root.height
        textFormat: Text.PlainText
        renderType: Text.QtRendering
    }

    function exportImage(callback) {
        return root.grabToImage(callback)
    }
}

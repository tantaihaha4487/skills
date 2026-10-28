# Compatibility and tooling

## Authority

Use current Iris documentation first:

- https://shaders.properties/current/reference/overview/
- https://irisshaders.dev/
- https://github.com/IrisShaders/ShaderDoc

Use shaderLABS for learning and templates:

- https://shaderlabs.org/wiki/Getting_Started
- https://shaderlabs.org/wiki/Rendering_Pipeline_(OptiFine,_ShadersMod)
- https://github.com/shaderLABS/Base-330

Use Iris examples for structure and idioms:

- https://github.com/IrisShaders/Iris-Example-Shaderpack
- https://github.com/IrisShaders/Aperture-Example-Pack

## Version discipline

Record Minecraft, loader, Iris, Sodium, GPU/OpenGL, and rendering-mod versions before implementation. Iris documents Fabric 1.16.5+ and NeoForge 1.21.1+, with Forge unsupported; recheck the current site before publishing compatibility claims.

Iris integrates with Sodium. Test target matrix: Nvidium disables with shaders; Distant Horizons/Voxy need explicit pack support; Canvas/Vulkan/OptiFine are incompatible; Indium depends on Minecraft/Sodium version.

## Development setup

A plain editor works; VS Code may add GLSL highlighting and Minecraft lint/includes via the `vscode-mcshader` language server (availability and platform vary). Prefer a known-good Base-330 pack to an empty one.

## Distribution

Keep template/example licenses intact; do not copy OptiFine docs verbatim. State Iris-only versus OptiFine targeting, list tested Minecraft/Iris/Sodium versions, and package a ZIP with `shaders/` at its root.

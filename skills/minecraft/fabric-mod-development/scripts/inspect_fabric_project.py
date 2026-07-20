#!/usr/bin/env python3
"""Read-only inventory of a Fabric project's version and architecture contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


IGNORED_PARTS = {
    ".git",
    ".gradle",
    ".idea",
    ".settings",
    "bin",
    "build",
    "out",
    "run",
}


def source_files(root: Path, name: str) -> list[Path]:
    return sorted(
        path
        for path in root.rglob(name)
        if not any(part in IGNORED_PARTS for part in path.relative_to(root).parts)
    )


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def parse_properties(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not path.is_file():
        return result
    for raw_line in read_text(path).splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", "!")):
            continue
        match = re.match(r"([^:=\s]+)\s*[:=]\s*(.*)$", line)
        if match:
            result[match.group(1)] = match.group(2).strip()
    return result


def first_property(properties: dict[str, str], names: Iterable[str]) -> str | None:
    for name in names:
        value = properties.get(name)
        if value:
            return value
    return None


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def parse_manifest(root: Path, path: Path) -> dict[str, Any]:
    entry: dict[str, Any] = {"path": rel(root, path)}
    try:
        payload = json.loads(read_text(path))
    except (OSError, json.JSONDecodeError) as exc:
        entry["error"] = str(exc)
        return entry

    entry.update(
        {
            "id": payload.get("id"),
            "version": payload.get("version"),
            "environment": payload.get("environment", "*"),
            "entrypoints": payload.get("entrypoints", {}),
            "mixins": payload.get("mixins", []),
            "access_widener_or_class_tweaker": payload.get("accessWidener"),
            "depends": payload.get("depends", {}),
        }
    )
    custom = payload.get("custom")
    if isinstance(custom, dict):
        fabric_api = custom.get("fabric-api")
        if isinstance(fabric_api, dict) and fabric_api.get("module-lifecycle"):
            entry["fabric_api_module_lifecycle"] = fabric_api["module-lifecycle"]
    return entry


def detect_plugins(build_text: str) -> list[dict[str, str | None]]:
    with_versions = re.findall(
        r"\bid\s*(?:\(\s*)?['\"]([^'\"]+)['\"]\s*\)?\s+"
        r"version\s*(?:\(\s*)?['\"]([^'\"]+)['\"]",
        build_text,
    )
    ids = re.findall(
        r"\bid\s*(?:\(\s*)?['\"]([^'\"]+)['\"]",
        build_text,
    )
    versions_by_id = {plugin_id: version for plugin_id, version in with_versions}
    return [
        {"id": plugin_id, "version": versions_by_id.get(plugin_id)}
        for plugin_id in dict.fromkeys(ids)
        if "loom" in plugin_id or "fabric" in plugin_id
    ]


def detect_java(build_text: str, properties: dict[str, str]) -> str | None:
    for pattern in (
        r"JavaLanguageVersion\.of\((\d+)\)",
        r"JavaVersion\.VERSION_(\d+)",
        r"sourceCompatibility\s*=\s*['\"]?(\d+)",
        r"jvmToolchain\((\d+)\)",
        r"\b(?:target)?[Jj]avaVersion\s*=\s*(\d+)",
    ):
        match = re.search(pattern, build_text)
        if match:
            return match.group(1)
    return first_property(properties, ("java_version", "javaVersion"))


def detect_mappings(build_text: str, properties: dict[str, str]) -> dict[str, Any]:
    lines = [
        line.strip()
        for line in build_text.splitlines()
        if re.search(r"\bmappings\b", line) and not line.lstrip().startswith("//")
    ]
    yarn = bool(
        first_property(properties, ("yarn_mappings", "yarnMappings"))
        or any("yarn" in line.lower() for line in lines)
    )
    return {
        "style": "yarn" if yarn else ("declared-other" if lines else "not-declared"),
        "declarations": lines,
        "property": first_property(properties, ("yarn_mappings", "yarnMappings", "mappings_version")),
    }


def count_files(path: Path, suffix: str | None = None) -> int:
    if not path.is_dir():
        return 0
    return sum(
        1
        for candidate in path.rglob("*")
        if candidate.is_file() and (suffix is None or candidate.suffix == suffix)
    )


def inspect(root: Path) -> dict[str, Any]:
    gradle_files = [
        path
        for name in ("settings.gradle", "settings.gradle.kts", "build.gradle", "build.gradle.kts")
        if (path := root / name).is_file()
    ]
    build_files = [path for path in gradle_files if path.name.startswith("build.gradle")]
    build_text = "\n".join(read_text(path) for path in build_files)
    properties = parse_properties(root / "gradle.properties")
    manifests = [parse_manifest(root, path) for path in source_files(root, "fabric.mod.json")]

    source_roots: list[dict[str, Any]] = []
    for path in sorted((root / "src").glob("*/*")) if (root / "src").is_dir() else []:
        if path.is_dir() and path.name in {"java", "kotlin", "resources"}:
            source_roots.append(
                {
                    "path": rel(root, path),
                    "kind": path.name,
                    "files": count_files(path, ".java" if path.name == "java" else None),
                }
            )

    java_paths = sorted(
        path
        for path in root.rglob("*.java")
        if not any(part in IGNORED_PARTS for part in path.relative_to(root).parts)
    )
    test_files = [path for path in java_paths if "test" in path.relative_to(root).parts]
    mixin_configs = source_files(root, "*.mixins.json")
    widener_files = sorted(
        path
        for pattern in ("*.accesswidener", "*.classtweaker")
        for path in root.rglob(pattern)
        if not any(part in IGNORED_PARTS for part in path.relative_to(root).parts)
    )

    minecraft = first_property(properties, ("minecraft_version", "minecraftVersion"))
    loader = first_property(properties, ("loader_version", "loaderVersion"))
    fabric_api = first_property(
        properties,
        ("fabric_version", "fabric_api_version", "fabricApiVersion"),
    )
    versions = {
        "minecraft": minecraft,
        "java": detect_java(build_text, properties),
        "loader": loader,
        "fabric_api": fabric_api,
        "loom_plugins": detect_plugins(build_text),
        "mappings": detect_mappings(build_text, properties),
    }

    features = {
        "split_environment_source_sets": "splitEnvironmentSourceSets" in build_text,
        "data_generation_configured": bool(
            re.search(r"dataGeneration|runDatagen|fabric-datagen", build_text)
            or any("fabric-datagen" in item.get("entrypoints", {}) for item in manifests)
        ),
        "publishing_configured": bool(re.search(r"\bpublishing\s*\{", build_text)),
        "mixin_configs": [rel(root, path) for path in mixin_configs],
        "access_wideners_or_class_tweakers": [rel(root, path) for path in widener_files],
        "test_source_files": len(test_files),
        "generated_roots": [
            rel(root, path)
            for path in source_files(root, "generated")
            if path.is_dir()
        ],
    }

    advisories: list[str] = []
    if not manifests:
        advisories.append("No source fabric.mod.json was found; confirm this is the mod project root.")
    if minecraft == "1.21.11":
        advisories.append(
            "Minecraft 1.21.11 is the last obfuscated-era release; use exact 1.21.11 docs and mapping-aware APIs."
        )
    if minecraft and re.match(r"^(26|2[7-9]|[3-9]\d)\.", minecraft):
        advisories.append(
            "This appears to be an unobfuscated-era target; verify official mappings, Java, and non-remapping Loom configuration."
        )
    if not features["split_environment_source_sets"] and any(
        rel(root, path).startswith("src/main/")
        and ("/client/" in f"/{path.as_posix()}/" or path.name.endswith("Client.java"))
        for path in java_paths
    ):
        advisories.append(
            "Client-looking classes exist in main sources without split environment source sets; inspect dedicated-server class-loading boundaries."
        )
    if not test_files:
        advisories.append("No Java test sources were detected; rely on explicit runtime checks or add tests when justified.")
    if any("fabric-loom" == plugin.get("id") for plugin in versions["loom_plugins"]):
        advisories.append(
            "The legacy fabric-loom plugin ID is present; preserve it for unrelated work, but consult target migration guidance before upgrading."
        )

    return {
        "root": str(root),
        "gradle_files": [rel(root, path) for path in gradle_files],
        "gradle_properties": properties,
        "versions": versions,
        "manifests": manifests,
        "source_roots": source_roots,
        "features": features,
        "advisories": advisories,
        "note": "This inventory is repository evidence, not proof of an API signature; verify resolved Javadocs/source before editing.",
    }


def scalar(value: Any) -> str:
    if value is None or value == "":
        return "not detected"
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return str(value)


def render_text(report: dict[str, Any]) -> str:
    versions = report["versions"]
    lines = [
        f"Fabric project inventory: {report['root']}",
        "",
        "Version contract",
        f"  Minecraft: {scalar(versions['minecraft'])}",
        f"  Java: {scalar(versions['java'])}",
        f"  Loader: {scalar(versions['loader'])}",
        f"  Fabric API: {scalar(versions['fabric_api'])}",
        f"  Loom plugins: {scalar(versions['loom_plugins'])}",
        f"  Mappings: {scalar(versions['mappings'])}",
        "",
        "Manifests",
    ]
    if report["manifests"]:
        for manifest in report["manifests"]:
            lines.append(
                f"  {manifest['path']}: id={scalar(manifest.get('id'))}, "
                f"environment={scalar(manifest.get('environment'))}, "
                f"entrypoints={scalar(sorted(manifest.get('entrypoints', {}).keys()))}"
            )
    else:
        lines.append("  none detected")

    lines.extend(["", "Source roots"])
    if report["source_roots"]:
        lines.extend(
            f"  {item['path']}: {item['files']} files" for item in report["source_roots"]
        )
    else:
        lines.append("  none detected")

    lines.extend(["", "Features", f"  {scalar(report['features'])}", "", "Advisories"])
    if report["advisories"]:
        lines.extend(f"  - {item}" for item in report["advisories"])
    else:
        lines.append("  none")
    lines.extend(["", report["note"]])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect a Fabric project without modifying it."
    )
    parser.add_argument("root", nargs="?", default=".", help="Fabric project root")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")

    report = inspect(root)
    if args.json:
        json.dump(report, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        print(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

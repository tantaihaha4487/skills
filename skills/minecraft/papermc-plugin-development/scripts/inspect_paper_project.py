#!/usr/bin/env python3
"""Produce a read-only inventory of a Paper plugin repository.

The report surfaces evidence and unknowns for an agent's mandatory architecture
summary. It deliberately does not infer runtime correctness from text matches.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


IGNORED_DIRS = {
    ".git",
    ".gradle",
    ".idea",
    ".settings",
    "build",
    "target",
    "out",
    "node_modules",
}
SOURCE_SUFFIXES = {".java", ".kt", ".kts"}
DESCRIPTORS = {"plugin.yml", "paper-plugin.yml"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect a Paper plugin repository without changing it."
    )
    parser.add_argument("root", nargs="?", default=".", help="repository root")
    parser.add_argument(
        "--json", action="store_true", dest="as_json", help="emit JSON"
    )
    return parser.parse_args()


def is_ignored(path: Path, root: Path) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return True
    return any(part in IGNORED_DIRS for part in parts)


def files_named(root: Path, names: set[str]) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.name in names and not is_ignored(path, root)
    )


def source_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix in SOURCE_SUFFIXES
        and not is_ignored(path, root)
        and "src" in path.parts
    )


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def matching_files(
    files: list[Path], pattern: str, root: Path, flags: int = 0
) -> list[str]:
    regex = re.compile(pattern, flags)
    return [rel(path, root) for path in files if regex.search(read_text(path))]


def parse_maven_paper_coordinates(pom: Path) -> list[str]:
    try:
        document = ET.parse(pom).getroot()
    except (ET.ParseError, OSError):
        return []

    def local_name(tag: str) -> str:
        return tag.rsplit("}", 1)[-1]

    properties: dict[str, str] = {}
    for element in document.iter():
        if local_name(element.tag) == "properties":
            for child in element:
                properties[local_name(child.tag)] = (child.text or "").strip()

    coordinates: set[str] = set()
    for dependency in document.iter():
        if local_name(dependency.tag) != "dependency":
            continue
        values = {
            local_name(child.tag): (child.text or "").strip()
            for child in dependency
        }
        if values.get("groupId") != "io.papermc.paper" or values.get("artifactId") != "paper-api":
            continue
        version = values.get("version", "unknown")
        property_match = re.fullmatch(r"\$\{([^}]+)}", version)
        if property_match:
            version = properties.get(property_match.group(1), version)
        scope = values.get("scope", "compile")
        coordinates.add(f"io.papermc.paper:paper-api:{version} [{scope}]")
    return sorted(coordinates)


def parse_maven_dependencies(pom: Path, root: Path) -> list[str]:
    try:
        document = ET.parse(pom).getroot()
    except (ET.ParseError, OSError):
        return []

    def local_name(tag: str) -> str:
        return tag.rsplit("}", 1)[-1]

    properties: dict[str, str] = {}
    for element in document.iter():
        if local_name(element.tag) == "properties":
            for child in element:
                properties[local_name(child.tag)] = (child.text or "").strip()

    dependencies: set[str] = set()
    for dependency in document.iter():
        if local_name(dependency.tag) != "dependency":
            continue
        values = {
            local_name(child.tag): (child.text or "").strip()
            for child in dependency
        }
        group = values.get("groupId")
        artifact = values.get("artifactId")
        if not group or not artifact:
            continue
        version = values.get("version", "managed")
        property_match = re.fullmatch(r"\$\{([^}]+)}", version)
        if property_match:
            version = properties.get(property_match.group(1), version)
        scope = values.get("scope", "compile")
        optional = ",optional" if values.get("optional", "").lower() == "true" else ""
        dependencies.add(f"{rel(pom, root)}:{scope}{optional}:{group}:{artifact}:{version}")
    return sorted(dependencies)


def parse_gradle_dependencies(path: Path, root: Path) -> list[str]:
    configurations = (
        "api|implementation|compileOnly|compileOnlyApi|runtimeOnly|"
        "testImplementation|testCompileOnly|testRuntimeOnly|annotationProcessor"
    )
    pattern = re.compile(
        rf"(?m)^\s*({configurations})\s*(?:\(|\s)\s*"
        r"([\"'][^\"']+[\"']|project\([^\n)]+\)|libs\.[A-Za-z0-9_.-]+)"
    )
    return sorted(
        {
            f"{rel(path, root)}:{match.group(1)}:{match.group(2)}"
            for match in pattern.finditer(read_text(path))
        }
    )


def declared_dependencies(build_files: list[Path], root: Path) -> list[str]:
    dependencies: set[str] = set()
    for path in build_files:
        if path.name == "pom.xml":
            dependencies.update(parse_maven_dependencies(path, root))
        elif path.name in {"build.gradle", "build.gradle.kts"}:
            dependencies.update(parse_gradle_dependencies(path, root))
    return sorted(dependencies)


def paper_coordinates(build_files: list[Path]) -> list[str]:
    coordinates: set[str] = set()
    for path in build_files:
        if path.name == "pom.xml":
            coordinates.update(parse_maven_paper_coordinates(path))
            continue
        text = read_text(path)
        coordinates.update(
            re.findall(r"io\.papermc\.paper:paper-api:[^\"'\s)]+", text)
        )
        coordinates.update(
            f"paperDevBundle:{value}"
            for value in re.findall(r"paperDevBundle\s*\(\s*[\"']([^\"']+)", text)
        )
    return sorted(coordinates)


def java_version_evidence(build_files: list[Path], root: Path) -> list[str]:
    evidence: set[str] = set()
    for path in build_files:
        label = rel(path, root)
        text = read_text(path)
        if path.name == "pom.xml":
            try:
                document = ET.parse(path).getroot()
            except (ET.ParseError, OSError):
                continue
            for element in document.iter():
                key = element.tag.rsplit("}", 1)[-1]
                value = (element.text or "").strip()
                if key in {"java.version", "maven.compiler.release", "maven.compiler.source", "maven.compiler.target", "release", "source", "target"} and re.fullmatch(r"\d+", value):
                    evidence.add(f"{label}:{key}={value}")
            continue
        for match in re.finditer(r"JavaLanguageVersion\.of\s*\(\s*(\d+)\s*\)", text):
            evidence.add(f"{label}:toolchain={match.group(1)}")
        for match in re.finditer(r"options\.release\.set\s*\(\s*(\d+)\s*\)", text):
            evidence.add(f"{label}:release={match.group(1)}")
        for match in re.finditer(r"(?:sourceCompatibility|targetCompatibility)\s*=\s*(?:JavaVersion\.VERSION_)?(\d+)", text):
            evidence.add(f"{label}:compatibility={match.group(1)}")
    return sorted(evidence)


def parse_maven_modules(pom: Path) -> list[str]:
    text = read_text(pom)
    return sorted(set(re.findall(r"<module>\s*([^<]+?)\s*</module>", text)))


def parse_gradle_modules(settings_files: list[Path]) -> list[str]:
    modules: set[str] = set()
    for path in settings_files:
        text = read_text(path)
        for call in re.findall(r"include\s*\((.*?)\)", text, re.DOTALL):
            modules.update(re.findall(r"[\"'](:?[^\"']+)[\"']", call))
        for call in re.findall(r"(?m)^\s*include\s+(.+)$", text):
            modules.update(re.findall(r"[\"'](:?[^\"']+)[\"']", call))
    return sorted(modules)


def descriptor_summary(path: Path, root: Path) -> dict[str, object]:
    text = read_text(path)
    keys: dict[str, str] = {}
    for raw_line in text.splitlines():
        if not raw_line or raw_line[0].isspace() or raw_line.lstrip().startswith("#"):
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$", raw_line)
        if match:
            keys[match.group(1)] = match.group(2).strip("'\"")
    return {
        "path": rel(path, root),
        "kind": path.name,
        "name": keys.get("name"),
        "version": keys.get("version"),
        "main": keys.get("main"),
        "api_version": keys.get("api-version"),
        "folia_supported": keys.get("folia-supported"),
        "has_unresolved_placeholders": bool(
            re.search(r"\$\{[^}]+}|@[A-Za-z0-9_.-]+@", text)
        ),
    }


def build_report(root: Path) -> dict[str, object]:
    build_names = {
        "build.gradle",
        "build.gradle.kts",
        "settings.gradle",
        "settings.gradle.kts",
        "pom.xml",
        "build.xml",
        "gradle.properties",
    }
    build_files = files_named(root, build_names)
    settings_files = [p for p in build_files if p.name.startswith("settings.gradle")]
    pom_files = [p for p in build_files if p.name == "pom.xml"]
    sources = source_files(root)
    descriptors = files_named(root, DESCRIPTORS)
    ci_files = sorted(
        path
        for path in (root / ".github" / "workflows").glob("*.y*ml")
        if path.is_file()
    ) if (root / ".github" / "workflows").is_dir() else []

    detected_paper_coordinates = paper_coordinates(build_files)
    dependencies = declared_dependencies(build_files, root)
    java_versions = java_version_evidence(build_files, root)

    evidence_patterns = {
        "java_plugin_entrypoints": r"extends\s+JavaPlugin\b|:\s*JavaPlugin\s*\(",
        "paper_bootstrappers": r"implements\s+PluginBootstrap\b|:\s*PluginBootstrap\b",
        "paper_loaders": r"implements\s+PluginLoader\b|:\s*PluginLoader\b",
        "lifecycle_commands": r"LifecycleEvents\.COMMANDS|registerCommand\s*\(",
        "legacy_commands": r"getCommand\s*\(|setExecutor\s*\(",
        "event_registration": r"registerEvents\s*\(|@EventHandler\b",
        "bukkit_scheduling": r"BukkitScheduler|runTask(?:Later|Timer|Asynchronously|LaterAsynchronously|TimerAsynchronously)?\s*\(",
        "folia_scheduler_apis": r"RegionScheduler|GlobalRegionScheduler|AsyncScheduler|EntityScheduler|Bukkit\.get(?:Region|GlobalRegion|Async)Scheduler\s*\(",
        "configuration": r"saveDefaultConfig\s*\(|reloadConfig\s*\(|YamlConfiguration|ConfigurationSerializable",
        "persistence": r"PersistentDataContainer|PersistentDataType|DataComponentTypes|java\.sql\.|DataSource\b",
        "minecraft_internals": r"import\s+(?:net\.minecraft|org\.bukkit\.craftbukkit)",
        "reflection": r"java\.lang\.reflect|Class\.forName\s*\(",
    }
    evidence = {
        key: matching_files(sources, pattern, root)
        for key, pattern in evidence_patterns.items()
    }

    tests = [
        rel(path, root)
        for path in sources
        if any(part in {"test", "integrationTest", "functionalTest"} for part in path.parts)
    ]

    build_systems: list[str] = []
    if any(p.name.startswith("build.gradle") for p in build_files):
        build_systems.append("Gradle")
    if pom_files:
        build_systems.append("Maven")
    if any(p.name == "build.xml" for p in build_files):
        build_systems.append("Ant")

    warnings: list[str] = []
    if not descriptors:
        warnings.append("No source plugin.yml or paper-plugin.yml was found; check generated metadata.")
    if len(descriptors) > 1:
        warnings.append("Multiple descriptors were found; map each one to its deployable artifact.")
    if any(p.name == "paper-plugin.yml" for p in descriptors):
        warnings.append("paper-plugin.yml is experimental; verify bootstrap, loader, dependencies, and target support.")
    if not detected_paper_coordinates:
        warnings.append("The Paper API/dev-bundle coordinate was not identified automatically.")
    if evidence["minecraft_internals"]:
        warnings.append("Minecraft internals evidence exists; require an API-first justification and per-target tests.")
    if evidence["reflection"]:
        warnings.append("Reflection evidence exists; inspect whether it is compatibility glue and keep it out of hot paths.")
    if any(d.get("folia_supported") == "true" for d in map(lambda p: descriptor_summary(p, root), descriptors)):
        warnings.append("Folia support is declared; compilation is not evidence of region-thread safety.")

    return {
        "root": str(root),
        "build_systems": build_systems,
        "wrappers": {
            "gradle": (root / "gradlew").is_file(),
            "maven": (root / "mvnw").is_file(),
        },
        "build_files": [rel(path, root) for path in build_files],
        "modules": {
            "gradle": parse_gradle_modules(settings_files),
            "maven": sorted({module for pom in pom_files for module in parse_maven_modules(pom)}),
        },
        "paper_coordinates": detected_paper_coordinates,
        "declared_dependencies": dependencies,
        "java_version_evidence": java_versions,
        "descriptors": [descriptor_summary(path, root) for path in descriptors],
        "source_file_count": len(sources),
        "evidence": evidence,
        "tests": tests,
        "ci_workflows": [rel(path, root) for path in ci_files],
        "warnings": warnings,
    }


def print_text(report: dict[str, object]) -> None:
    print("Paper project inventory (evidence, not runtime proof)")
    print(f"Root: {report['root']}")
    print(f"Build systems: {', '.join(report['build_systems']) or 'unknown'}")
    wrappers = report["wrappers"]
    print(f"Wrappers: Gradle={wrappers['gradle']} Maven={wrappers['maven']}")
    print("Build files:")
    for item in report["build_files"]:
        print(f"  - {item}")
    modules = report["modules"]
    print(f"Modules: Gradle={modules['gradle'] or 'none found'} Maven={modules['maven'] or 'none found'}")
    print(f"Paper coordinates: {report['paper_coordinates'] or 'unknown'}")
    print("Declared dependencies:")
    for item in report["declared_dependencies"]:
        print(f"  - {item}")
    if not report["declared_dependencies"]:
        print("  - none found")
    print(f"Java evidence: {report['java_version_evidence'] or 'unknown'}")
    print("Descriptors:")
    for item in report["descriptors"]:
        print(
            "  - {path}: name={name!r} version={version!r} main={main!r} "
            "api-version={api_version!r} folia-supported={folia_supported!r} placeholders={has_unresolved_placeholders}".format(
                **item
            )
        )
    print(f"Source files: {report['source_file_count']}")
    print("Architecture/API evidence:")
    for key, paths in report["evidence"].items():
        print(f"  - {key}: {', '.join(paths) if paths else 'none found'}")
    print(f"Tests: {', '.join(report['tests']) if report['tests'] else 'none found'}")
    print(f"CI: {', '.join(report['ci_workflows']) if report['ci_workflows'] else 'none found'}")
    if report["warnings"]:
        print("Review warnings:")
        for warning in report["warnings"]:
            print(f"  - {warning}")


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2
    report = build_report(root)
    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

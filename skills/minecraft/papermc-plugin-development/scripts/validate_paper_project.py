#!/usr/bin/env python3
"""Build and statically validate a Paper plugin artifact.

This script intentionally reports the real-server checks it cannot prove.
"""

from __future__ import annotations

import argparse
import os
import re
from paper_descriptor import has_unresolved_placeholders, top_level_yaml
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path


DESCRIPTOR_NAMES = ("plugin.yml", "paper-plugin.yml")
IGNORED_JAR_MARKERS = ("-sources", "-javadoc", "-tests", "original-", "-plain")
SUMMARY_TAIL_LINES = 40
SUMMARY_TAIL_CHARS = 8_000
SUMMARY_TAIL_SCAN_BYTES = 64 * 1024
LONG_LINE_MARKER = "\n... [middle of long diagnostic omitted] ...\n"
CLIPPED_LINE_MARKER = "... [beginning of diagnostic line is outside scan window] ...\n"
TAIL_TRUNCATION_MARKER = "... [earlier build output omitted] ...\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the repository-native build and inspect a Paper plugin JAR."
    )
    parser.add_argument("root", nargs="?", default=".", help="repository root")
    parser.add_argument("--artifact", type=Path, help="exact deployable JAR to inspect")
    parser.add_argument(
        "--build-system",
        choices=("gradle", "maven"),
        help="select the build when both Gradle and Maven are present",
    )
    parser.add_argument(
        "--build-task",
        action="append",
        default=[],
        help="Gradle task or Maven goal to run instead of the default; repeat for multiple tasks",
    )
    parser.add_argument(
        "--java-home",
        type=Path,
        help="JDK home for the build; useful when the repository target differs from the shell JDK",
    )
    parser.add_argument("--skip-build", action="store_true", help="inspect an existing artifact")
    parser.add_argument(
        "--compile-only",
        action="store_true",
        help="compile without producing/inspecting a JAR",
    )
    parser.add_argument(
        "--summary-capture",
        action="store_true",
        help="capture the complete build log and print a bounded failure tail",
    )
    return parser.parse_args()


def build_command(
    root: Path, compile_only: bool, requested: str | None, build_tasks: list[str]
) -> tuple[list[str], str | None]:
    has_gradle = any(
        (root / name).is_file()
        for name in (
            "gradlew",
            "settings.gradle",
            "settings.gradle.kts",
            "build.gradle",
            "build.gradle.kts",
        )
    )
    has_maven = any((root / name).is_file() for name in ("mvnw", "pom.xml"))
    if requested == "gradle" and not has_gradle:
        raise RuntimeError("--build-system gradle was selected, but no root Gradle build was found")
    if requested == "maven" and not has_maven:
        raise RuntimeError("--build-system maven was selected, but no root Maven build was found")
    if requested is None and has_gradle and has_maven:
        raise RuntimeError("both Gradle and Maven are present; select the authoritative build with --build-system")
    selected = requested or ("gradle" if has_gradle else "maven" if has_maven else None)
    actions = build_tasks or (["classes"] if compile_only else ["build"])
    if selected == "gradle" and (root / "gradlew").is_file():
        return (["./gradlew", *actions], None)
    if selected == "gradle":
        gradle = shutil.which("gradle")
        if gradle:
            return ([gradle, *actions], "Gradle wrapper absent; used system Gradle.")
        raise RuntimeError("Gradle project has no ./gradlew and no system gradle was found")
    if selected == "maven":
        actions = build_tasks or (["compile"] if compile_only else ["verify"])
        if (root / "mvnw").is_file():
            return (["./mvnw", "-B", *actions], None)
        maven = shutil.which("mvn")
        if maven:
            return ([maven, "-B", *actions], "Maven wrapper absent; used system Maven.")
        raise RuntimeError("Maven project has no ./mvnw and no system mvn was found")
    raise RuntimeError("No supported Gradle or Maven build was detected")


def source_descriptors(root: Path) -> list[Path]:
    found: list[Path] = []
    for name in DESCRIPTOR_NAMES:
        found.extend(
            path
            for path in root.rglob(name)
            if path.is_file()
            and not any(
                part in {".git", "build", "target", "out"}
                for part in path.relative_to(root).parts
            )
        )
    return sorted(found)


def descriptor_issues(name: str, text: str) -> tuple[list[str], list[str], dict[str, str]]:
    failures: list[str] = []
    warnings: list[str] = []
    values = top_level_yaml(text)
    for key in ("name", "version", "main"):
        if not values.get(key):
            failures.append(f"{name}: missing top-level {key!r}")
    if has_unresolved_placeholders(values):
        failures.append(f"{name}: unresolved resource placeholder remains")
    if not values.get("api-version"):
        warnings.append(f"{name}: api-version is absent; confirm legacy compatibility is intentional")
    if name == "paper-plugin.yml":
        warnings.append("paper-plugin.yml is experimental; runtime-test bootstrap, dependencies, and classloading")
    if values.get("folia-supported", "").lower() == "true":
        warnings.append("Folia support is declared; an actual multi-region Folia run is required")
    return failures, warnings, values


def validate_source_descriptors(root: Path) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    paths = source_descriptors(root)
    if not paths:
        warnings.append("No static source descriptor found; verify whether the build generates it")
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        found_failures, found_warnings, values = descriptor_issues(str(path.relative_to(root)), text)
        # Source descriptors may intentionally contain build placeholders.
        found_failures = [
            item for item in found_failures if "unresolved resource placeholder" not in item
        ]
        if has_unresolved_placeholders(values):
            found_warnings.append(f"{path.relative_to(root)}: build must resolve descriptor placeholders")
        failures.extend(found_failures)
        warnings.extend(found_warnings)
    return failures, warnings


def candidate_artifacts(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for path in root.rglob("*.jar"):
        relative_parts = path.relative_to(root).parts
        in_gradle_libs = ("build", "libs") in zip(relative_parts, relative_parts[1:])
        if (in_gradle_libs or path.parent.name == "target") and not any(
            marker in path.name for marker in IGNORED_JAR_MARKERS
        ):
            candidates.append(path.resolve())
    return sorted(set(candidates))


def select_artifact(root: Path, explicit: Path | None) -> Path:
    if explicit:
        path = explicit if explicit.is_absolute() else root / explicit
        path = path.resolve()
        if not path.is_file():
            raise RuntimeError(f"artifact does not exist: {path}")
        return path
    candidates = candidate_artifacts(root)
    deployable: list[Path] = []
    for path in candidates:
        try:
            with zipfile.ZipFile(path) as jar:
                if any(name in jar.namelist() for name in DESCRIPTOR_NAMES):
                    deployable.append(path)
        except zipfile.BadZipFile:
            continue
    if len(deployable) == 1:
        return deployable[0]
    if not deployable:
        raise RuntimeError("no built JAR containing plugin.yml or paper-plugin.yml was found")
    choices = "\n  - ".join(str(path) for path in deployable)
    raise RuntimeError(f"multiple deployable JARs found; pass --artifact explicitly:\n  - {choices}")


def inspect_jar(path: Path) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    try:
        jar = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        return ([f"not a valid JAR/ZIP: {path}"], warnings)
    with jar:
        names = set(jar.namelist())
        descriptors = [name for name in DESCRIPTOR_NAMES if name in names]
        if not descriptors:
            failures.append("artifact has no root plugin.yml or paper-plugin.yml")
            return failures, warnings
        if len(descriptors) == 2:
            warnings.append("artifact contains both descriptors; confirm coexistence is intentional")
        for descriptor in descriptors:
            text = jar.read(descriptor).decode("utf-8", errors="replace")
            found_failures, found_warnings, values = descriptor_issues(descriptor, text)
            failures.extend(found_failures)
            warnings.extend(found_warnings)
            for class_field in ("main", "bootstrapper", "loader"):
                class_name = values.get(class_field)
                if not class_name or re.search(r"\$\{|@", class_name):
                    continue
                class_path = class_name.replace(".", "/") + ".class"
                if class_path not in names:
                    failures.append(
                        f"{descriptor}: {class_field} class is absent from JAR: {class_path}"
                    )
        if "org/bukkit/Bukkit.class" in names or "io/papermc/paper/plugin/PluginInitializerManager.class" in names:
            failures.append("artifact appears to bundle the Bukkit/Paper server API")
        service_count = sum(name.startswith("META-INF/services/") and not name.endswith("/") for name in names)
        if service_count:
            warnings.append(f"artifact contains {service_count} service descriptor(s); verify shading merged them")
    return failures, warnings


def print_results(label: str, failures: list[str], warnings: list[str]) -> None:
    print(label)
    for failure in failures:
        print(f"  FAIL: {failure}")
    for warning in warnings:
        print(f"  WARN: {warning}")
    if not failures and not warnings:
        print("  PASS")


def build_log_path(root: Path) -> Path:
    temp_dir = Path(tempfile.gettempdir()).resolve()
    if root == temp_dir or root in temp_dir.parents:
        raise RuntimeError(
            f"temporary directory is inside the project tree; set TMPDIR outside {root}"
        )
    try:
        descriptor, name = tempfile.mkstemp(
            prefix="paper-validation-", suffix=".log", dir=temp_dir
        )
    except OSError as error:
        raise RuntimeError(f"could not create temporary build log: {error}") from error
    path = Path(name)
    try:
        os.close(descriptor)
    except OSError as error:
        try:
            os.close(descriptor)
        except OSError:
            pass
        try:
            path.unlink()
        except OSError as cleanup_error:
            raise RuntimeError(
                f"could not create temporary build log: {error}; "
                f"log path retained after cleanup failure: {path} ({cleanup_error})"
            ) from error
        raise RuntimeError(f"could not create temporary build log: {error}") from error
    try:
        os.chmod(path, 0o600)
    except OSError:
        # mkstemp is private by default; retain that platform default when chmod is unavailable.
        pass
    return path


def build_failure_tail(path: Path) -> str:
    with path.open("rb") as log:
        log.seek(0, os.SEEK_END)
        end = log.tell()
        start = max(0, end - SUMMARY_TAIL_SCAN_BYTES)
        log.seek(start)
        text = log.read(end - start).decode("utf-8", "ignore" if start else "replace")
    clipped_line = False
    if start:
        first_newline = text.find("\n")
        if first_newline >= 0:
            leading = text[:first_newline].rstrip("\r")
            remainder = text[first_newline + 1 :]
            if remainder.strip():
                text = remainder
            else:
                text = leading
                clipped_line = True
        else:
            clipped_line = True
    lines = text.splitlines()[-SUMMARY_TAIL_LINES:]
    if clipped_line and lines:
        suffix_length = SUMMARY_TAIL_CHARS - len(CLIPPED_LINE_MARKER)
        return CLIPPED_LINE_MARKER + lines[-1][-suffix_length:]
    if lines and len(lines[-1]) > SUMMARY_TAIL_CHARS:
        line = lines[-1]
        available = SUMMARY_TAIL_CHARS - len(LONG_LINE_MARKER)
        prefix_length = available // 2
        suffix_length = available - prefix_length
        return (
            line[:prefix_length]
            + LONG_LINE_MARKER
            + line[-suffix_length:]
        )
    tail = "\n".join(lines)
    if len(tail) > SUMMARY_TAIL_CHARS:
        suffix_length = SUMMARY_TAIL_CHARS - len(TAIL_TRUNCATION_MARKER)
        tail = TAIL_TRUNCATION_MARKER + tail[-suffix_length:]
    return tail


def main() -> int:
    args = parse_args()
    if args.summary_capture and args.skip_build:
        print("error: --summary-capture cannot be combined with --skip-build", file=sys.stderr)
        return 2
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2
    source_failures, source_warnings = validate_source_descriptors(root)
    print_results("Source descriptor checks:", source_failures, source_warnings)
    sys.stdout.flush()
    if source_failures:
        return 1

    if args.skip_build and args.build_task:
        print("error: --skip-build cannot be combined with --build-task", file=sys.stderr)
        return 2
    if args.compile_only and args.build_task:
        print("error: --compile-only cannot be combined with --build-task", file=sys.stderr)
        return 2

    build_started_at: float | None = None
    if not args.skip_build:
        try:
            command, warning = build_command(
                root, args.compile_only, args.build_system, args.build_task
            )
        except RuntimeError as error:
            print(f"error: {error}", file=sys.stderr)
            return 2
        if warning:
            print(f"WARN: {warning}")
        print(f"Running: {' '.join(command)}")
        environment = os.environ.copy()
        if args.java_home:
            java_home = args.java_home.resolve()
            java_binary = java_home / "bin" / "java"
            if not java_binary.is_file():
                print(f"error: --java-home has no bin/java: {java_home}", file=sys.stderr)
                return 2
            environment["JAVA_HOME"] = str(java_home)
            environment["PATH"] = str(java_home / "bin") + os.pathsep + environment.get("PATH", "")
            print(f"Build JDK: {java_home}")
        sys.stdout.flush()
        build_started_at = time.time()
        build_log: Path | None = None
        if args.summary_capture:
            try:
                build_log = build_log_path(root)
            except RuntimeError as error:
                print(f"error: {error}", file=sys.stderr)
                return 2
            try:
                with build_log.open("wb") as output:
                    result = subprocess.run(
                        command,
                        cwd=root,
                        check=False,
                        env=environment,
                        stdout=output,
                        stderr=subprocess.STDOUT,
                    )
            except OSError as error:
                try:
                    build_log.unlink()
                except OSError as cleanup_error:
                    print(
                        f"error: could not write build log {build_log}: {error}; "
                        f"log path retained after cleanup failure: {cleanup_error}",
                        file=sys.stderr,
                    )
                else:
                    print(f"error: could not write build log {build_log}: {error}", file=sys.stderr)
                return 2
            print(f"Build exit status: {result.returncode}")
            print(f"Build log: {build_log}")
        else:
            result = subprocess.run(command, cwd=root, check=False, env=environment)
        if result.returncode:
            if build_log:
                print("Build failure tail:")
                try:
                    tail = build_failure_tail(build_log)
                except OSError as error:
                    print(f"WARN: could not read build log {build_log}: {error}", file=sys.stderr)
                else:
                    if tail:
                        print(tail)
            print(f"FAIL: build exited with status {result.returncode}", file=sys.stderr)
            return result.returncode or 1
    elif args.compile_only:
        print("error: --skip-build and --compile-only cannot be combined", file=sys.stderr)
        return 2

    if args.compile_only:
        print("Compile-only gate passed; artifact inspection was intentionally skipped.")
    else:
        try:
            artifact = select_artifact(root, args.artifact)
        except RuntimeError as error:
            print(f"error: {error}", file=sys.stderr)
            return 2
        print(f"Inspecting artifact: {artifact}")
        if build_started_at is not None and artifact.stat().st_mtime < build_started_at - 1:
            print(
                "WARN: artifact predates this build invocation; it may be an up-to-date output "
                "or a stale JAR from a task the build did not run"
            )
        jar_failures, jar_warnings = inspect_jar(artifact)
        print_results("Artifact checks:", jar_failures, jar_warnings)
        if jar_failures:
            return 1

    print("Manual runtime gates still required:")
    print("  - clean target Paper startup and plugin enable")
    print("  - command, permission, event, configuration, and integration behavior")
    print("  - clean disable plus second startup with persisted data")
    print("  - scheduler ownership and async error/cancellation paths")
    print("  - actual multi-region Folia run when Folia support is claimed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

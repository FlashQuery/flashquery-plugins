#!/usr/bin/env python3
"""Build .plugin archives from plugin source directories.

A plugin source directory contains:
  <plugin>/.claude-plugin/plugin.json
  <plugin>/skills/...
  <plugin>/commands/...    (optional)
  <plugin>/...             (any other supporting files)

The output `<plugin>.plugin` is a zip placed next to the source directory and
contains all files rooted at `<plugin>/...` (so installers see the plugin name
as the top-level folder).

Usage:
  build_plugin.py <plugin_dir>...   Build the listed plugin source dirs
  build_plugin.py --all             Build every plugin under core/ and apps/

Examples:
  python3 scripts/build_plugin.py core/fq-base
  python3 scripts/build_plugin.py --all
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXCLUDED_DIRS = {"__pycache__", "evals", ".DS_Store", "node_modules"}
EXCLUDED_FILES = {".DS_Store"}


def discover_plugin_dirs() -> list[Path]:
    """Find every plugin source directory under core/ and apps/."""
    roots = [REPO_ROOT / "core", REPO_ROOT / "apps"]
    plugins: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        for entry in sorted(root.iterdir()):
            if entry.is_dir() and (entry / ".claude-plugin" / "plugin.json").is_file():
                plugins.append(entry)
    return plugins


def validate(plugin_dir: Path) -> list[str]:
    errors: list[str] = []

    manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
    if not manifest_path.is_file():
        errors.append(f"MISSING: {manifest_path}")
        return errors

    try:
        manifest = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as e:
        errors.append(f"plugin.json is invalid JSON: {e}")
        return errors

    for field in ("name", "version", "description"):
        if field not in manifest:
            errors.append(f"plugin.json missing required field: {field}")

    claude_plugin_dir = plugin_dir / ".claude-plugin"
    for item in claude_plugin_dir.iterdir():
        if item.name != "plugin.json":
            errors.append(
                f".claude-plugin/ should only contain plugin.json, found: {item.name}"
            )

    skills_dir = plugin_dir / "skills"
    if skills_dir.is_dir():
        for skill in sorted(skills_dir.iterdir()):
            if skill.is_dir() and not (skill / "SKILL.md").is_file():
                errors.append(f"Skill '{skill.name}' missing SKILL.md")

    return errors


def build_one(plugin_dir: Path) -> Path:
    plugin_dir = plugin_dir.resolve()
    if not plugin_dir.is_dir():
        raise SystemExit(f"Plugin directory not found: {plugin_dir}")

    manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
    if not manifest_path.is_file():
        raise SystemExit(f"Not a plugin directory (no .claude-plugin/plugin.json): {plugin_dir}")

    manifest = json.loads(manifest_path.read_text())
    print(f"\n=== {plugin_dir.relative_to(REPO_ROOT)} (name={manifest.get('name')}, version={manifest.get('version')}) ===")

    errors = validate(plugin_dir)
    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  ✗ {e}")
        raise SystemExit(1)

    output_path = plugin_dir.parent / f"{plugin_dir.name}.plugin"
    arcroot = plugin_dir.parent  # so files are stored as "<plugin-name>/..."
    file_count = 0
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(plugin_dir):
            dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRS)
            for file in sorted(files):
                if file in EXCLUDED_FILES:
                    continue
                filepath = Path(root) / file
                arcname = filepath.relative_to(arcroot).as_posix()
                zf.write(filepath, arcname)
                file_count += 1

    size_kb = output_path.stat().st_size / 1024
    print(f"  built {output_path.relative_to(REPO_ROOT)} ({file_count} files, {size_kb:.1f} KB)")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plugins", nargs="*", help="Plugin source directories to build")
    parser.add_argument("--all", action="store_true", help="Build every plugin under core/ and apps/")
    args = parser.parse_args()

    if args.all and args.plugins:
        parser.error("Pass either --all or explicit plugin directories, not both.")

    if args.all:
        targets = discover_plugin_dirs()
        if not targets:
            print("No plugin source directories found under core/ or apps/.")
            return 1
    elif args.plugins:
        targets = [Path(p) for p in args.plugins]
    else:
        parser.print_help()
        return 1

    for target in targets:
        build_one(target)
    print(f"\nDone: {len(targets)} plugin(s) built.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Build the distributable package ZIP.

Output: dist/<name>-<version>.zip, with package files at the ZIP root:
  plugin.json, mcp.json, LICENSE, README.md, assets/, skills/

plugin.json and mcp.json are copies of plugin-manifest.json and
mcp-manifest.json (the portable format); they exist only inside the ZIP.
Maintainer-only files (DEVELOPMENT.md, scripts/, .github/, .git, dist/) and
OS junk (.DS_Store) are never included. The version comes from plugin-manifest.json.
Docs-sync snippet markers are stripped from the packaged SKILL.md files only;
the files in the repo are not modified.
"""
import json
import pathlib
import re
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
FILES = ["LICENSE", "README.md"]
# Portable (OpenAI) files: source in the repo -> name inside the ZIP.
GENERATED = {"plugin-manifest.json": "plugin.json", "mcp-manifest.json": "mcp.json"}
DIRS = ["assets", "skills"]
SKIP_NAMES = {".DS_Store", "Thumbs.db"}

# Fixed timestamp so identical sources produce an identical ZIP.
EPOCH = (2020, 1, 1, 0, 0, 0)


# Docs-sync snippet markers (e.g. `<!-- --8<-- [start:body] -->`) stay in the
# repo for the documentation sync, but are removed from the shipped skills.
SNIPPET_MARKER = re.compile(r"^<!-- --8<-- \[(?:start|end):[^\]]+\] -->\n", re.M)


def package_bytes(path: pathlib.Path) -> bytes:
    data = path.read_bytes()
    if path.name == "SKILL.md":
        data = SNIPPET_MARKER.sub("", data.decode("utf-8")).encode("utf-8")
    return data


def main() -> int:
    meta = json.loads((ROOT / "plugin-manifest.json").read_text())
    out_dir = ROOT / "dist"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"{meta['name']}-{meta['version']}.zip"

    members: list[pathlib.Path] = [ROOT / f for f in FILES]
    for d in DIRS:
        members += sorted(p for p in (ROOT / d).rglob("*")
                          if p.is_file() and p.name not in SKIP_NAMES)

    missing = [p for p in members + [ROOT / s for s in GENERATED] if not p.is_file()]
    if missing:
        print("missing package files: " + ", ".join(str(m.relative_to(ROOT)) for m in missing),
              file=sys.stderr)
        return 1

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for src_name, zip_name in GENERATED.items():
            info = zipfile.ZipInfo(zip_name, EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, (ROOT / src_name).read_bytes())
        for path in members:
            info = zipfile.ZipInfo(str(path.relative_to(ROOT)), EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, package_bytes(path))

    print(f"built {out.relative_to(ROOT)} ({len(members) + len(GENERATED)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Generate client manifests from the root plugin.json.

Root plugin.json is the single source of truth for identity, version,
description, and listing URLs. This script derives:
  - .claude-plugin/plugin.json       (Claude requires its own manifest)
  - .claude-plugin/marketplace.json  (shared single-plugin marketplace)

Usage:
  python3 scripts/sync_manifests.py           # write .claude-plugin/plugin.json
  python3 scripts/sync_manifests.py --check   # exit 1 if it is out of date (CI)
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE = ROOT / "plugin.json"
TARGET = ROOT / ".claude-plugin" / "plugin.json"

# Fields copied verbatim from the root manifest.
SHARED = ["name", "version", "description", "author", "homepage",
          "repository", "license", "keywords"]


def build() -> dict:
    src = json.loads(SOURCE.read_text())
    iface = src["extensions"]["com.openai"]["interface"]
    out = {k: src[k] for k in SHARED}
    # Claude author takes name/email only.
    out["author"] = {k: v for k, v in src["author"].items() if k in ("name", "email")}
    out["displayName"] = iface["displayName"]
    out["supportUrl"] = iface["supportURL"]
    out["documentationUrl"] = src["homepage"]
    out["termsOfServiceUrl"] = iface["termsOfServiceURL"]
    out["privacyPolicyUrl"] = iface["privacyPolicyURL"]
    out["icon"] = "assets/icon.png"
    out["mcpServers"] = "./mcp.json"
    return out


MARKETPLACE_TARGET = ROOT / ".claude-plugin" / "marketplace.json"
MARKETPLACE_NAME = "ringcentral"
MARKETPLACE_OWNER = "RingCentral"


def build_marketplace() -> dict:
    """Single-plugin marketplace shared by every client.

    `interface` and `policy` are read by OpenAI clients; Claude ignores them
    (validation reports warnings for them, which is expected).
    """
    src = json.loads(SOURCE.read_text())
    iface = src["extensions"]["com.openai"]["interface"]
    return {
        "name": MARKETPLACE_NAME,
        "description": src["description"],
        "interface": {"displayName": iface["displayName"]},
        "owner": {"name": MARKETPLACE_OWNER, "email": src["author"]["email"]},
        "plugins": [
            {
                "name": src["name"],
                "source": "./",
                "description": src["description"],
                "category": iface["category"],
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
            }
        ],
    }


def main() -> int:
    outputs = {
        TARGET: json.dumps(build(), indent=2) + "\n",
        MARKETPLACE_TARGET: json.dumps(build_marketplace(), indent=2) + "\n",
    }
    if "--check" in sys.argv:
        stale = [p for p, text in outputs.items()
                 if (p.read_text() if p.exists() else "") != text]
        for p in stale:
            print(f"{p.relative_to(ROOT)} is out of date. "
                  "Run: python3 scripts/sync_manifests.py", file=sys.stderr)
        if stale:
            return 1
        print("manifests in sync")
        return 0
    for path, text in outputs.items():
        path.parent.mkdir(exist_ok=True)
        path.write_text(text)
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

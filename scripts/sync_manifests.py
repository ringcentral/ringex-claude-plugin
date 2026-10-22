#!/usr/bin/env python3
"""Generate client manifests from plugin-manifest.json.

plugin-manifest.json is the single source of truth for identity, version,
description, and listing URLs. This script derives:
  - .claude-plugin/plugin.json       (Claude requires its own manifest)
  - .mcp.json                        (clean MCP config for Claude)
  - .claude-plugin/marketplace.json  (clean Claude marketplace)
  - .agents/plugins/marketplace.json (Codex marketplace, with interface/policy)

The OpenAI-portable root plugin.json and mcp.json are NOT written to the repo;
scripts/build_package.py generates them inside the package ZIP only.

Usage:
  python3 scripts/sync_manifests.py           # write all generated manifests
  python3 scripts/sync_manifests.py --check   # exit 1 if it is out of date (CI)
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE = ROOT / "plugin-manifest.json"
TARGET = ROOT / ".claude-plugin" / "plugin.json"

# Fields copied verbatim from plugin-manifest.json.
SHARED = ["name", "version", "description", "author", "homepage",
          "repository", "license", "keywords"]


def build() -> dict:
    src = json.loads(SOURCE.read_text())
    iface = src["extensions"]["com.openai"]["interface"]
    out = {k: src[k] for k in SHARED}
    # Claude author takes name/email only.
    out["author"] = {k: v for k, v in src["author"].items() if k in ("name", "email")}
    out["displayName"] = iface["displayName"]
    # privacyPolicyUrl is required for plugins that use a remote MCP server
    # (PRIVACY_URL_MISSING), so it is sourced from the interface block.
    out["privacyPolicyUrl"] = iface["privacyPolicyURL"]
    # Other listing-only keys (supportUrl, documentationUrl, termsOfServiceUrl,
    # icon) are intentionally omitted: the submission checker flags them as
    # UNKNOWN_KEY_CROSS_TOOL. Enter them in the submission form.
    out["mcpServers"] = "./.mcp.json"
    return out


MCP_SOURCE = ROOT / "mcp-manifest.json"
MCP_TARGET = ROOT / ".mcp.json"


def build_mcp() -> dict:
    """Clean Claude MCP config: no $schema, no per-server `extensions`."""
    src = json.loads(MCP_SOURCE.read_text())
    servers = {
        name: {k: v for k, v in cfg.items() if k != "extensions"}
        for name, cfg in src["mcpServers"].items()
    }
    return {"mcpServers": servers}


MARKETPLACE_TARGET = ROOT / ".claude-plugin" / "marketplace.json"
CODEX_MARKETPLACE_TARGET = ROOT / ".agents" / "plugins" / "marketplace.json"
MARKETPLACE_NAME = "ringcentral"
MARKETPLACE_OWNER = "RingCentral"


def build_marketplace() -> dict:
    """Clean single-plugin marketplace for Claude (no unknown fields)."""
    src = json.loads(SOURCE.read_text())
    iface = src["extensions"]["com.openai"]["interface"]
    return {
        "name": MARKETPLACE_NAME,
        "description": src["description"],
        "owner": {"name": MARKETPLACE_OWNER, "email": src["author"]["email"]},
        "plugins": [
            {
                "name": src["name"],
                "source": "./",
                "description": src["description"],
                "category": iface["category"],
            }
        ],
    }


def build_codex_marketplace() -> dict:
    """Marketplace for OpenAI Codex: adds `interface` and `policy`.

    The location may change; adjust CODEX_MARKETPLACE_TARGET if it does.
    """
    out = build_marketplace()
    iface = json.loads(SOURCE.read_text())["extensions"]["com.openai"]["interface"]
    out["interface"] = {"displayName": iface["displayName"]}
    out["plugins"][0]["policy"] = {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL",
    }
    return out


def main() -> int:
    outputs = {
        TARGET: json.dumps(build(), indent=2) + "\n",
        MCP_TARGET: json.dumps(build_mcp(), indent=2) + "\n",
        MARKETPLACE_TARGET: json.dumps(build_marketplace(), indent=2) + "\n",
        CODEX_MARKETPLACE_TARGET: json.dumps(build_codex_marketplace(), indent=2) + "\n",
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
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

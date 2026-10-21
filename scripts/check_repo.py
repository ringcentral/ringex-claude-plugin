#!/usr/bin/env python3
"""Validate repository content. Exits non-zero on any failure (used by CI).

Checks:
  - JSON files parse
  - plugin.json: required fields, semver version, listing field limits
  - mcp.json: HTTPS URLs, no versioned paths, OAuth auth block present
  - skills: each folder has SKILL.md with matching `name` and a `description`
  - no empty directories under skills/
  - no vendor / model names in user-facing text (README, listing metadata, skills)
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def load(rel: str):
    path = ROOT / rel
    try:
        return json.loads(path.read_text())
    except Exception as exc:  # noqa: BLE001
        fail(f"{rel}: invalid JSON ({exc})")
        return None


# ---- JSON + manifests -------------------------------------------------------
plugin = load("plugin.json")
mcp = load("mcp.json")
load(".claude-plugin/plugin.json")
load(".claude-plugin/marketplace.json")

if plugin:
    for key in ("name", "version", "description", "author", "license"):
        if key not in plugin:
            fail(f"plugin.json: missing '{key}'")
    if not re.fullmatch(r"\d+\.\d+\.\d+", plugin.get("version", "")):
        fail("plugin.json: version must be semver (x.y.z)")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", plugin.get("name", "")) or len(plugin["name"]) > 64:
        fail("plugin.json: name must be lowercase-hyphenated, <= 64 chars")
    iface = plugin.get("extensions", {}).get("com.openai", {}).get("interface", {})
    limits = {"displayName": 30, "shortDescription": 30, "longDescription": 4000}
    for key, limit in limits.items():
        if key not in iface:
            fail(f"plugin.json: interface.{key} missing")
        elif len(iface[key]) > limit:
            fail(f"plugin.json: interface.{key} is {len(iface[key])} chars (max {limit})")
    for key in ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"):
        if not str(iface.get(key, "")).startswith("https://"):
            fail(f"plugin.json: interface.{key} must be an HTTPS URL")
    for key in ("composerIcon", "logo"):
        rel = iface.get(key)
        if not rel or not (ROOT / rel).is_file():
            fail(f"plugin.json: interface.{key} missing or file not found ({rel})")

if mcp:
    servers = mcp.get("mcpServers", {})
    if not servers:
        fail("mcp.json: no servers defined")
    for name, cfg in servers.items():
        url = cfg.get("url", "")
        if not url.startswith("https://"):
            fail(f"mcp.json: {name}: url must be HTTPS")
        if re.search(r"/v\d+(\.\d+)*/", url):
            fail(f"mcp.json: {name}: versioned URL path not allowed ({url})")
        auth = cfg.get("extensions", {}).get("com.openai", {}).get("auth")
        if not auth or auth.get("type") not in ("oauth", "mixed", "none", "api_key"):
            fail(f"mcp.json: {name}: missing extensions['com.openai'].auth")

# ---- Skills -----------------------------------------------------------------
skills_dir = ROOT / "skills"
for entry in sorted(skills_dir.iterdir()):
    if not entry.is_dir():
        continue
    skill_md = entry / "SKILL.md"
    if not skill_md.is_file():
        fail(f"skills/{entry.name}: missing SKILL.md")
        continue
    text = skill_md.read_text()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        fail(f"skills/{entry.name}/SKILL.md: missing frontmatter")
        continue
    fm = m.group(1)
    name = re.search(r"^name:\s*(\S+)", fm, re.M)
    if not name or name.group(1) != entry.name:
        fail(f"skills/{entry.name}/SKILL.md: frontmatter name must equal folder name")
    if not re.search(r"^description:", fm, re.M):
        fail(f"skills/{entry.name}/SKILL.md: missing description")

for d in skills_dir.rglob("*"):
    if d.is_dir() and not any(d.iterdir()):
        fail(f"{d.relative_to(ROOT)}: empty directory")

# ---- Vendor-neutral wording -------------------------------------------------
# Format-required technical tokens are allowed; everything else is flagged.
ALLOWED = ["com.openai", ".claude-plugin", "ringex-claude-plugin"]
BANNED = re.compile(
    r"\b(claude|chatgpt|openai|codex|gpt[-\w]*|anthropic|gemini|copilot|llms?|cowork)\b",
    re.I,
)


def scan(label: str, text: str) -> None:
    for token in ALLOWED:
        text = text.replace(token, "")
    for lineno, line in enumerate(text.splitlines(), 1):
        hit = BANNED.search(line)
        if hit:
            fail(f"{label}:{lineno}: vendor/model name '{hit.group(0)}' in user-facing text")


scan("README.md", (ROOT / "README.md").read_text())
for skill_md in skills_dir.rglob("SKILL.md"):
    scan(str(skill_md.relative_to(ROOT)), skill_md.read_text())
if plugin:
    # Listing metadata only: description, keywords, and the interface block.
    listing = {
        "description": plugin.get("description"),
        "keywords": plugin.get("keywords"),
        "interface": plugin.get("extensions", {}).get("com.openai", {}).get("interface"),
    }
    scan("plugin.json(listing)", json.dumps(listing, indent=1))

if errors:
    print(f"{len(errors)} problem(s) found:", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print("repo checks passed")

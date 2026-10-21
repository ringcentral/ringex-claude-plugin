# Development Guide

Maintainer notes for building, testing, and publishing this plugin across plugin ecosystems. This file is not part of the distributed package.

## Writing rules

- Descriptions, skills, and listing copy must be AI-assistant-agnostic. Do not name specific models, assistants, or vendors. Use "AI assistant" or similar generic terms.
- Skills in `skills/` are shared by every client. Don't add client-specific tool names to them.
- Vendor names are acceptable only where a format requires them (for example the `com.openai` extension key or the `.claude-plugin/` directory).
- Keep `README.md` current. Any change to generated files, what contributors edit, or CI behavior must update the "How this repository is maintained" section in the same change.

## Clients and manifests

| Client | Manifest used | MCP config |
| --- | --- | --- |
| Claude | `.claude-plugin/plugin.json` (generated) | `mcp.json` (via `mcpServers`) |
| OpenAI (ChatGPT / Codex) | `plugin.json` (portable, with `extensions.com.openai`) | `mcp.json` |

- `plugin.json` is the single source of truth. Edit metadata and bump the version there only.
- `.claude-plugin/plugin.json` is generated. Never hand-edit it. Run `python3 scripts/sync_manifests.py` after changing `plugin.json`; `--check` fails if it is out of date.
- `mcp.json` is the only MCP config. It carries the OpenAI OAuth settings under `extensions["com.openai"]`.

## Marketplace

`.claude-plugin/marketplace.json` is generated (never hand-edit) and shared by both ecosystems; OpenAI reads it as a legacy-compatible location. It includes OpenAI-only fields (`interface`, `policy`) that Claude ignores, so `claude plugin validate .` reports two expected warnings.

- **Claude install:** `/plugin marketplace add <owner>/<repo>`, then `/plugin install ringcentral@ringcentral` (verified against a local folder copy).
- **OpenAI install:** `codex plugin marketplace add <owner>/<repo>` (not yet tested against this file).
- The `<owner>/<repo>` path changes when the repo is renamed.

## Testing

- **Claude:** `claude plugin validate .`, then `claude --plugin-dir <path-to-this-repo>` and authorize the `phone` and `team-chat` servers when prompted.
- **OpenAI:** upload the package ZIP through the OpenAI plugin submission portal, or add the plugin to a local or repo marketplace.

## Packaging for OpenAI

Build locally with `python3 scripts/build_package.py` (output in `dist/`). The ZIP has `plugin.json`, `mcp.json`, `skills/`, `assets/`, `LICENSE`, and `README.md` at its root; Claude-only files, this guide, and the tooling are excluded. The builds are deterministic. The `<!-- --8<-- [start:body] -->` / `[end:body]` markers in `SKILL.md` files are `pymdownx.snippets` section markers used by the docs site to include each skill's body (without the frontmatter). Keep them in the repo and don't change their names; the build strips them from the packaged copies.

The root-versus-wrapper-folder layout is unconfirmed against the submission portal. If the portal rejects the layout, change it in `scripts/build_package.py`.

Local check before pushing: `python3 scripts/sync_manifests.py --check && python3 scripts/check_repo.py && claude plugin validate .`

## Skill synchronization

Skills in this repository are synchronized with the documentation repository `ringcentral-mcp-docs`. When updating skills, update both repositories, keep versions and functionality in sync, and see `../ringcentral-mcp-docs/AGENTS.md` for the procedure.

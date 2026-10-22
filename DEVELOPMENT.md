# Development Guide

Maintainer notes for building, testing, and publishing this plugin across plugin ecosystems. This file is not part of the distributed package.

## Writing rules

- Descriptions, skills, and listing copy must be AI-assistant-agnostic. Do not name specific models, assistants, or vendors. Use "AI assistant" or similar generic terms.
- Skills in `skills/` are shared by every client. Don't add client-specific tool names to them.
- Vendor names are acceptable only where a format requires them (for example the `com.openai` extension key or the `.claude-plugin/` directory).
- Keep this file current. Any change to generated files, what contributors edit, or CI behavior must update the "Repository maintenance" section below in the same change. `README.md` stays user-facing and should not reference build scripts, manifests, or asset files.

## Repository maintenance

One set of source files produces the package for every supported plugin client. Some files are hand-edited, and some are generated.

### What you edit

| File | Purpose |
| --- | --- |
| `plugin-manifest.json` | Single source of truth for name, **version**, description, author, URLs, and listing metadata. Bump the version here only |
| `mcp-manifest.json` | MCP servers and their OAuth settings (portable format) |
| `skills/*/SKILL.md` | Skills. Keep them AI-assistant-agnostic: don't name specific models, assistants, or vendors |
| `assets/` | Plugin icon and other static assets |
| `DEVELOPMENT.md` | This file. Update it whenever the build, generated files, or CI behavior changes |
| `scripts/`, `.github/workflows/ci.yml` | Build, check, and CI tooling |

### What is generated (do not hand-edit)

| File | Generated from | How |
| --- | --- | --- |
| `.claude-plugin/plugin.json` | `plugin-manifest.json` | `python3 scripts/sync_manifests.py` |
| `.mcp.json` | `mcp-manifest.json` | `python3 scripts/sync_manifests.py` |
| `.claude-plugin/marketplace.json` | `plugin-manifest.json` | `python3 scripts/sync_manifests.py` |
| `.agents/plugins/marketplace.json` | `plugin-manifest.json` | `python3 scripts/sync_manifests.py` |

`.mcp.json` is the clean Claude MCP config (no `$schema`, no `extensions`; `streamable-http` is accepted by Claude as an alias for `http`). The OpenAI-portable root `plugin.json` and `mcp.json` are not kept in the repo, because the Anthropic submission checker flags them (`AGENT_PLUGINS_MANIFEST_DETECTED`); `scripts/build_package.py` generates them inside the package ZIP from `plugin-manifest.json` and `mcp-manifest.json`.

Each client has its own marketplace catalog listing this single plugin: `.claude-plugin/marketplace.json` for Claude (clean, so `claude plugin validate .` reports no warnings) and `.agents/plugins/marketplace.json` for Codex (adds the `interface` and `policy` fields). The Codex location is unverified and may change; edit `CODEX_MARKETPLACE_TARGET` in `scripts/sync_manifests.py` if so.

A tracked pre-commit hook (`.githooks/pre-commit`) runs `scripts/sync_manifests.py` and stages the generated files on every commit. Enable it once per clone with `bash scripts/install_hooks.sh` (sets `core.hooksPath` to `.githooks`). CI still runs `--check` as a backstop for clones without the hook.

After changing `plugin-manifest.json`, run the script (or just commit with the hook enabled) and commit the results. `python3 scripts/sync_manifests.py --check` exits non-zero if any generated file is stale.

### What CI produces automatically

The workflow in `.github/workflows/ci.yml` runs on every pull request, every push to `main`, and every `v*` tag:

1. **Generated files are current** — `scripts/sync_manifests.py --check` fails if a generated file is stale
2. **Repository content is valid** — `scripts/check_repo.py` checks JSON syntax, required manifest fields and listing limits, MCP server URLs (HTTPS, unversioned) and OAuth settings, skill frontmatter, empty folders, and that README, skill, and listing text don't name specific models, assistants, or vendors
3. **Plugin validation** — the client's own plugin validator runs against the repository
4. **Package build** — `scripts/build_package.py` produces `dist/<name>-<version>.zip` and uploads it as a build artifact. The ZIP contains `plugin.json`, `mcp.json` (both generated from the `*-manifest.json` sources), `LICENSE`, `README.md`, `assets/`, and `skills/` at its root; maintainer-only files are excluded, and the docs-sync markers (`<!-- --8<-- ... -->`) are stripped from the packaged skills (the files in the repo keep them)
5. **Release** — on a `v*` tag, the ZIP is attached to the GitHub release

To cut a release: bump `version` in `plugin-manifest.json`, run `python3 scripts/sync_manifests.py`, commit, and push a matching `vX.Y.Z` tag.

Run the same steps locally with the `scripts/` commands above. Generated artifacts and build output (`dist/`) are not committed.

The generated Claude manifest includes `privacyPolicyUrl` (sourced from `privacyPolicyURL` in `plugin-manifest.json`), because the plugin uses a remote MCP server and the submission checker requires it (`PRIVACY_URL_MISSING`). It intentionally omits `supportUrl`, `documentationUrl`, `termsOfServiceUrl`, and `icon`; the submission checker flags them as `UNKNOWN_KEY_CROSS_TOOL`. Provide those values in the directory submission form instead. If a listing ends up missing its icon or links, re-add the keys in `build()` in `scripts/sync_manifests.py`.

## Clients and manifests

| Client | Manifest used | MCP config |
| --- | --- | --- |
| Claude | `.claude-plugin/plugin.json` (generated) | `.mcp.json` (generated, via `mcpServers`) |
| OpenAI (ChatGPT / Codex) | `plugin.json` (portable; generated into the ZIP only) | `mcp.json` (portable; ZIP only) |

- `plugin-manifest.json` is the single source of truth (named to avoid colliding with any client's own `plugin.json`). Edit metadata and bump the version there only.
- `.claude-plugin/plugin.json` is generated. Never hand-edit it. Run `python3 scripts/sync_manifests.py` after changing `plugin-manifest.json`; `--check` fails if it is out of date.
- `mcp-manifest.json` is the only MCP source. It carries the OpenAI OAuth settings under `extensions["com.openai"]`.

## Marketplace

Both marketplace files are generated (never hand-edit). The Claude one contains no OpenAI-only fields, so validation is warning-free.

- **Claude install:** `/plugin marketplace add <owner>/<repo>`, then `/plugin install ringcentral@ringcentral` (verified against a local folder copy).
- **OpenAI install:** `codex plugin marketplace add <owner>/<repo>` (not yet tested against this file).
- The `<owner>/<repo>` path changes when the repo is renamed.

## Testing

- **Claude:** `claude plugin validate .`, then `claude --plugin-dir <path-to-this-repo>` and authorize the `phone` and `team-chat` servers when prompted.
- **OpenAI:** upload the package ZIP through the OpenAI plugin submission portal, or add the plugin to a local or repo marketplace.

## Packaging for OpenAI

Build locally with `python3 scripts/build_package.py` (output in `dist/`). The ZIP has `plugin.json`, `mcp.json` (generated from the `*-manifest.json` sources), `skills/`, `assets/`, `LICENSE`, and `README.md` at its root; Claude-only files, this guide, and the tooling are excluded. The builds are deterministic. The `<!-- --8<-- [start:body] -->` / `[end:body]` markers in `SKILL.md` files are `pymdownx.snippets` section markers used by the docs site to include each skill's body (without the frontmatter). Keep them in the repo and don't change their names; the build strips them from the packaged copies.

The root-versus-wrapper-folder layout is unconfirmed against the submission portal. If the portal rejects the layout, change it in `scripts/build_package.py`.

Local check before pushing: `python3 scripts/sync_manifests.py --check && python3 scripts/check_repo.py && claude plugin validate .`

## Skill synchronization

Skills in this repository are synchronized with the documentation repository `ringcentral-mcp-docs`. When updating skills, update both repositories, keep versions and functionality in sync, and see `../ringcentral-mcp-docs/AGENTS.md` for the procedure.

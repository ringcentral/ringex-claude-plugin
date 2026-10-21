# RingCentral Agent Plugin

A portable plugin that connects your AI assistant to RingCentral phone and Team Chat. It works with any AI assistant or plugin client that supports the Agent Plugins format.

## Contents

This repository contains one RingCentral plugin package: portable metadata, two remote MCP servers, and reusable skills.

### Plugin Configuration
- **`plugin.json`** — Portable Agent Plugins manifest
- **`mcp.json`** — MCP configuration for the two RingCentral remote servers (phone and team chat)
- **`assets/`** — Plugin icon

## How this repository is maintained

One set of source files produces the package for every supported plugin client. Some files are hand-edited, and some are generated.

### What you edit

| File | Purpose |
| --- | --- |
| `plugin.json` | Single source of truth for name, **version**, description, author, URLs, and listing metadata. Bump the version here only |
| `mcp.json` | MCP servers and their OAuth settings |
| `skills/*/SKILL.md` | Skills. Keep them AI-assistant-agnostic: don't name specific models, assistants, or vendors |
| `assets/icon.png` | Plugin icon |
| `README.md` | This file. Update it whenever the build, generated files, or CI behavior changes |
| `scripts/`, `.github/workflows/ci.yml` | Build, check, and CI tooling |

### What is generated (do not hand-edit)

| File | Generated from | How |
| --- | --- | --- |
| `.claude-plugin/plugin.json` | `plugin.json` | `python3 scripts/sync_manifests.py` |
| `.claude-plugin/marketplace.json` | `plugin.json` | `python3 scripts/sync_manifests.py` |

`marketplace.json` is the plugin catalog used to install from this repository. One file serves every supported client; it lists this single plugin.

After changing `plugin.json`, run the script and commit the results. `python3 scripts/sync_manifests.py --check` exits non-zero if any generated file is stale.

### What CI produces automatically

The workflow in `.github/workflows/ci.yml` runs on every pull request, every push to `main`, and every `v*` tag:

1. **Generated files are current** — `scripts/sync_manifests.py --check` fails if a generated file is stale
2. **Repository content is valid** — `scripts/check_repo.py` checks JSON syntax, required manifest fields and listing limits, MCP server URLs (HTTPS, unversioned) and OAuth settings, skill frontmatter, empty folders, and that README, skill, and listing text don't name specific models, assistants, or vendors
3. **Plugin validation** — the client's own plugin validator runs against the repository
4. **Package build** — `scripts/build_package.py` produces `dist/<name>-<version>.zip` and uploads it as a build artifact. The ZIP contains `plugin.json`, `mcp.json`, `LICENSE`, `README.md`, `assets/`, and `skills/` at its root; maintainer-only files are excluded, and the docs-sync markers (`<!-- --8<-- ... -->`) are stripped from the packaged skills (the files in the repo keep them)
5. **Release** — on a `v*` tag, the ZIP is attached to the GitHub release

To cut a release: bump `version` in `plugin.json`, run `python3 scripts/sync_manifests.py`, commit, and push a matching `vX.Y.Z` tag.

Run the same steps locally with the `scripts/` commands above. Generated artifacts and build output (`dist/`) are not committed.

Maintainers: see [`DEVELOPMENT.md`](DEVELOPMENT.md) for testing and publishing notes.

### Skills
The `skills/` directory contains 16 reusable skills that extend the plugin's capabilities:

**Communication Skills:**
- `call-followup-email` — Draft follow-up emails after calls
- `call-recap` — Summarize and recap call details
- `voicemail-inbox` — Access and manage voicemail messages
- `sms-inbox` — View SMS/text message threads
- `send-sms` — Send a confirmed person-to-person SMS
- `fax-inbox` — Access received faxes

**Team Chat (Glip) Skills:**
- `post-to-chat` — Post messages to Glip channels and DMs
- `read-team-chat` — Read and summarize team chat conversations
- `manage-teams` — Create and manage Glip teams
- `manage-tasks` — Create and manage Glip tasks
- `manage-notes` — Create and manage Glip notes
- `manage-events` — Create and manage Glip events
- `manage-webhooks` — Set up and manage Glip webhooks
- `manage-adaptive-cards` — Create and send Adaptive Cards

**Directory & Contacts:**
- `colleague-lookup` — Look up colleagues in the RingCentral directory
- `communications-brief` — Get a daily communications digest

## Features

- **Phone Management** — Check recent calls, voicemail transcripts, and call history
- **SMS/Messaging** — Read and send text messages
- **Team Chat** — Read, post, and manage messages in Glip channels and teams
- **Task Management** — Create, update, and track team tasks
- **Contact Directory** — Look up colleagues and directory information
- **Call Follow-ups** — Automatically draft follow-up emails after calls

## Usage

Install the plugin from your AI assistant's plugin directory or marketplace, or add it from this repository using your client's plugin install flow.

Both servers use OAuth, so you sign in with your RingCentral account the first time a tool is used.

## Privacy & Security

- **Privacy Policy:** https://ringcentral.com/privacy
- The plugin connects to RingCentral's official MCP servers at `mcp.labs.ringcentral.com`
- All communication with RingCentral APIs is authenticated and follows RingCentral's security standards

## License

MIT

## Author

Byrne Reese (byrne.reese@ringcentral.com)

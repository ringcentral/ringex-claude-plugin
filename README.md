# RingCentral Claude Plugin

A Claude plugin that enables seamless integration with RingCentral's communication platform, allowing users to manage calls, voicemail, SMS, and team chat directly from Claude.

## Contents

This repository contains the RingCentral Claude plugin with the following components:

### Plugin Configuration
- **`.mcp.json`** — MCP server configuration connecting to RingCentral's remote MCP servers for phone and team chat functionality
- **`.claude-plugin/plugin.json`** — Plugin manifest with metadata, permissions, and configuration

### Skills
The `skills/` directory contains 17 Claude skills that extend the plugin's capabilities:

**Communication Skills:**
- `call-followup-email` — Draft follow-up emails after calls
- `call-recap` — Summarize and recap call details
- `voicemail-inbox` — Access and manage voicemail messages
- `sms-inbox` — View SMS/text message threads
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

This plugin is designed to work with Claude's plugin system. Install it through the Claude plugin marketplace or developer portal.

## Privacy & Security

- **Privacy Policy:** https://ringcentral.com/privacy
- The plugin connects to RingCentral's official MCP servers at `mcp.labs.ringcentral.com`
- All communication with RingCentral APIs is authenticated and follows RingCentral's security standards

## Development Notes

**Skill Synchronization:** Skills in this plugin repository are synchronized with the documentation repository at `ringcentral-mcp-docs`. When updating skills:
- Update the skill in **both** repositories
- Keep version numbers and functionality in sync
- See `../ringcentral-mcp-docs/AGENTS.md` for detailed sync procedures

## License

MIT

## Author

Byrne Reese (byrne.reese@ringcentral.com)

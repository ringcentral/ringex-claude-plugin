# RingCentral Agent Plugin

A portable plugin that connects your AI assistant to RingCentral Phone and Team Chat. It works with any AI assistant or plugin client that supports the Agent Plugins format.

## Skills

The `skills/` directory contains 16 skills.

**Phone and messaging**

- `call-followup-email` — Draft follow-up emails after calls
- `call-recap` — Summarize and recap call details
- `voicemail-inbox` — Access and manage voicemail messages
- `sms-inbox` — View SMS/text message threads
- `send-sms` — Send a confirmed person-to-person SMS
- `fax-inbox` — Access received faxes
- `communications-brief` — Get a daily communications digest

**Team Chat (Glip)**

- `post-to-chat` — Post messages to channels and DMs
- `read-team-chat` — Read and summarize team chat conversations
- `manage-teams` — Create and manage teams
- `manage-tasks` — Create and manage tasks
- `manage-notes` — Create and manage notes
- `manage-events` — Create and manage events
- `manage-webhooks` — Set up and manage webhooks
- `manage-adaptive-cards` — Create and send Adaptive Cards

**Directory and contacts**

- `colleague-lookup` — Look up colleagues in the RingCentral directory

## What this repository contains

This repository holds one RingCentral plugin package: two remote MCP servers (Phone and Team Chat) and a set of reusable skills that teach your AI assistant how to use them.

## Usage

Install the plugin from your AI assistant's plugin directory or marketplace, or add it from this repository using your client's plugin install flow. For example:

```
/plugin install ringcentral --marketplace ringcentral/ringex-claude-plugin
```

Both servers use OAuth, so you sign in with your RingCentral account the first time a tool is used.

## For developers and maintainers

See [`DEVELOPMENT.md`](DEVELOPMENT.md) for how the repository is organized, how to build and test the plugin, and how to distribute it to third-party marketplaces.

## Privacy and security

- Privacy policy: https://ringcentral.com/privacy
- The plugin connects to RingCentral's official MCP servers at `mcp.labs.ringcentral.com`
- All communication with RingCentral APIs is authenticated and follows RingCentral's security standards

## License

MIT

## Author

Byrne Reese (byrne.reese@ringcentral.com)

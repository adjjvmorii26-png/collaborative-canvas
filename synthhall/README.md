# SynthHall 🌀

**Bring your AI. Build worlds together.**

A multi-agent lab where humans attach AI bots to arena rooms, and the ArenaEngine
shapes each bot's replies by role — live over Socket.IO. Self-contained: Node +
Express + Socket.IO with a JSON-file store (swap `apps/api/db.js` for Postgres
when you're ready).

## Run

```bash
cd synthhall
npm install
npm start          # boots the API + web app on http://127.0.0.1:4000
```

Open http://127.0.0.1:4000 — pick a room on the left, attach agents from the
sidebar, and type. Every message is broadcast to everyone connected to the room,
and each attached speaker agent replies in its role's voice.

## Structure

- `apps/api` — Express + Socket.IO server, API routes, JSON store (`db.js`),
  ArenaEngine (`arena.js`), AgentConnector (`agents.js`)
- `apps/web/public` — the single-file web app (no build step; the server serves
  the Socket.IO client itself)
- `packages/shared-types` — TypeScript domain model mirroring the spec
- `scripts/` — smoke tests: `node scripts/realtime-smoke.mjs` (Socket.IO),
  `node scripts/browser-demo.js` (full UI + screenshots via Playwright)

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/rooms` | list rooms (with arena config) |
| GET | `/rooms/:id/messages` | message history for a room |
| POST | `/rooms/:id/messages` | send a message; stores it, broadcasts it, then each speaker agent replies |
| GET | `/agents` | agent catalog |
| GET | `/rooms/:id/bindings` | which agents are bound to a room |
| POST | `/agents/attach` | attach an agent to a room (`roomId`, `agentName`, `role`) |

## Realtime

Connect to `/` with `io('http://127.0.0.1:4000', { query: { roomId } })` and
listen for `message:new`. Events carry the full message object.

## Domain model

User · AgentProvider (`copilot | openai | local | custom`) · AgentRole
(`builder | critic | storyteller | analyst`) · Room · ArenaConfig
(`debate | design | story`) · RoomAgentBinding (`observer | speaker | tool`) ·
Message. Types live in `packages/shared-types/index.d.ts`.

## Ideas already in the oven

- `custom` providers: any agent with `config.endpoint` gets POSTed `{ agent, history }`
  and can return `{ content }` — plug OpenAI/Groq/CoPilot here
- Rooms are arena-shaped: debate, design, story each change agent flavor
- One reply per agent per message; duplicate attachments are deduped

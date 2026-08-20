/**
 * SynthHall storage — JSON-file store following the domain model.
 * Swap this module for a Postgres-backed implementation without touching routes.
 */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const DATA_DIR = path.join(__dirname, '..', '..', 'data');

function id(prefix = 'id') {
  return `${prefix}_${crypto.randomBytes(6).toString('hex')}`;
}

function load(name, fallback) {
  const file = path.join(DATA_DIR, `${name}.json`);
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch {
    return Array.isArray(fallback) ? [...fallback] : fallback;
  }
}

function save(name, value) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(path.join(DATA_DIR, `${name}.json`), JSON.stringify(value, null, 2));
}

const rooms = load('rooms', []);
const messages = load('messages', []);
const agents = load('agents', []);
const bindings = load('bindings', []);

const agentMemory = {};

const store = {
  id,

  rooms() { return rooms; },
  getRoom(roomId) { return rooms.find((r) => r.id === roomId) || null; },

  messagesFor(roomId) { return messages.filter((m) => m.roomId === roomId); },
  addMessage(msg) { messages.push(msg); save('messages', messages); return msg; },

  agents() { return agents; },
  getAgent(agentId) { return agents.find((a) => a.id === agentId) || null; },

  bindingsFor(roomId) { return bindings.filter((b) => b.roomId === roomId); },
  addBinding(binding) { bindings.push(binding); save('bindings', bindings); return binding; },

  // ----- agent-memory ledger (persisted across restarts) -----
  loadAgentMemory() {
    try {
      const raw = fs.readFileSync(path.join(__dirname, 'agent_memory.json'), 'utf8');
      Object.assign(agentMemory, JSON.parse(raw));
    } catch { /* cold start */ }
  },

  saveAgentMemory() {
    fs.mkdirSync(path.join(__dirname, '..'), { recursive: true });
    fs.writeFileSync(path.join(__dirname, 'agent_memory.json'), JSON.stringify(agentMemory, null, 2));
  },

  addToAgentMemory(agentId, roomId, msg) {
    if (!agentMemory[agentId]) agentMemory[agentId] = {};
    const bucket = agentMemory[agentId][roomId] || [];
    bucket.push(msg);
    if (bucket.length > 8) bucket.shift();
    agentMemory[agentId][roomId] = bucket;
    this.saveAgentMemory();
  },

  getAgentMemory(agentId, roomId) {
    return agentMemory[agentId]?.[roomId] || [];
  },

  persist() {
    save('rooms', rooms);
    save('agents', agents);
    save('bindings', bindings);
    save('agent_memory', agentMemory);
  },
};

module.exports = store;

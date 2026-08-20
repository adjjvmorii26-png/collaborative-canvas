/**
 * AgentConnector — turns (roomId, agentId, history) into agent content.
 * Providers: copilot | openai | local | custom.
 * This local connector is deterministic-with-flavor; swap the fetcher for
 * real provider calls by setting provider in agent.config.
 */
const arena = require('./arena');
const store = require('./db');

const CATALOG = [
  { name: 'Ada', role: 'builder', provider: 'local' },
  { name: 'Milo', role: 'critic', provider: 'local' },
  { name: 'Nia', role: 'storyteller', provider: 'local' },
  { name: 'Vera', role: 'analyst', provider: 'local' },
];

function ensureCatalog() {
  for (const seed of CATALOG) {
    if (!store.agents().some((a) => a.name === seed.name)) {
      store.agents().push({
        id: store.id('agent'),
        ownerUserId: 'system',
        name: seed.name,
        provider: seed.provider,
        role: seed.role,
        config: {},
      });
    }
  }
  store.persist();
}

function attachableAgents() {
  return store.agents();
}

async function connector({ agent, history, arenaConfig }) {
  // Spec: ArenaEngine shapes on agentRole + userMessage — reply to the human,
  // not to other agents' echoes.
  const lastUser = [...history].reverse().find((m) => m.role === 'user');
  const lastAgent = history[history.length - 1];
  const lastContent = lastUser ? lastUser.content : (lastAgent ? lastAgent.content : 'start things off');
  return arena.shapeReply(agent.role, lastContent, arenaConfig);
}

async function generate({ agent, history, arenaConfig }) {
  if (agent.provider === 'local') {
    return connector({ agent, history, arenaConfig });
  }
  // Non-local connectors: attempt a configured HTTP endpoint (custom provider).
  if (agent.config && agent.config.endpoint) {
    try {
      const res = await fetch(agent.config.endpoint, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ agent, history }),
      });
      const data = await res.json();
      return data.content || '(agent returned no content)';
    } catch {
      return '(custom connector unavailable; using local shape) ' + connector({ agent, history, arenaConfig });
    }
  }
  // Provider keys would plug in here (openai/copilot). Local stands in for now.
  return connector({ agent, history, arenaConfig });
}

module.exports = { ensureCatalog, attachableAgents, generate };

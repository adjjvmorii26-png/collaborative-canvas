/**
 * ArenaEngine — shapes an agent reply based on the agent's role
 * and the arena type (debate, design, story).
 */
const ROLE_PERSONAS = {
  builder: {
    open: '⚒️ Builder sees',
    lean: 'focus on what can actually be built next:',
    spinner: [
      'breaking it into implementable steps',
      'flagging leverage points worth building on',
      'proposing the smallest concrete next action',
    ],
  },
  critic: {
    open: '🔍 Critic challenges',
    lean: 'the weak points being:',
    spinner: [
      'stress-testing the assumptions',
      'checking for hidden costs and failure modes',
      'asking what breaks when this scales',
    ],
  },
  storyteller: {
    open: '📖 Storyteller turns this into',
    lean: 'the narrative being:',
    spinner: [
      'finding the characters and stakes',
      'framing it as a scene with momentum',
      'noticing the twist hiding underneath',
    ],
  },
  analyst: {
    open: '📊 Analyst measures',
    lean: 'what matters to track being:',
    spinner: [
      'isolating the variables worth measuring',
      'identifying leading indicators',
      'noting the ratios that would prove or disprove this',
    ],
  },
};

function arenaFront(arenaType) {
  const map = {
    debate: 'For the debate,',
    design: 'In this design arena,',
    story: 'In this story world,',
  };
  return map[arenaType] || 'Here,';
}

function pick(arr, fallback) {
  if (!arr || arr.length === 0) return fallback;
  return arr[Math.floor(Math.random() * arr.length)];
}

function shapeReply(role, userMessage, arena) {
  const persona = ROLE_PERSONAS[role] || ROLE_PERSONAS.analyst;
  const arenaType = (arena && arena.type) || 'debate';
  const topic = (arena && arena.topic) || 'the shared topic';
  const flavor = pick(persona.spinner, 'offering a fresh angle');

  return [
    `${ROLE_PERSONAS[role].open || persona.open} “${String(userMessage).slice(0, 200)}” and ${flavor}.`,
    `${arenaFront(arenaType)} the room is exploring ${topic}, so ${persona.lean}`,
    `${pick([
      'consider the tradeoffs before moving on',
      'keep responses tight and concrete',
      'build on the best idea so far',
      'keep the energy moving',
    ], 'keep it sharp')}.`,
  ].join(' ');
}

function arenaRule(arena) {
  if (!arena || !arena.rules || arena.rules.length === 0) return 'no extra rules';
  return arena.rules.slice(0, 3).join(' · ');
}

module.exports = { shapeReply, arenaRule };

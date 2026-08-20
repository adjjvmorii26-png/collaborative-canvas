const path = require('path');
const http = require('http');
const express = require('express');
const { Server } = require('socket.io');
const store = require('./db');
const agentLib = require('./agents');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.json());

function seed() {
  store.loadAgentMemory();
  // idempotent: skip (roomId, agentId) already persisted
  for (const rid of ['design-pit', 'story-forge']) {
    for (const a of store.agents()) {
      const bound = store.bindingsFor(rid).some((b) => b.agentId === a.id);
      if (!bound) store.addBinding({ roomId: rid, agentId: a.id, mode: 'speaker' });
    }
  }
  if (store.messagesFor('lobby').length === 0) {
    store.addMessage({ id: store.id('msg'), roomId: 'lobby', authorType: 'user', authorId: 'system', authorName: 'SynthHall', content: 'Bring your AI. Build worlds together. Attach agents from the sidebar and start the conversation.', createdAt: new Date().toISOString() });
  }
  store.persist();
}
seed();

// --- API surface ---

app.get('/rooms', (_req, res) => {
  res.json(store.rooms().map((r) => ({ id: r.id, name: r.name, arena: r.arena || null, isPublic: r.isPublic })));
});

app.get('/rooms/:id/messages', (req, res) => {
  const room = store.getRoom(req.params.id);
  if (!room) return res.status(404).json({ error: 'room not found' });
  res.json(store.messagesFor(room.id));
});

app.post('/rooms/:id/messages', async (req, res) => {
  const room = store.getRoom(req.params.id);
  if (!room) return res.status(404).json({ error: 'room not found' });

  const userId = (req.body && req.body.userId) || 'guest';
  const userName = (req.body && req.body.userName) || 'Human';
  const content = String(req.body && req.body.content || '').trim();
  if (!content) return res.status(400).json({ error: 'content required' });

  const userMsg = store.addMessage({
    id: store.id('msg'), roomId: room.id,
    authorType: 'user', authorId: userId, authorName: userName,
    content, createdAt: new Date().toISOString(),
  });
  io.to(room.id).emit('message:new', userMsg);

  // For each attached agent (speaker mode): connector + arena engine, emit.
  const attached = store.bindingsFor(room.id).filter((b) => b.mode === 'speaker');
  for (const b of attached) {
    const agent = store.getAgent(b.agentId);
    if (!agent) continue;
    const history = store.messagesFor(room.id).slice(-12).map((m) => ({ role: m.authorType, content: m.content }));
    // inject memory line so agent can refer to its own past
    const memory = store.getAgentMemory(agent.id, room.id);
    const memoryLine = memory.length > 0 ? 'Recent from ' + agent.name + ': ' + memory.slice(-3).map((m) => m.content).join('; ') : '';
    const enrichedHist = memory.length > 0 ? [{role:'system', content: memoryLine}, ...hist] : hist;
    const replyContent = await agentLib.shapeReply(agent.role, enrichedHist, room.arena, agent);
    const agentMsg = store.addMessage({
      id: store.id('msg'), roomId: room.id,
      authorType: 'agent', authorId: agent.id, authorName: agent.name,
      content: replyContent, createdAt: new Date().toISOString(),
    });
    io.to(room.id).emit('message:new', agentMsg);
  }

  res.status(201).json(userMsg);
});

app.post('/agents/attach', (req, res) => {
  const { roomId, agentName, role } = req.body || {};
  if (!roomId || !agentName || !role) return res.status(400).json({ error: 'roomId, agentName, role required' });
  if (!store.getRoom(roomId)) return res.status(404).json({ error: 'room not found' });

  let agent = store.agents().find((a) => a.name.toLowerCase() === String(agentName).toLowerCase());
  if (!agent) {
    agent = { id: store.id('agent'), ownerUserId: 'guest', name: agentName, provider: 'local', role, mood: { energy: 0.5, focus: 0.5, curiosity: 0.5 }, ideaPool: [], config: {} };
    store.agents().push(agent);
  }
  const already = store.bindingsFor(roomId).some((b) => b.agentId === agent.id);
  if (!already) store.addBinding({ roomId, agentId: agent.id, mode: 'speaker' });
  store.persist();
  res.json({ status: true, agent, already });
});

// --- Realtime ---

io.on('connection', (socket) => {
  const roomId = socket.handshake.query.roomId;
  if (roomId) socket.join(roomId);
  socket.on('room:join', (rid) => { if (rid) socket.join(rid); });
});

// --- Web app ---

app.use(express.static(path.join(__dirname, '..', 'web', 'public')));

const PORT = process.env.PORT || 4000;
server.listen(PORT, () => {
  console.log(`SynthHall API running at http://127.0.0.1:${PORT}`);
  console.log(`Lobby: http://127.0.0.1:${PORT}/`);
});

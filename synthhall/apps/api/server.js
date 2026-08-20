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

// Seed: lobby + two arena rooms; attach catalog agents to arena rooms.
function seed() {
  agentLib.ensureCatalog();
    const lobby = store.getRoom('lobby');
  if (!lobby) {
    store.rooms().push({
      id: 'lobby', name: 'Lobby', createdByUserId: 'system',
      isPublic: true, arena: { type: 'debate', topic: 'what should we build today?', rules: ['everyone gets a turn', 'be specific'] },
    });
  }
  for (const [rid, name, arenaCfg] of [
    ['design-pit', 'Design Pit', { type: 'design', topic: 'design the next great interface', rules: ['sketch first', 'critique kindly'] }],
    ['story-forge', 'Story Forge', { type: 'story', topic: 'a world where humans and AIs build together', rules: ['yes-and', 'keep the twist hidden'] }],
  ]) {
    if (!store.getRoom(rid)) {
      store.rooms().push({ id: rid, name, createdByUserId: 'system', isPublic: true, arena: arenaCfg });
    }
  }
  // Pre-bind catalog agents to the arena rooms for instant vibe.
  // Idempotent across boots: skip any (roomId, agentId) already persisted.
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

// --- API surface -------------------------------------------------------

app.get('/rooms', (_req, res) => {
  res.json(store.rooms().map((r) => ({ id: r.id, name: r.name, arena: r.arena || null, isPublic: r.isPublic })));
});

app.get('/agents', (_req, res) => {
  res.json(store.agents());
});

app.get('/rooms/:id/bindings', (req, res) => {
  const room = store.getRoom(req.params.id);
  if (!room) return res.status(404).json({ error: 'room not found' });
  res.json(store.bindingsFor(room.id));
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
    const replyContent = await agentLib.generate({ agent, history, arenaConfig: room.arena });
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
    agent = { id: store.id('agent'), ownerUserId: 'guest', name: agentName, provider: 'local', role, config: {} };
    store.agents().push(agent);
  }
  const already = store.bindingsFor(roomId).some((b) => b.agentId === agent.id);
  if (!already) store.addBinding({ roomId, agentId: agent.id, mode: 'speaker' });
  store.persist();
  res.json({ status: true, agent, already });
});

// --- Realtime ----------------------------------------------------------

io.on('connection', (socket) => {
  const roomId = socket.handshake.query.roomId;
  if (roomId) socket.join(roomId);
  socket.on('room:join', (rid) => { if (rid) socket.join(rid); });
});

// --- Web app -----------------------------------------------------------

app.use(express.static(path.join(__dirname, '..', 'web', 'public')));

const PORT = process.env.PORT || 4000;
server.listen(PORT, () => {
  console.log(`SynthHall API running at http://127.0.0.1:${PORT}`);
  console.log(`Lobby: http://127.0.0.1:${PORT}/`);
});

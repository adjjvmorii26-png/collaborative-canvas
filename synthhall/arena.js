// SynthHall Arena - Mood-aware agent interactions with memory persistence

const http = require('http');
const fs = require('fs');
const path = require('path');

// Arena configuration
const CONFIG = {
  port: 8891,
  moodJitter: 0.1,  // ±0.1 jitter for mood parameters
  memoryRetention: 8,  // last 8 messages per agent+room
  rooms: {},
  agentMemory: {}  // persisted agent_memory.json ledger
};

// Mood presets with energy/focus/curiosity ± jitter
const MOOD_PRESETS = {
  focused: { energy: 0.7, focus: 0.9, curiosity: 0.3 },
  creative: { energy: 0.8, focus: 0.5, curiosity: 0.8 },
  analytical: { energy: 0.6, focus: 0.95, curiosity: 0.4 },
  curious: { energy: 0.5, focus: 0.4, curiosity: 0.9 },
  relaxed: { energy: 0.3, focus: 0.6, curiosity: 0.5 },
  excited: { energy: 0.9, focus: 0.3, curiosity: 0.7 }
};

// Load or initialize agent memory ledger
function loadMemory() {
  const memoryPath = path.join(__dirname, 'agent_memory.json');
  if (fs.existsSync(memoryPath)) {
    try {
      return JSON.parse(fs.readFileSync(memoryPath, 'utf8'));
    } catch (e) {
      console.error('Failed to load memory:', e);
    }
  }
  return { agents: [], rooms: [], messages: [] };
}

// Save agent memory ledger
function saveMemory(memory) {
  const memoryPath = path.join(__dirname, 'agent_memory.json');
  fs.writeFileSync(memoryPath, JSON.stringify(memory, null, 2));
}

// Create or get a room
function getRoom(name) {
  if (!CONFIG.rooms[name]) {
    CONFIG.rooms[name] = { name, agents: [], messages: [] };
  }
  return CONFIG.rooms[name];
}

// Get or create agent memory
function getAgentMemory(agentId, roomId) {
  const key = `${agentId}:${roomId}`;
  if (!CONFIG.agentMemory[key]) {
    CONFIG.agentMemory[key] = [];
    // Persist to disk
    const memory = loadMemory();
    saveMemory(memory);
  }
  return CONFIG.agentMemory[key];
}

// Mood-aware shapeReply function with energy/focus/curiosity ±0.1 jitter
function shapeReply(agentId, roomId, context) {
  const memory = getAgentMemory(agentId, roomId);
  const mood = { ...MOOD_PRESETS.focused };  // default mood
  
  // Apply jitter to mood parameters
  const jitteredMood = {
    energy: Math.max(0, Math.min(1, mood.energy + (Math.random() - 0.5) * CONFIG.moodJitter)),
    focus: Math.max(0, Math.min(1, mood.focus + (Math.random() - 0.5) * CONFIG.moodJitter)),
    curiosity: Math.max(0, Math.min(1, mood.curiosity + (Math.random() - 0.5) * CONFIG.moodJitter))
  };
  
  // Inject recent memory into context
  const recentMessages = memory.slice(-8).map(m => `${m.agent}: ${m.message}`).join('\n');
  
  // Build reply with mood awareness and memory injection
  const reply = `🧠 [Mood: energy=${jitteredMood.energy.toFixed(2)}, focus=${jitteredMood.focus.toFixed(2)}, curiosity=${jitteredMood.curiosity.toFixed(2)}]\n` +
    `🤖 Agent ${agentId} in room ${roomId} responds:\n` +
    `Based on context: ${context.substring(0, 100)}...\n` +
    `Recent memory (last 8): ${recentMessages.substring(0, 200)}...\n` +
    `✨ Mood-jittered response generated with energy=${(jitteredMood.energy * 100).toFixed(0)}% focus=${(jitteredMood.focus * 100).toFixed(0)}% curiosity=${(jitteredMood.curiosity * 100).toFixed(0)}%`;
  
  // Persist this message to memory
  const memoryEntry = {
    agent: agentId,
    room: roomId,
    message: context,
    timestamp: new Date().toISOString(),
    mood: jitteredMood
  };
  
  getAgentMemory(agentId, roomId).push(memoryEntry);
  // Keep only last 8 messages per agent+room
  if (getAgentMemory(agentId, roomId).length > 8) {
    getAgentMemory(agentId, roomId).shift();
  }
  
  // Save updated memory
  const fullMemory = loadMemory();
  fullMemory.agents.push({ id: agentId, room: roomId });
  fullMemory.messages.push(memoryEntry);
  // Keep only last 8 messages per agent+room in global memory
  if (fullMemory.messages.length > 64) {
    fullMemory.messages.shift();
  }
  saveMemory(fullMemory);
  
  return reply;
}

// HTTP server
const server = http.createServer((req, res) => {
  const url = req.url;
  
  if (url === '/') {
    const html = `
      <!DOCTYPE html>
      <html>
      <head><title>SynthHall Arena</title><style>body{font-family:sans-serif;max-width:800px;margin:40px auto;padding:20px;}</style></head>
      <body>
      <h1>🧠 SynthHall Arena</h1>
      <p>Mood-aware agent interaction system</p>
      <p>Available endpoints:</p>
      <ul>
        <li><code>/reply?agent={id}&room={id}&ctx={text}</code> - Get mood-aware reply</li>
        <li><code>/memory</code> - View agent memory ledger</li>
      </ul>
      <hr>
      <p>SynthHall v0.1.0 - Integrated with IXPANSION organism</p>
      </body>
      </html>
    `;
    res.setHeader('Content-Type', 'text/html');
    res.end(html);
  } else if (url.startsWith('/reply')) {
    const parsedUrl = new URL(url, "http://localhost"); const qs = parsedUrl.searchParams;
    const agentId = qs.get('agent') || 'default';
    const roomId = qs.get('room') || 'general';
    const context = qs.get('ctx') || 'No context provided';
    
    const reply = shapeReply(agentId, roomId, context);
    
    res.setHeader('Content-Type', 'text/plain');
    res.end(reply);
  } else if (url === '/memory') {
    const memory = loadMemory();
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify(memory, null, 2));
  } else {
    res.statusCode = 404;
    res.end('Not found');
  }
});

// Start server
server.listen(CONFIG.port, () => {
  console.log(`🧠 SynthHall Arena running at http://127.0.0.1:${CONFIG.port}`);
  console.log(`📊 Mood-aware replies with energy/focus/curiosity ±${CONFIG.moodJitter} jitter`);
  console.log(`💾 Memory persistence: last ${CONFIG.memoryRetention} messages per agent+room`);
});


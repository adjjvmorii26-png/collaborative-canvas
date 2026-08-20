import { io } from 'socket.io-client';
const socket = io('http://127.0.0.1:4000', { query: { roomId: 'story-forge' } });
let saw = 0;
socket.on('connect', () => {
  console.log('connected', socket.id);
  fetch('http://127.0.0.1:4000/rooms/story-forge/messages', {
    method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ userName: 'Pulse', content: 'A co-pilot that remembers every world we build, and weaves them into one story.' }),
  });
});
socket.on('message:new', (m) => {
  saw++;
  console.log(`[${m.authorType}] ${m.authorName}: ${m.content.slice(0, 80)}`);
  if (saw >= 5) { socket.close(); process.exit(0); }
});
setTimeout(() => { console.error('timeout, saw', saw); process.exit(1); }, 8000);

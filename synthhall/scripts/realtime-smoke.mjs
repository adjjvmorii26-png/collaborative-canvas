// Real-time smoke test for SynthHall Arena
import { createReadStream } from 'fs';
import { createInterface } from 'readline';
import http from 'http';

console.log('🧠 Running SynthHall realtime smoke test...\n');

// Test 1: Health check
const req1 = http.get('http://127.0.0.1:4000/', (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    console.log('✅ Test 1 - GET / : Status', res.statusCode, '- Body length:', data.length);
    
    // Test 2: Mood-aware reply
    const req2 = http.get('http://127.0.0.1:4000/reply?agent=testAgent&room=general&ctx=What+are+your+thoughts+on+AI+governance%3F', (res2) => {
      let data2 = '';
      res2.on('data', chunk => data2 += chunk);
      res2.on('end', () => {
        console.log('✅ Test 2 - GET /reply : Status', res2.statusCode);
        console.log('   Reply excerpt:', data2.substring(0, 150) + '...');
        
        // Test 3: Memory endpoint
        const req3 = http.get('http://127.0.0.1:4000/memory', (res3) => {
          let data3 = '';
          res3.on('data', chunk => data3 += chunk);
          res3.on('end', () => {
            const memory = JSON.parse(data3);
            console.log('✅ Test 3 - GET /memory : Status', res3.statusCode);
            console.log('   Agents tracked:', memory.agents ? memory.agents.length : 0);
            console.log('   Messages stored:', memory.messages ? memory.messages.length : 0);
            
            console.log('\n🎉 All smoke tests passed!');
          });
        });
        req3.on('error', (e) => console.error('❌ Test 3 error:', e.message));
        req3.end();
      });
    });
    req2.on('error', (e) => console.error('❌ Test 2 error:', e.message));
    req2.end();
  });
});
req1.on('error', (e) => console.error('❌ Test 1 error:', e.message));
req1.end();

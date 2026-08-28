import 'dotenv/config';
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import Anthropic from '@anthropic-ai/sdk';
import { buildMetaPrompt, comparePrompts, scorePrompt } from './optimizer.js';

const root = fileURLToPath(new URL('.', import.meta.url));
const port = Number(process.env.PORT || 3000);
const contentTypes = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' };

async function askClaude(system, prompt) {
  if (!process.env.ANTHROPIC_API_KEY) throw new Error('Set ANTHROPIC_API_KEY in .env to call Claude.');
  const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
  const response = await client.messages.create({
    model: process.env.CLAUDE_MODEL || 'claude-3-5-haiku-latest', max_tokens: 900, system,
    messages: [{ role: 'user', content: prompt }],
  });
  return response.content.filter(block => block.type === 'text').map(block => block.text).join('');
}

async function handleApi(path, body) {
  if (path === '/api/optimize') {
    const engineered = await askClaude('You are a meticulous prompt engineer.', buildMetaPrompt(body.rawPrompt, body));
    return { engineered, scores: comparePrompts(body.rawPrompt, engineered) };
  }
  if (path === '/api/evaluate') {
    const [baselineOutput, engineeredOutput] = await Promise.all([
      askClaude('Answer the user request directly.', body.rawPrompt),
      askClaude('Follow the engineered instruction exactly.', body.engineeredPrompt),
    ]);
    return { baselineOutput, engineeredOutput, scores: comparePrompts(body.rawPrompt, body.engineeredPrompt, baselineOutput, engineeredOutput) };
  }
  if (path === '/api/score') return { scores: scorePrompt(body.prompt, body.output || '') };
  throw new Error('Unknown endpoint.');
}

const server = createServer(async (request, response) => {
  try {
    if (request.url.startsWith('/api/')) {
      const chunks = []; for await (const chunk of request) chunks.push(chunk);
      const result = await handleApi(request.url, JSON.parse(Buffer.concat(chunks)));
      response.writeHead(200, { 'Content-Type': 'application/json' }); response.end(JSON.stringify(result)); return;
    }
    const requested = request.url === '/' ? '/index.html' : request.url;
    const file = await readFile(join(root, 'public', requested));
    response.writeHead(200, { 'Content-Type': contentTypes[extname(requested)] || 'text/plain' }); response.end(file);
  } catch (error) {
    response.writeHead(error.message.startsWith('Set ') ? 503 : 400, { 'Content-Type': 'application/json' });
    response.end(JSON.stringify({ error: error.message }));
  }
});
server.listen(port, () => console.log(`Prompt Optimizer running at http://localhost:${port}`));

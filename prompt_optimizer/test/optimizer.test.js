import test from 'node:test';
import assert from 'node:assert/strict';
import { buildMetaPrompt, comparePrompts, scorePrompt } from '../optimizer.js';

test('meta-prompt preserves raw intent and requests engineering dimensions', () => {
  const prompt = buildMetaPrompt('Summarize this report', { expected: 'A five-bullet executive summary' });
  assert.match(prompt, /Summarize this report/);
  assert.match(prompt, /role framing/i);
  assert.match(prompt, /five-bullet executive summary/);
});

test('structured prompts score higher than vague prompts', () => {
  const baseline = scorePrompt('Make a good launch plan.');
  const engineered = scorePrompt('You are a launch strategist. Create a launch plan for the product. Return a table with owners and dates. Do not invent data.');
  assert.ok(engineered.overall > baseline.overall);
  assert.equal(engineered.dimensions['Role framing'], 1);
  assert.equal(engineered.dimensions['Output format'], 1);
});

test('comparison returns both baseline and engineered scores', () => {
  const result = comparePrompts('Write a post.', 'You are an editor. Return five bullet points.', 'short', '1. one\n2. two');
  assert.ok(result.baseline && result.engineered);
  assert.ok(Number.isInteger(result.engineered.overall));
});

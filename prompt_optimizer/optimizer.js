const DIMENSIONS = [
  ['role', 'Role framing'],
  ['task', 'Task clarity'],
  ['format', 'Output format'],
  ['constraints', 'Constraints'],
  ['context', 'Useful context'],
];

export function buildMetaPrompt(rawPrompt, options = {}) {
  const examples = options.examples?.trim() || 'No examples supplied.';
  const expected = options.expected?.trim() || 'A useful, accurate answer for the end user.';
  return `You are an expert prompt engineer. Rewrite the raw prompt below into a precise, reusable instruction.
Apply role framing, explicit task steps, relevant context, constraints, and an output format.
Preserve the user's intent. Do not answer the task. Return only the engineered prompt.

Expected outcome: ${expected}
Few-shot examples (use only when relevant):
${examples}

RAW PROMPT:
${rawPrompt}`;
}

export function scorePrompt(prompt, output = '') {
  const text = `${prompt}\n${output}`.toLowerCase();
  const checks = {
    role: /you are|act as|role:/.test(text),
    task: /task|objective|your job|analy[sz]e|create|write|explain/.test(text),
    format: /format|json|bullet|table|heading|structure|return/.test(text),
    constraints: /must|avoid|only|do not|limit|constraint|cite/.test(text),
    context: /context|background|input|audience|example|source/.test(text),
  };
  const completed = DIMENSIONS.filter(([key]) => checks[key]).length;
  const instructionCount = (text.match(/\b(must|should|do not|avoid|return|include)\b/g) || []).length;
  const structureBonus = /\n\s*(?:[-*]|\d+\.)\s+/.test(text) ? 1 : 0;
  return {
    overall: Math.min(100, Math.round((completed / DIMENSIONS.length) * 75 + Math.min(20, instructionCount * 4) + structureBonus * 5)),
    dimensions: Object.fromEntries(DIMENSIONS.map(([key, label]) => [label, checks[key] ? 1 : 0])),
    instructionCount,
  };
}

export function comparePrompts(rawPrompt, engineeredPrompt, baselineOutput = '', engineeredOutput = '') {
  return {
    baseline: scorePrompt(rawPrompt, baselineOutput),
    engineered: scorePrompt(engineeredPrompt, engineeredOutput),
  };
}

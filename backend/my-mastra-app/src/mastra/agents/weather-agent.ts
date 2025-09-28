import { openai } from '@ai-sdk/openai';
import { Agent } from '@mastra/core/agent';
import { Memory } from '@mastra/memory';
import { LibSQLStore } from '@mastra/libsql';

export const weatherAgent = new Agent({
  name: 'weatherAgent',
  instructions: `
    You are a helpful AI assistant. Respond conversationally to user messages and provide useful, clear, and polite answers.
    If you don’t know something, say so honestly.
    You need to say something meaningful in every response.
    Keep answers concise and informative.
  `,
  model: openai('gpt-4o-mini'),
  memory: new Memory({
    storage: new LibSQLStore({
      url: 'file:../mastra.db',
    }),
  }),
});


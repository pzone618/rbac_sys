import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createBrowserTts, splitText } from '../skills/website-tts/assets/browser-tts.mjs';

test('chunks retain multilingual content and Unicode characters', () => {
  const text = '你好。Hello!😀😀😀';
  const chunks = splitText(text, 2);
  assert.equal(chunks.join(''), text);
  assert.ok(chunks.every(s => Array.from(s).length <= 2));
});

test('SSR gives an actionable unsupported error', () => {
  assert.throws(() => createBrowserTts(), /unavailable/);
});

test('local-only selection blocks remote voice; stop settles cancelled reading', async () => {
  let utterance;
  const local = { voiceURI: 'local', name: 'Local', lang: 'zh-CN', localService: true };
  globalThis.window = {
    speechSynthesis: {
      getVoices: () => [local, { voiceURI: 'remote', lang: 'zh-CN', localService: false }],
      cancel() {}, pause() {}, resume() {},
      speak(value) { utterance = value; }
    },
    SpeechSynthesisUtterance: class { constructor(text) { this.text = text; } }
  };
  try {
    const reader = createBrowserTts();
    assert.equal((await reader.listVoices()).length, 1);
    await assert.rejects(reader.speak('私人文本', { voiceURI: 'remote' }), /local voice/);
    const reading = reader.speak('你好');
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(utterance.voice, local);
    reader.stop();
    assert.deepEqual(await reading, { cancelled: true });
    reader.dispose();
  } finally { delete globalThis.window; }
});

test('rapid replacement cancels old text while new text completes', async () => {
  const pending = [];
  globalThis.window = {
    speechSynthesis: {
      getVoices: () => [{ voiceURI: 'local', lang: 'en-US', localService: true }],
      cancel() {}, pause() {}, resume() {}, speak(value) { pending.push(value); }
    },
    SpeechSynthesisUtterance: class { constructor(text) { this.text = text; } }
  };
  try {
    const reader = createBrowserTts();
    const first = reader.speak('First.', { lang: 'en-US' });
    await new Promise(resolve => setImmediate(resolve));
    const second = reader.speak('Second.', { lang: 'en-US' });
    await new Promise(resolve => setImmediate(resolve));
    assert.deepEqual(await first, { cancelled: true });
    assert.equal(pending[0].onend, null);
    pending[1].onend();
    assert.deepEqual(await second, { cancelled: false });
  } finally { delete globalThis.window; }
});

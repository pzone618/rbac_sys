/** Browser-only, framework-independent. Owns the page's global speech queue. */
export function splitText(text, maxLength = 180) {
  if (typeof text !== 'string' || !text.trim()) throw new Error('Text is empty.');
  if (!Number.isInteger(maxLength) || maxLength < 1) throw new Error('Invalid chunk size.');
  const sentences = typeof Intl !== 'undefined' && Intl.Segmenter
    ? [...new Intl.Segmenter(undefined, { granularity: 'sentence' }).segment(text)].map(s => s.segment)
    : text.match(/[^。！？.!?\n]+[。！？.!?\n]*/gu) || [text];
  const chunks = [];
  for (const sentence of sentences) {
    const points = Array.from(sentence);
    for (let i = 0; i < points.length; i += maxLength) {
      const chunk = points.slice(i, i + maxLength).join('').trim();
      if (chunk) chunks.push(chunk);
    }
  }
  return chunks;
}

export function createBrowserTts({ offlineOnly = true, onState = () => {} } = {}) {
  if (typeof window === 'undefined' || !window.speechSynthesis) throw new Error('Browser speech synthesis is unavailable.');
  const engine = window.speechSynthesis;
  let generation = 0;
  let pending = null;
  let currentUtterance = null;
  let active = false;
  const emit = state => onState(state);

  async function listVoices() {
    if (!engine.getVoices().length) {
      await new Promise(resolve => {
        let timer;
        const finish = () => {
          clearTimeout(timer);
          engine.removeEventListener('voiceschanged', finish);
          resolve();
        };
        engine.addEventListener('voiceschanged', finish, { once: true });
        timer = setTimeout(finish, 1500);
        if (engine.getVoices().length) finish();
      });
    }
    return engine.getVoices().filter(v => !offlineOnly || v.localService);
  }

  function stop() {
    generation++;
    active = false;
    if (currentUtterance) currentUtterance.onend = currentUtterance.onerror = null;
    currentUtterance = null;
    engine.cancel();
    if (pending) pending();
    pending = null;
    emit('idle');
  }

  async function speak(text, { voiceURI, lang = 'zh-CN', rate = 1 } = {}) {
    const chunks = splitText(text);
    if (!Number.isFinite(rate) || rate < 0.5 || rate > 2) throw new Error('Rate must be between 0.5 and 2.');
    stop();
    const token = generation;
    active = true;
    emit('loading');
    try {
      const voices = await listVoices();
      if (token !== generation) return { cancelled: true };
      const voice = voiceURI
        ? voices.find(v => v.voiceURI === voiceURI)
        : voices.find(v => v.lang.toLowerCase() === lang.toLowerCase())
          || voices.find(v => v.lang.split('-')[0] === lang.split('-')[0]);
      if (!voice) throw new Error(offlineOnly ? 'No matching local voice. Install a voice or use prepared audio.' : 'No matching voice is available.');
      for (const chunk of chunks) {
        if (token !== generation) return { cancelled: true };
        await new Promise((resolve, reject) => {
          const utterance = new window.SpeechSynthesisUtterance(chunk);
          currentUtterance = utterance;
          utterance.voice = voice;
          utterance.lang = voice.lang;
          utterance.rate = rate;
          pending = resolve;
          utterance.onend = () => { pending = null; currentUtterance = null; resolve(); };
          utterance.onerror = event => { pending = null; currentUtterance = null; reject(new Error(event.error || 'Speech failed.')); };
          emit('speaking');
          engine.speak(utterance);
        });
      }
      if (token !== generation) return { cancelled: true };
      active = false;
      emit('idle');
      return { cancelled: false };
    } catch (error) {
      if (token !== generation) return { cancelled: true };
      stop();
      emit('error');
      throw error;
    }
  }

  return {
    listVoices, speak, stop,
    pause() { if (active) { engine.pause(); emit('paused'); } },
    resume() { if (active) { engine.resume(); emit('speaking'); } },
    dispose: stop,
    capabilities: Object.freeze({ exportAudio: false, localVoicesOnly: offlineOnly, wordTimestamps: false })
  };
}

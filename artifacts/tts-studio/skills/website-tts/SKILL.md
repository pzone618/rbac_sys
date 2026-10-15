---
name: website-tts
description: Add specified-text read-aloud and text-to-audio generation to websites, or generate reusable speech assets using local or cloud engines. Use for TTS selection, offline speech, playback controls, and audio export.
---

# Website TTS

Inspect the current website and reuse its framework and components. Separate live reading, audio file generation, and offline synthesis. Preserve a requested voice/provider; otherwise use the sourced [engine guide](references/engines.md) to choose based on language, target hardware, latency and export needs.

## Implement

- Static text: generate reusable audio during development/build and ship it with the site. Dynamic text: use browser reading or a backend synthesis endpoint. The installed plugin is a development tool, not the deployed site's backend.
- Browser reading: adapt [the reusable module](assets/browser-tts.mjs). It offers explicit voice selection, local-only filtering, sentence chunks, cancellation and pause/resume. Browser speech exposes no standard audio-file export. `localService` is a useful filter, not a substitute for a real disconnected-device test. Missing local voices must produce an actionable error.
- Audio generation: use MCP `tts_doctor`, `tts_voices`, `tts_synthesize`, `tts_synthesize_batch`; when tools are unavailable execute [the bundled CLI](../../server/tts_server.py) using its absolute path. For environment/model setup read [runtime setup](references/runtime.md).
- Synthesis defaults to offline-only. A user's explicit cloud-provider request authorizes online synthesis within that request; pass `offline_only=false`. Never silently change providers, upload offline text or retry a potentially billed request after an ambiguous failure.
- For long content use tts_synthesize_batch to generate cached clips and a playlist (up to 100000 characters). Individual clips accept at most 3000 characters; DashScope Qwen-TTS accepts at most 600. Youdao is limited to English word/short-phrase lookups and is not a paragraph engine. Preserve dates, numbers, abbreviations and Chinese/English mixed text when preparing input.
- For neural browser offline inference, use a Worker and explicit model download/cache progress. Model, tokenizer, phonemizer and WASM assets must all be available locally before claiming offline readiness. See the engine guide for sherpa WASM and kokoro-js; neither is bundled in this version.

## Website behavior

Provide a user-triggered play button, pause/resume/stop controls, accessible labels and visible loading/error state. Stop prior reading when a new text is selected or the route unmounts. Do not autoplay on page load. For generated audio, native `<audio controls>` is a useful baseline; revoke generated object URLs on disposal.

Cloud secrets stay in server-side environment variables. Add authentication, per-user limits and input limits to a deployed synthesis endpoint using the project's existing patterns. The MCP process is not an HTTP endpoint and should not be exposed to site visitors. Do not add a local bridge by default.

Capabilities differ: word timestamps, SSML, streaming, cloning and speed controls are provider/model specific. The current MCP adapters return complete files; do not claim live streaming or timed highlighting. Use real timing metadata for text highlighting, not estimated word durations.

## Verify

Exercise the site's actual playback path with Chinese, English, mixed text, dates/numbers and punctuation. Check stop, rapid text switching, missing voices, unavailable network and mobile playback. For offline requirements, prepare assets then disconnect and test on the target device. Report adapter implementation, configuration presence, generated-file validation and subjective listening as distinct evidence. Check the selected model's license separately from its inference engine when distributing it.

Prefer explicit engine selection for macOS/Linux; do not default to Windows. Edge is the preferred user-familiar online candidate, Youdao is for English pronunciation, DashScope provides a domestic-region Qwen-TTS option, and sherpa is the cross-platform offline path. See runtime.md for personal installation and installed-voice checks. The catalogue is broader than implemented adapters.

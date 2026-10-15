# Youdao investigation — 2026-10-15

Source project: `C:/Work/dev/leon-reboot-system`. Read-only inspection; no source files changed.

## Actual integration

- `backend/app/services/tts/engine_youdao.py:21`: calls `http://dict.youdao.com/dictvoice`; no app ID, signing secret or paid TTS SDK. Frontend direct calls use HTTPS.
- `engine_youdao.py:87`: maps en-GB to type=1, other locales to type=0. `frontend/src/components/ielts/WordHoverCard.tsx:100` uses type=1 for UK and type=2 for US instead. Current samples show type=0 and type=2 returned identical bytes for hello and good morning; this is observed behavior, not an official API guarantee.
- `engine_youdao.py:103`: forwards the entire input as the audio query value. It does not split paragraphs or perform local synthesis. The URL is interpolated without explicit query-value encoding.
- `engine_youdao.py:187`: returns response bytes as MP3; sample rate is hardcoded to 22050. duration_ms records request elapsed time, not decoded audio duration. rate/pitch/volume/output_format arguments do not change the request.
- `frontend/src/lib/dictionaryUtils.ts:126`: routes current reading through the v2 API, makes a Blob URL, caches it in memory and deduplicates in-flight requests. This is not persistent offline audio caching.
- `backend/app/api/v2/endpoints/tts.py:145` and `:316`: both reading and export automatically fall back to edge-tts, then pyttsx3. A successful result requested as youdao can therefore originate from another provider.
- Non-streaming responses expose actual provider through X-TTS-Engine and fallback through X-TTS-Note. `frontend/src/lib/api.ts:426` and `:471` return a Blob/delegate and do not propagate these headers to callers.
- `/export` wraps the returned bytes in a downloadable attachment; it does not establish that Youdao itself synthesized arbitrary text.

## Direct endpoint checks

Made HTTPS requests directly to dict.youdao.com, bypassing the application and its fallback. Harmless English input only. Word/phrase/sentence matrix used types 0, 1 and 2 with browser-like request headers.

| Input | type=0 | type=1 | type=2 |
|---|---|---|---|
| hello | HTTP 200, MP3 signature, 10605 bytes | HTTP 200, MP3 signature, 11565 bytes | HTTP 200, MP3 signature, 10605 bytes |
| good morning | HTTP 200, MP3 signature, 18720 bytes | HTTP 200, MP3 signature, 22080 bytes | HTTP 200, MP3 signature, 18720 bytes |
| This is a test of English text reading. The final word is pineapple. | HTTP 500 | HTTP 500 | HTTP 500 |

An initial longer paragraph with type=2 also returned HTTP 500. Returned MP3 files and JSON results are in `.local/youdao-investigation/`. No subjective listening or speech transcription was performed. Results describe this endpoint, network and test time; they do not establish a universal sentence-length limit, all possible supported phrases or historical behavior. The backend currently uses HTTP, while these tests deliberately used HTTPS.

## Interpretation for TTS Studio

The implementation is a keyless online dictionary-voice adapter, distinct from Youdao Zhiyun paid/trial TTS and local EmotiVoice. Source comments call audio human recordings, but the code and MP3 signatures alone do not establish how every returned clip was produced.

Treat it as an English word/phrase audio provider. Allow saving successful response audio. Do not promise arbitrary-text synthesis or offline generation. For broader text reading use explicit Edge/cloud/local selection, and always preserve requestedProvider, actualProvider and fallbackReason. Network fallback must remain inside the user's online/offline policy. The observed app fallback is a plausible explanation for successful long text under a Youdao selection, not proof of which provider produced a particular historical playback.

Potential adaptations should encode query parameters, use verified HTTPS, validate audio, report real capabilities and measured metadata, and avoid inheriting the existing verify=False/HTTP workarounds. This investigation did not modify or republish TTS Studio.

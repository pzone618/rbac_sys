# Verification — 0.2.0, 2026-10-15

- 21 Python tests passed, including real MP3 decoding from a generated fixture, fake ID3 rejection, truncated WAV rejection, corrupted-cache recovery, Edge proxy/request contracts, Youdao query encoding, DashScope request/download isolation, macOS command construction, batch resume and failure-stop behavior.
- 4 Node browser-module tests passed; skill frontmatter validator passed.
- Actual MCP subprocess smoke tests passed on Windows Python 3.12 and an existing Linux WSL distribution: initialization, five-tool discovery, doctor, catalog, invalid params and offline policy. Linux tested startup/protocol only, not audio synthesis.
- Personal marketplace preparation was tested in workspace `.local/tts-studio-install-test`: complete plugin copy and absolute-interpreter MCP configurations generated. No global host installation or configuration was changed.
- Actual Youdao adapter request: `good morning`, en-US, returned a 18720-byte MP3. FFmpeg decoded duration 0.936 seconds. No provider fallback.
- Actual Edge adapter request: `Hello. Welcome to TTS Studio.`, en-US-AriaNeural, returned a 25776-byte MP3. FFmpeg decoded duration 4.296 seconds. The initial 7.2.8 client received HTTP 403; upgrading the isolated environment to current 7.3.1 resolved it. requirements.txt pins the working client. This does not guarantee future or other-network availability.
- Tests used isolated workspace Python dependencies, not the global environment. FFmpeg came from imageio-ffmpeg 0.6.0. No subjective listening evaluation was performed.
- macOS say adapter command construction was tested with a mock; actual macOS speech, installed-voice behavior and Apple Silicon neural performance remain unverified because no Mac is attached.
- DashScope Beijing/Singapore Qwen-TTS WAV contract and signed-download handling were tested with simulated responses and verified against official API documentation. No paid credentials were available, so no real DashScope billing, latency or account/model availability was tested. Other paid adapters remain at their prior verification level.
- No sherpa model weights were installed; resident-model caching and real neural synthesis require target-model integration testing. No browser UI/mobile/disconnected-device test was performed.
- Context7 Edge and DashScope excerpts are in `research/edge-v020.txt` and `research/dashscope-v020.txt`; the current Qwen-TTS official API was additionally opened to verify the 600-character limit, input body and output audio URL.

## Historical 0.1.0 verification

- Python 3.12.4, Windows; Node 22.17.1.
- 10 Python tests passed: MCP initialization/tool discovery/doctor/catalog calls over actual stdio; offline network prohibition; invalid inputs; cache behavior; Azure SSML escaping; ElevenLabs and Speech API request contracts; invalid audio rejection; local-only sherpa paths; sanitized unexpected errors.
- 4 Node tests passed: Unicode/multilingual splitting, SSR failure, local-only voice filtering, cancellation, rapid reading replacement and completion.
- Skill frontmatter validator passed.
- Actual Windows SAPI enumeration returned David, Zira, Haruka, Huihui and Tracy.
- Actual local synthesis: Huihui Chinese/date/amount/English sample generated a 581728-byte, 22050 Hz WAV lasting 13.190 seconds. Zira English sample generated a 301624-byte, 22050 Hz WAV lasting 6.839 seconds. Repeating the Huihui request hit cache with identical file SHA-256. Samples remain in workspace `.local/tts-studio-verification/`, outside the plugin archive.
- SAPI enumeration/synthesis needed execution outside this session's sandbox; the sandbox restricted the speech service. This is an execution environment limitation, not evidence that no local voices are installed.
- No subjective listening evaluation was performed. No target-browser UI, mobile or disconnected-device test was performed; browser tests use a mock speech engine.
- sherpa-onnx and model weights are not installed in this environment. Constructor/API shape was checked against Context7 official-documentation excerpts; real neural synthesis remains unverified.
- Cloud environment credentials were absent. Cloud HTTP payloads were tested using simulated responses; no real cloud synthesis, billing, latency or account permissions were exercised.
- No global environment, project MCP configuration, or model download was changed. Account saving and target-host installation/tool activation are separate steps.

## Sources

Context7 library search plus context retrieval was used for sherpa, Kokoro, Piper, Qwen3-TTS, CosyVoice, F5-TTS, Azure Speech, ElevenLabs and Google Cloud TTS. Raw results are in `research/`. Official web sources supplemented current Piper upstream, hosted Chinese services, Polly, OpenAI, Gemini and specialist models. The catalogue records canonical links; false matches and failed Context7 queries are explicitly noted in the engine guide.

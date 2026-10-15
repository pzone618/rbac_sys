# Audio/video with synchronized transcripts

Use for listening practice, transcript navigation and timed loops. Separate media language, subtitle language and interface locale. Inspect the existing player and subtitle pipeline before choosing libraries. Establish supported sources (local file, URL, stream) and subtitle formats; native text tracks consume WebVTT, while SRT or other formats need explicit parsing/conversion. Do not claim arbitrary subtitle support.

## State and timing contract

Use the media element/player's reported playback position as the authoritative clock. Never advance subtitles using an independent elapsed-time counter. Track metadata readiness, paused/playing, seeking, buffering, ended and errors distinctly; handle rejected play requests and unavailable seek ranges. Remove listeners and release object URLs on source change/unmount.

Normalize cues to stable IDs, start/end seconds and text. Validate malformed times and encoding; support legitimate overlapping cues rather than silently deleting them. Define boundary membership, normally start-inclusive/end-exclusive, and highlight all active cues when overlaps are supported. Native `cuechange` and `activeCues` can drive highlighting when tracks are available; custom renderers derive active cues from media time.

Define subtitle offset explicitly, for example cue time = media time - offset; positive offset delays displayed subtitles. A click seeking to that cue then targets cue start + offset, bounded by the source's seekable range. Use the same convention for loop boundaries and display. Render subtitle text through safe text/markup handling rather than injecting untrusted HTML.

## Actions and loops

Specify whether clicking a cue seeks only or also starts playback. Provide keyboard-operable cue actions, clear current-cue indication and playback-rate controls if requested. Auto-follow should pause when the user deliberately scrolls away and offer an explicit return-to-current-cue action; avoid constantly stealing focus or announcing every timestamp to screen readers.

Separate repeat-all, repeat-cue, play-cue-once and A-B loop modes. Establish behavior for gaps, overlaps, selection changes, finite repeat counts and end-of-media. Validate A < B and valid seek ranges; prevent repeated seeks while one is already pending. Disable native full-media loop when it conflicts with a segment controller. Pause must remain paused. Switching source resets incompatible loop state.

`timeupdate` is not a precision timer. Choose scheduling appropriate to the requested tolerance, using playback events and available frame/animation callbacks for foreground updates as needed. Browser scheduling, buffering, seeking and background tabs limit precision; do not promise sample-accurate loops. For tight audio editing requirements, assess a specialized audio pipeline separately rather than silently expanding the player.

## Acceptance evidence

Use short licensed or synthetic fixtures with known cue boundaries. Exercise click-to-seek, pause/resume, seeking across cues, subtitle offset, cue gaps/overlaps, rate changes, first/last cue, segment completion, buffering and source replacement. State the acceptable loop overshoot/timing tolerance and measure it when precision matters. Include malformed subtitles, absent subtitles and play/seek failure. Check transcript readability and controls on mobile and in each relevant theme. Distinguish a mocked player from actual media playback.

Official MDN documentation checked with Context7 on 2026-10-15:
- https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/currentTime
- https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/timeupdate_event
- https://developer.mozilla.org/en-US/docs/Web/API/TextTrack/cuechange_event

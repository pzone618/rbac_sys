# Video browsing and playback sites

Separate browsing/search, video detail/player and playlist/episode journeys. Determine the source contract: ordinary media files, adaptive streams or provider embeds have different capabilities. Inspect the chosen player/provider and verify its API with Context7 before promising quality selection, captions, fullscreen, picture-in-picture or seek control. Do not bypass cross-origin embed boundaries.

Design cards with useful title, duration, poster and metadata; give search/filter/sort clear behavior and avoid loading every media source in a grid. Provide poster/image fallbacks and deliberate pagination or incremental loading. Keep recommendations and sample engagement metrics explicitly mocked when no service exists.

On the detail page, prioritize playback, title, context and episode navigation. Distinguish loading, buffering, autoplay blocked, source unavailable and unsupported playback. Use an explicit user gesture where playback requires it. Handle player events as authoritative state and clean up the previous player on route/video changes. Keep subtitle language and interface locale independent. Read [media-transcripts.md](media-transcripts.md) when timed transcript controls are required.

Define resume policy, progress save cadence and completed-video behavior. Key progress by video identity and account where applicable; do not carry one video's position into another. Respect deliberate replay and changed source duration. Define whether next-item playback is automatic or user-controlled; communicate countdown/cancel behavior when present. Scope offline/download features separately.

On mobile, verify inline/fullscreen transitions, orientation, touch controls and controls obscured by browser UI. Keyboard shortcuts must not fire while typing or override unrelated controls. Caption overlays must remain readable without colliding with playback controls. Test the chosen provider's actual capabilities; a desktop prototype does not establish iOS/Android behavior.

Acceptance: browse to play, search with no results, source error/retry, switch episode while playing, resume/replay, next-item cancel, subtitle choice and supported fullscreen behavior. Distinguish UI prototypes from production streaming: hosting, transcoding, adaptive delivery, DRM and recommendation services require their own authorized implementation.

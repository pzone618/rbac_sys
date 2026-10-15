# Mobile compatibility and responsive acceptance

Design for the primary mobile task rather than shrinking the desktop screenshot. Reuse project breakpoints, adding content-driven thresholds only where needed. Support small phones, a stressed intermediate width and desktop; include landscape when relevant. Example inspection widths such as 360, 390, 768 and 1280 CSS pixels are samples, not a guarantee of device coverage.

## Layout and input

- Make navigation, menus and dialogs usable by touch and keyboard without hover-only actions. Use appropriate input types and autocomplete. Do not disable pinch zoom.
- Keep important content and actions reachable with virtual keyboards open, browser bars changing height and display cutouts. Check scroll containers, safe-area insets, viewport-height assumptions and sticky/fixed regions. A fixed footer must not obscure focused fields or feedback.
- For tables, choose horizontal scrolling, priority columns or an equivalent row/card layout around the task. Keep essential information and actions available. Ensure charts and wide code blocks have intentional overflow behavior.
- Keep reading/focus order meaningful when rearranging layouts. Preserve modal focus behavior and accessible names in mobile navigation.
- Make touch targets comfortably usable; a practical design target is around 44 by 44 CSS pixels where space permits. WCAG 2.2 AA target-size minimum is 24 by 24 CSS pixels with specified exceptions and spacing alternatives; do not describe 44 pixels as the AA minimum.

## Acceptance

Inspect the primary journey with long supported translations, text enlargement, empty/error states and at least the most stressful theme combination. Check reflow at 320 CSS pixels where applicable, allowing genuinely two-dimensional content such as data tables its scoped exception. Look for accidental page-level horizontal scrolling, clipping and hidden controls.

Use available browser emulation to inspect viewport and touch behavior, and relevant desktop/browser checks already required by the project. Report emulation accurately: it does not establish physical-device keyboard, safe-area or browser behavior. If target Safari/iOS or Android devices cannot be tested, state that limitation rather than claiming compatibility.

Sources checked on 2026-10-15:
- https://tailwindcss.com/docs/responsive-design (Context7)
- https://www.w3.org/TR/WCAG22/ (1.4.10, 2.5.8)

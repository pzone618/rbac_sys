# Themes and color-vision accessibility

Use for multi-theme design, comfortable reading styles or color-vision requirements. Preserve the existing theme implementation. Propose only modes that fit the request; do not force a theme switcher into every website.

## Independent preferences

Separate appearance (for example light, dark or soft reading), contrast preference and chart encoding. Provide system-following and explicit appearance choices when requested. A manual choice should persist and override the system appearance; system-following should respond to OS changes. Switching appearance must not reset locale, navigation or contrast choice.

Use semantic surface/text/border/action/status/focus tokens across components, portals, charts and native controls. Validate foreground/background pairs per theme. A soft reading style may use warm surfaces, comfortable type and restrained motion while retaining contrast. Call it comfortable or soft reading; do not promise medical eye protection or equate lower contrast with comfort.

With Tailwind v4, runtime CSS variables can hold theme values, with `@theme inline` exposing appropriate utilities and a custom variant targeting `data-theme` if needed. Follow the installed framework's SSR/CSP pattern to establish initial theme without visible flashing or hydration mismatches. Do not access browser storage during server rendering. Handle unavailable storage gracefully. Use `color-scheme` appropriately for native controls.

## Color vision and contrast

Every mode must convey meaning through more than hue: add labels/icons to statuses, underlines or other cues to links, and shapes/line styles/patterns or direct labels to charts. Include distinguishable series and selected/focused states. A universal 'colorblind palette' cannot cover all users; choose palettes for the actual content and supplement them with redundant encoding. Avoid whole-page color filters that distort assets and status meanings.

Offer a color-vision-friendly chart palette when useful, and evaluate red/green and blue/yellow deficiencies using available simulation. A simulation is a diagnostic aid, not proof of accessibility or a substitute for user feedback. Do not infer a user's condition.

Target WCAG 2.2 AA where applicable: normal text contrast at least 4.5:1, large text 3:1, and required non-text visual information 3:1 against adjacent colors. Respect the criteria's scope and exceptions. Check focus, borders that identify controls, status colors and chart elements, not only body text. Honor `forced-colors`, contrast and reduced-motion preferences; avoid globally disabling forced color adjustment to preserve branding.

## Verification

Check each supported theme across ordinary, focus, error, selected and disabled states as relevant; check overlays/charts as well as the main page. Exercise initial load, reload, route changes, system-following updates and manual override persistence. Test relevant appearance/contrast intersections. Record measured ratios and simulated results separately from visual judgment. Do not claim WCAG certification from automated checks.

Sources checked on 2026-10-15: Context7 for responsive/forced-color guidance; official web docs for dark mode after a focused Context7 lookup returned no matching documentation.
- https://tailwindcss.com/docs/dark-mode
- https://tailwindcss.com/docs/forced-color-adjust
- https://www.w3.org/TR/WCAG22/ (1.4.1, 1.4.3, 1.4.11)

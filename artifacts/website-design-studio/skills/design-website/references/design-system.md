# Composition and design continuity

## Establish a direction

Read existing tokens and representative pages first. A brand reference constrains expression; it does not prescribe all layout decisions. For a new site, choose typography, spatial rhythm, visual hierarchy and image treatment around its content and audience. Avoid treating large rounded cards, gradients or dark navigation as universal defaults.

Compare directions with the same representative page and content. Explain differences in scanability, density, emphasis and audience fit. Do not promise multiple full applications when a representative screen will resolve the choice.

## Tokens and components

Prefer semantic roles such as surface, text, muted text, border, accent and danger, with accessible foreground/background pairs. Define typography, spacing, radii, elevation and motion in the existing token system. Reference shared tokens in components instead of scattering independent values. Inherit the existing icon family and licensed fonts/assets.

For Tailwind v4, use documented `@theme` namespaces to expose utility-generating tokens. Use regular CSS variables for runtime theme values and `@theme inline` where utilities need to reference those values. Share a theme CSS file using imports when appropriate. Do not copy v4 configuration into a v3 project or reset all theme values without examining existing dependencies.

Official source, checked through Context7 on 2026-10-15: https://tailwindcss.com/docs/theme

## Layout and interaction

Design around content pressure. Choose breakpoints where navigation, forms or content stop fitting, and inspect intermediate widths. On mobile, prioritize essential data, offer deliberate table scrolling or alternative rows, and keep key actions reachable. Avoid hiding necessary information just to fit the viewport.

Specify relevant default, hover, focus, disabled, loading, empty, error and success states. A disabled button needs enough surrounding explanation for the user to understand how to proceed. Preserve labels, keyboard behavior and reduced-motion preferences. For Chinese interfaces, test mixed Chinese/Latin text, font fallback, line height and wrapping; do not assume English text metrics.

Choose meaningful imagery only when it supports the content. Use existing vector/icon systems for interface symbols. If images are generated or supplied, preserve their licensing/provenance information where applicable and include useful alternative text.

# Multilingual interface design

Use when the website supports multiple locales, a language switcher or RTL. Replying in the user's language is not evidence that the application is localized. Reuse the project's library, locale list, default locale, routing and translation conventions. Do not add i18next or extra languages solely because this reference mentions them.

## Content and preferences

- Externalize user-facing copy, validation messages, accessible names and image text alternatives into the existing resource structure. Translate whole messages with placeholders rather than joining sentence fragments. Use locale-specific plural rules; do not assume singular/plural covers every language.
- Use BCP 47 locale tags, an explicit missing-translation fallback and meaningful development diagnostics. Distinguish requested locale from resolved fallback. A fallback prevents blank UI but is not a completed translation.
- Use native language names in the switcher rather than country flags as language identifiers. Make it keyboard accessible. Preserve the current page, form state and unrelated preferences where practical; save explicit choice using the project's storage conventions. Treat initial detection precedence as a project decision, not a universal rule.
- Format dates, numbers, currency and units through locale-aware APIs. Language, currency and time zone are separate settings; do not infer all three from a locale. Keep machine identifiers and stored values stable.
- Update document `lang` and, for supported RTL locales, `dir`. Use CSS logical properties. Mirror directional navigation where appropriate, not logos, all icons or the entire UI. Handle mixed-direction identifiers with appropriate isolation.

## Layout and validation

Design buttons, tabs, navigation, dialogs and tables for translation expansion and wrapping. Check fonts, CJK line breaking, mixed scripts, truncation and zoom. Avoid fixed heights that clip translated text. Language switching must update portal content and accessible labels as well as visible page text.

Exercise each supported locale on a representative journey; include missing-key fallback, counts such as 0/1/2/many, formatting and reload persistence. Use pseudo-localization or long synthetic strings to expose clipping; label these as stress tests, not verified human translations. Test RTL only when supported or explicitly evaluating future readiness. Human review may still be needed for translation quality.

When using i18next, consult installed-version docs for `fallbackLng`, plural resources, `changeLanguage` and `dir`; adapt them to framework lifecycle and SSR conventions.

Official documentation checked via Context7 on 2026-10-15:
- https://www.i18next.com/principles/fallback
- https://www.i18next.com/translation-function/plurals
- https://www.i18next.com/overview/api

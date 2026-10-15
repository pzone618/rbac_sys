---
name: design-website
description: Design and refine website interfaces, compare visual directions, build clickable UI prototypes, or review visual quality and responsive behavior. Use with or without Figma references; adapts to existing project components and design systems.
---

# Website Design Studio

Turn the user's website intent into an inspectable visual result. Match their language. Support landing pages, content sites, commerce, dashboards and internal tools; do not assume every site is an admin dashboard.

## Choose the scope

- For ideas or exploration, show distinct visual directions and their tradeoffs. Do not install dependencies or change an application when only advice was requested.
- For a preview request, produce a viewable artifact using available local or host preview capabilities. Describe an image as a visual mockup, not a clickable prototype.
- For implementation, inspect repository instructions, framework versions, existing components and tokens before editing. Honor the existing stack; a new design does not justify a framework migration.
- For an existing-page review, prioritize observable usability and visual defects. Read [review.md](references/review.md).
- With Figma input, read [figma.md](references/figma.md) before interpreting or fetching the design.

Infer the audience, primary task, content, brand constraints and delivery target from context. Ask only for missing information that materially changes the result, and continue independent work. If told to explore first, avoid treating a proposed direction as a selection. For implementation without a selected style, choose a reasonable direction and state the assumption.

## Design and preview

Use [design-system.md](references/design-system.md) for tokens, composition and responsive decisions. If direction is open, normally offer two or three meaningfully different compositions using the same content and primary task. Vary information hierarchy, typography, density or navigation as appropriate, not just accent color. A narrow edit rarely needs alternatives.

Make the initial viewport communicate purpose and a primary action. Use plausible, clearly fictional sample content. Include long names and realistic data density where useful. Carry the selected direction into supporting states and mobile layouts. Keep changes to one component local unless a shared token is responsible.

For a clickable prototype, implement the main journey with meaningful feedback: navigation, search/filter, modal open/close, form validation or another task-relevant interaction. Label mocked persistence or integrations. Do not attach destructive prototype actions to live data. Reuse accessible primitives already in the project.

Persist established design decisions in the project's existing design documentation or a small project-local design note when useful: selected direction, semantic tokens, reused components, layout rules and open decisions. This is the continuity mechanism; do not claim memory outside saved artifacts.

## Documentation and tools

Use available Context7 tools for library-specific implementation questions: resolve the library first, then query focused documentation matching installed versions. Record relevant source links and distinguish documentation evidence from recommendations. Do not send project secrets or proprietary source as search queries. If unavailable, disclose that and use official docs or local package documentation; do not invent a successful lookup.

Figma and browser tools are optional host capabilities, not tools supplied by this plugin. Discover what is actually callable. Without a browser, deliver a runnable preview and report visual checks as pending. Without Figma access, work from supplied screenshots/exports or proceed with an original design when authorized. No new account or service is required for the core workflow.

## Verify and hand off

Read [review.md](references/review.md) and perform checks proportionate to the task. For implementation, use the project's relevant build/type checks and inspect desktop and narrow-screen behavior when tools permit. Fix observed failures, then report what was verified and any limitations. A successful build alone is not evidence of visual fidelity.

Provide the artifact/preview location, design rationale, important interactions and verification status. Keep delivery concise. Do not publish a site or mutate Figma merely because a local design was requested.

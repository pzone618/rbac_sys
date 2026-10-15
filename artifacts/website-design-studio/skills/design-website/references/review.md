# Interface review and verification

Inspect the actual target artifact when available. Separate observed defects from inferred risks and unchecked behavior. Focus on problems affecting the user's primary task before cosmetic adjustments.

Check relevant items, rather than mechanically applying every item to a tiny edit:

- Purpose and hierarchy: clear page title, primary action, readable grouping, scannable content and reasonable density.
- Responsive content: narrow and desktop widths plus a stressed intermediate width; long labels, zoom and realistic row counts; overflow, navigation and sticky regions.
- Interaction: primary journey, error recovery, empty/loading states, filters with no matches, validation, modal escape/close and focus restoration.
- Accessibility: semantic landmarks/headings, labels, keyboard traversal, visible focus, dialog focus behavior, contrast, accessible names and reduced motion. Where measurable, target WCAG AA text contrast of 4.5:1 for normal text and 3:1 for large text; automated scans are partial evidence, not certification.
- Consistency: shared tokens/components, alignment, spacing, icon family, typography and cross-page behavior.
- Delivery: relevant project checks, missing assets, browser errors, preview accessibility and explicit mocked behavior.

For each material finding, give location, trigger, user impact and a concrete fix. Apply fixes when asked and recheck affected behavior. Avoid tests that simply assert implementation text or add snapshots for every visual adjustment. Preserve meaningful existing checks.

When matching Figma, compare the same viewport and variant using screenshot evidence. Separate reference fidelity from accessibility and behavior, since a screenshot cannot establish all three. Report any missing browser/Figma validation plainly.

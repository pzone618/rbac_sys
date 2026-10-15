# PDF viewing pages

Choose the viewer around the task: a browser embed may suffice for simple display; controlled navigation/search requires a viewer integration. Reuse existing infrastructure and confirm supported browsers and worker/asset packaging before selecting a renderer. Do not rebuild a full PDF application by default.

Specify page navigation, zoom/fit-width, rotation, outline, search, text selection, links and downloads only as needed. Keep page number, total count and zoom state understandable. A canvas renders appearance; selectable/searchable text and clickable annotations are separate concerns. Scanned PDFs may lack text and need separately scoped OCR. Do not claim reading order or screen-reader accessibility from canvas/text-layer presence alone.

For PDF.js integrations, keep library and worker versions compatible, use documented APIs for the installed version, align canvas/text/annotation layers under scale and rotation, and manage loading/render tasks and cleanup. Cancel obsolete work on rapid page/source/zoom changes and prevent stale results replacing the current document. Render visible/nearby pages with bounded resources for long files rather than allocating every high-resolution canvas.

Provide progress, password-required/wrong-password, inaccessible source, malformed document and failed-render states when relevant. Use allowed asset/network loading conventions; do not bypass permissions. Store reading progress by document identity/version. Document controls may follow the app theme, while original page colors should remain intact unless the user explicitly chooses a separately evaluated viewing filter. Do not promise semantic PDF recoloring or preserved fidelity from blanket inversion.

On mobile, check fit-width readability, page changes, zoom/pan, toolbar space, orientation and nested scrolling. Verify one-page and long documents, searchable text and scanned samples, links, rapid navigation/zoom and source replacement. Report browser/device and accessibility limitations explicitly.

Official source checked through Context7 during the preceding design assessment on 2026-10-15; re-query installed-version APIs when implementing:
- https://github.com/mozilla/pdf.js

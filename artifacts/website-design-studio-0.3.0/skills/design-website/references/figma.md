# Optional Figma workflow

This is a Codex design workflow with Figma knowledge, not a plugin running inside the Figma editor. Figma is useful for precise reference extraction and team handoff; original website design does not require it.

## Access and reference extraction

1. Discover available Figma tools and their current schemas. Use the user's exact file/frame/node reference; a file link alone does not identify the intended screen. Read only the relevant scope. If necessary, inspect metadata to select a frame.
2. Fetch design context for the target node before implementing a Figma-driven page. With official tools this is commonly `get_design_context`; names and availability must be checked rather than assumed. If truncated, use metadata to split retrieval into relevant children and fetch their context.
3. Obtain the target variant's screenshot, either included in the context response or through the available screenshot tool. Use structure and screenshot together. A screenshot alone cannot establish component semantics or hidden interactions.
4. Extract variables/modes, text styles, Auto Layout direction/gaps/padding/alignment, sizing constraints, components/instances, variant properties, assets and any explicit prototype connections. Distinguish measured values from inferred behavior. Auto Layout is evidence for flex/grid behavior, not a reason to absolutely position the whole page.
5. Inspect existing source components and Code Connect mappings if available. Map design instances and variants onto those components and props. Treat generated example code as design evidence to adapt to the project's conventions, not a new architecture to copy blindly.
6. Compare the rendered target viewport to the reference. Record unresolved asset/font differences, intentional accessibility adjustments and responsive inferences. A single desktop frame does not define mobile behavior.

## Assets, mappings and writes

Use returned assets and verified asset URLs through permitted tooling. Do not invent file IDs, node IDs, download URLs or component mappings. Check icon/font availability and avoid silently substituting unrelated assets.

Reading designs does not authorize edits, publishing libraries, creating Code Connect mappings, or writing generated pages into Figma. Perform those only within an explicit user request and only using verified available write capabilities. Do not promise arbitrary Figma editing from a design-reading connection. If write tools are absent, deliver code and a handoff specification rather than claiming the Figma file changed.

If Figma is not connected, explain that direct inspection is unavailable and use screenshots or exports already provided. Suggest an optional Figma connection only when it helps the actual task. Do not make installation a prerequisite for unrelated design work or embed access tokens in a plugin.

## Handoff when requested

Provide frame/component names, semantic token mapping, variants and states, responsive rules, asset inventory and known deviations. This is a handoff document unless an actual Figma mutation succeeded. Avoid claiming pixel-perfect fidelity without comparison evidence.

Official sources, checked via Context7 on 2026-10-15:
- https://github.com/figma/mcp-server-guide
- https://github.com/figma/code-connect

Re-query current official documentation when implementing tool-specific behavior; these notes are workflow guidance rather than frozen API signatures.

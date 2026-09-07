# Create React Component

Create a new React component with TypeScript.

## Input

The user should provide: $ARGUMENTS

Parse from the arguments:
- Component name
- Component type (UI component, layout, form, etc.)
- Any props or features needed

## Steps

1. Determine the appropriate directory:
   - Shared/reusable UI components: `frontend/src/components/{ComponentName}/`
   - Feature-specific components: `frontend/src/features/{feature}/components/{ComponentName}/`
   - Layout components: `frontend/src/components/layout/`

2. Create the component file `{ComponentName}.tsx`:
   - Define a TypeScript interface for props (named `{ComponentName}Props`)
   - Export as a named export (not default)
   - Use functional component with proper typing

3. Create an `index.ts` barrel export in the component directory.

4. If the component can be composed from shadcn/ui primitives, import from `@/components/ui/` and compose.

5. Style exclusively with Tailwind utility classes. Use `cn()` from `@/lib/utils` for conditional classes.

## Conventions

- Named exports only, no default exports
- Props interface always defined and exported
- Component name matches file name exactly
- Keep components focused — one responsibility per component
- Use React.FC only if children are expected; otherwise type props directly
- Prefer controlled components for form elements
- **Always prefer shadcn/ui primitives** (Button, Input, Card, etc.) over custom HTML
- **Never use inline styles** — use Tailwind classes exclusively
- **Never modify `components/ui/`** — create wrappers in your component directory
- Use `class-variance-authority` (cva) for custom component variants
- Follow the design system rules defined in `/project:design`

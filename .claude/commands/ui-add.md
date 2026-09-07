# Add shadcn/ui Component

Add a shadcn/ui component to the project and optionally create a custom wrapper.

## Input

The user should provide: $ARGUMENTS

Parse from the arguments:
- Component name(s) from shadcn/ui registry (e.g., button, card, dialog, table, form)
- Whether to create a custom wrapper with project-specific defaults

## Steps

1. **Install the shadcn/ui component(s)**:
   ```bash
   cd frontend && npx shadcn@latest add {component_name}
   ```
   Multiple components can be installed at once:
   ```bash
   cd frontend && npx shadcn@latest add button card dialog
   ```

2. **Verify installation**:
   - Check that files were created in `frontend/src/components/ui/`
   - Ensure imports resolve correctly

3. **Create custom wrapper** (if requested or if project needs special defaults):
   - Create at `frontend/src/components/{ComponentName}/{ComponentName}.tsx`
   - Import the base shadcn/ui component from `@/components/ui/`
   - Add project-specific default props, variants, or compositions
   - Export with clear naming to distinguish from base component

4. **Show usage example** to the user.

## Available Components (common ones)

Layouts: accordion, card, collapsible, resizable, separator, tabs
Forms: button, checkbox, form, input, label, radio-group, select, switch, textarea, toggle
Feedback: alert, alert-dialog, dialog, drawer, popover, sheet, toast, tooltip
Data: avatar, badge, calendar, carousel, data-table, table
Navigation: breadcrumb, command, dropdown-menu, menubar, navigation-menu, pagination, sidebar

Full list: https://ui.shadcn.com/docs/components

## Conventions

- Never modify files in `components/ui/` directly — they are managed by shadcn CLI
- Create wrappers in `components/` for project-specific customization
- Use the `cn()` utility from `@/lib/utils` for conditional classes
- Follow the variant pattern with `class-variance-authority` for custom variants

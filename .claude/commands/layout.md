# Create Layout Template

Create a page layout using Tailwind + shadcn/ui components.

## Input

The user should provide: $ARGUMENTS

Parse from the arguments:
- Layout type: dashboard, sidebar, landing, auth, settings, etc.
- Key sections: header, sidebar, footer, main content area
- Responsive requirements

## Layout Templates

### Dashboard Layout
- Sidebar navigation (collapsible on mobile)
- Top header with breadcrumbs + user menu
- Main content area with max-width container
- Uses: `sidebar`, `navigation-menu`, `avatar`, `dropdown-menu`

### Auth Layout
- Centered card on a minimal background
- Logo/branding at top
- Form area with inputs + buttons
- Footer link (e.g., "Don't have an account?")
- Uses: `card`, `input`, `button`, `label`

### Landing/Marketing Layout
- Full-width hero section
- Responsive grid sections
- Sticky header with navigation
- Footer with links
- Uses: `navigation-menu`, `button`, `card`

### Settings Layout
- Sidebar navigation (vertical tabs)
- Content area with form sections
- Uses: `tabs`, `separator`, `form`, `card`

## Steps

1. **Create the layout component** at `frontend/src/components/layout/{LayoutName}Layout.tsx`:
   - Use Tailwind utility classes for structure (grid/flexbox)
   - Import shadcn/ui components for UI elements
   - Make responsive with Tailwind breakpoints (sm:, md:, lg:)
   - Accept children prop for content slot

2. **Create sub-components** as needed:
   - `Header.tsx` — navigation, user menu, theme toggle
   - `Sidebar.tsx` — navigation links, collapse state
   - `Footer.tsx` — links, copyright

3. **Set up responsive behavior**:
   - Mobile: stack vertically, hamburger menu for navigation
   - Tablet: collapsible sidebar
   - Desktop: full sidebar + content layout

4. **Wire into router**:
   - Create a route layout wrapper so pages within the layout share it
   - Use React Router's `<Outlet />` for nested routes

5. **Install required shadcn/ui components** if not already present.

## Conventions

- Layouts use full viewport height (`min-h-screen`)
- Main content area scrolls independently from sidebar/header
- Use `cn()` for conditional responsive classes
- Keep layout components free of business logic
- Use CSS Grid for page-level structure, Flexbox for component-level alignment

# Design System Conventions

Reference skill — defines the project's UI design rules. Use this as a constraint when creating components, pages, and layouts.

## Principles

1. **Consistency over creativity** — use existing shadcn/ui components before creating custom ones
2. **Utility-first** — compose with Tailwind classes, extract components only when a pattern repeats 3+ times
3. **Accessible by default** — all interactive elements must be keyboard-navigable and have ARIA labels
4. **Responsive-first** — design for mobile, enhance for desktop

## Component Rules

### When to use shadcn/ui directly
- Standard UI patterns (buttons, inputs, dialogs, tables, cards)
- Always prefer the shadcn/ui primitive over building from scratch

### When to create a custom component
- Composing multiple shadcn/ui primitives into a reusable pattern
- Domain-specific UI that doesn't exist in shadcn/ui
- When you need project-specific default props or variants

### Never do
- Modify files inside `components/ui/` (managed by shadcn CLI)
- Use inline styles — always use Tailwind classes
- Create deeply nested `div` soup — use semantic HTML elements
- Use arbitrary pixel values — stick to Tailwind spacing scale (4, 8, 12, 16, 20, 24...)
- Mix different color systems — always use CSS variable tokens

## Spacing Scale

Use consistent spacing following Tailwind defaults:
- `gap-1` / `p-1` = 4px (tight, between related items)
- `gap-2` / `p-2` = 8px (compact)
- `gap-3` / `p-3` = 12px (default between elements)
- `gap-4` / `p-4` = 16px (section padding)
- `gap-6` / `p-6` = 24px (card padding, section gaps)
- `gap-8` / `p-8` = 32px (page-level section separation)

## Typography

- Headings: `text-4xl`/`3xl`/`2xl`/`xl`/`lg` — use font-semibold or font-bold
- Body: `text-base` (16px) default, `text-sm` (14px) for secondary
- Caption/Meta: `text-xs` (12px) with `text-muted-foreground`
- Never skip heading levels (h1 → h3)

## Color Usage

- Primary actions: `bg-primary text-primary-foreground`
- Secondary actions: `bg-secondary text-secondary-foreground`
- Destructive: `bg-destructive text-destructive-foreground`
- Muted text: `text-muted-foreground`
- Borders: `border-border`
- Hover states: use opacity variants or shade tokens

## Responsive Breakpoints

- Mobile-first (base styles = mobile)
- `sm:` (640px+) — large phones landscape
- `md:` (768px+) — tablets
- `lg:` (1024px+) — desktop
- `xl:` (1280px+) — wide desktop
- Sidebar collapses below `lg:`
- Grid columns: 1 → `sm:2` → `lg:3` → `xl:4`

## File Organization

```
frontend/src/components/
├── ui/              # shadcn/ui primitives (DO NOT EDIT)
├── layout/          # Layout shells (Header, Sidebar, Footer)
├── forms/           # Reusable form patterns
├── data-display/    # Tables, lists, stats cards
└── {Feature}/       # Feature-specific composed components
```

## Applying This Skill

When other skills (component, page, layout) are invoked, follow these constraints automatically. If a created component violates these rules, fix it before reporting completion.

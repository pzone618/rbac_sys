# Configure UI Theme

Customize the design tokens and theme for the project.

## Input

The user may provide: $ARGUMENTS

Parse from the arguments:
- Brand colors (primary, accent, etc.)
- Typography preferences (font family, scale)
- Spacing/radius preferences
- Dark mode strategy (class-based toggle vs system preference)

## Steps

1. **Update CSS variables** in `frontend/src/index.css`:
   - Modify `:root` (light theme) and `.dark` (dark theme) sections
   - Key tokens to configure:
     - `--background`, `--foreground` (base colors)
     - `--primary`, `--primary-foreground` (brand color)
     - `--secondary`, `--accent`, `--muted` (supporting colors)
     - `--destructive` (error/danger)
     - `--border`, `--ring` (borders and focus rings)
     - `--radius` (border radius base)

2. **Configure Tailwind** in `tailwind.config.ts` or CSS:
   - Extend the theme if custom values are needed beyond CSS variables
   - Add custom font families if specified
   - Configure responsive breakpoints if non-standard

3. **Set up dark mode** toggle (if not already present):
   - Install: `npx shadcn@latest add dropdown-menu`
   - Create a ThemeProvider using `next-themes` or custom context:
     ```bash
     cd frontend && npm install next-themes
     ```
   - Create `frontend/src/components/ThemeProvider.tsx`
   - Create `frontend/src/components/ThemeToggle.tsx`
   - Wrap App with ThemeProvider

4. **Set up typography** (optional):
   - Install custom fonts via Google Fonts or local files
   - Configure font-family in CSS variables and Tailwind config
   - Set up consistent type scale (heading sizes, body text, captions)

5. **Verify**:
   - Check both light and dark modes render correctly
   - Verify contrast ratios meet WCAG AA standard for text colors

## Design Token Reference

```css
:root {
  --background: 0 0% 100%;        /* white */
  --foreground: 240 10% 3.9%;     /* near black */
  --primary: 240 5.9% 10%;        /* brand primary */
  --primary-foreground: 0 0% 98%; /* text on primary */
  --secondary: 240 4.8% 95.9%;
  --muted: 240 4.8% 95.9%;
  --accent: 240 4.8% 95.9%;
  --destructive: 0 84.2% 60.2%;
  --border: 240 5.9% 90%;
  --ring: 240 5.9% 10%;
  --radius: 0.5rem;
}
```

Colors use HSL format without the `hsl()` wrapper (shadcn convention).

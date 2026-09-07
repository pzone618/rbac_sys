# Initialize UI Framework

Set up Tailwind CSS + shadcn/ui in the frontend project.

## Steps

1. **Install and configure Tailwind CSS** (if not already set up):
   ```bash
   cd frontend && npm install -D tailwindcss @tailwindcss/vite
   ```
   - Add Tailwind plugin to `vite.config.ts`
   - Create/update `frontend/src/index.css` with `@import "tailwindcss"`
   - Remove any conflicting CSS resets

2. **Install and configure shadcn/ui**:
   ```bash
   cd frontend && npx shadcn@latest init
   ```
   - Style: Default (or user's preference)
   - Base color: Neutral (or user's preference)
   - CSS variables: Yes
   - Choose appropriate settings for the project

3. **Set up design tokens** in `frontend/src/index.css`:
   - Ensure CSS variables for colors, radius, spacing are defined in `:root` and `.dark`
   - Configure the color palette to match the project's brand if specified

4. **Verify path aliases** in `tsconfig.json`:
   - Ensure `@/*` maps to `./src/*` (required by shadcn/ui)
   - Update `vite.config.ts` resolve aliases to match

5. **Install common utility packages**:
   ```bash
   cd frontend && npm install clsx tailwind-merge class-variance-authority lucide-react
   ```
   - Create `frontend/src/lib/utils.ts` with the `cn()` helper:
     ```ts
     import { clsx, type ClassValue } from "clsx"
     import { twMerge } from "tailwind-merge"

     export function cn(...inputs: ClassValue[]) {
       return twMerge(clsx(inputs))
     }
     ```

6. **Test the setup**:
   - Add a simple shadcn/ui component (e.g., Button) to verify everything works
   - Start dev server and confirm styles render correctly

## Post-setup

Report to user:
- Tailwind version installed
- shadcn/ui components available via `npx shadcn@latest add <component>`
- Location of theme configuration
- How to toggle dark mode

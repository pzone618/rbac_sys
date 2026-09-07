# Create React Page

Create a new page/route with associated components.

## Input

The user should provide: $ARGUMENTS

Parse from the arguments:
- Page name / route path
- Page purpose (list, detail, form, dashboard, etc.)
- Data requirements (which API endpoints it uses)

## Steps

1. Create the page component at `frontend/src/pages/{PageName}/{PageName}.tsx`:
   - Import necessary hooks and components
   - Implement data fetching (React Query / SWR / useEffect as per project convention)
   - Include loading and error states
   - Compose with existing shared components where possible

2. Create `frontend/src/pages/{PageName}/index.ts` barrel export.

3. Register the route in the router configuration:
   - Add route entry in `frontend/src/router.tsx` (or equivalent routing config)
   - Use lazy loading for code splitting if appropriate

4. If the page needs API integration, create or update the API service:
   - Add API functions in `frontend/src/services/{resource}.ts`
   - Include proper TypeScript types for request/response

## Conventions

- Pages are top-level route components, not reusable
- Each page in its own directory
- Handle loading, error, and empty states
- Use shadcn/ui `Skeleton` component for loading states
- Use shadcn/ui `Alert` for error states
- Page components should orchestrate, not implement detail logic
- Use existing layout components (wrap with appropriate Layout from `@/components/layout/`)
- Style with Tailwind utilities, use `cn()` for conditional classes
- Follow responsive patterns: mobile-first, breakpoints at sm/md/lg/xl
- Follow the design system rules defined in `/project:design`

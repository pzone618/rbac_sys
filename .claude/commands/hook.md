# Create React Hook

Create a custom React hook with TypeScript.

## Input

The user should provide: $ARGUMENTS

Parse from the arguments:
- Hook name (should start with "use")
- Purpose (data fetching, state management, DOM interaction, etc.)
- API endpoints it needs to call (if applicable)

## Steps

1. Create the hook file at `frontend/src/hooks/{useHookName}.ts`:
   - Define proper TypeScript types for parameters and return value
   - Export as named export
   - Include JSDoc comment only if the hook's behavior is non-obvious

2. If it's a data-fetching hook:
   - Use the project's data-fetching pattern (React Query / SWR / custom)
   - Include loading, error, and data states in return type
   - Handle caching and revalidation as appropriate

3. If it needs API service functions, create or update `frontend/src/services/{resource}.ts`.

4. Add a basic test in `frontend/src/__tests__/{useHookName}.test.ts` if the logic is complex.

## Conventions

- Hook names always start with `use`
- Return an object (not array) when there are more than 2 return values
- Keep hooks composable — prefer composing small hooks over one large hook
- Don't mix concerns (data fetching + UI state) in a single hook
- Type the return value explicitly for better DX

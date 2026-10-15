# Local MCP credentials

The tracked `.mcp.json` contains environment references rather than credentials.
Claude Code supports `${VARIABLE}` expansion in MCP configuration. Other clients
must use their own documented environment/configuration mechanism; do not assume
they read this file or support identical interpolation.

Keep local values in `.local/mcp-secrets.json` (Git ignored):

```json
{
  "CONTEXT7_API_KEY": "replace-with-your-key",
  "RBAC_MCP_POSTGRES_URL": "postgresql://USER:PASSWORD@HOST:PORT/DATABASE",
  "RBAC_MCP_REDIS_URL": "redis://:PASSWORD@HOST:PORT/0"
}
```

Do not commit this file. It remains plaintext on this computer, not an encrypted
secret store. A managed secret store or environment injection can be used instead.

From the repository root in PowerShell, initialize the process environment and
launch the client from the same shell:

```powershell
. ./scripts/Initialize-McpEnvironment.ps1
claude
```

The helper does not print values, modify machine/user environment settings or
start services. It does not affect an already running application. A `.env` file
is not automatically loaded by this helper. If using another launcher, provide
these variables through that launcher's supported configuration.

Existing credentials were migrated into the ignored file during cleanup.
This migration does not revoke credentials or remove them from earlier commits.
Rotate previously exposed keys/passwords with their providers and update local
values. History rewriting is a separate coordinated operation; do not force-push
or rewrite shared history as part of ordinary configuration cleanup.

Documentation verified on 2026-10-15 through Context7:
- https://code.claude.com/docs/en/agent-sdk/mcp
- https://github.com/upstash/context7

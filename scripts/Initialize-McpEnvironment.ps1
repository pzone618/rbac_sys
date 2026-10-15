# Dot-source this script before launching the MCP client from this PowerShell.
$mcpSecretsPath = Join-Path $PSScriptRoot '../.local/mcp-secrets.json'
if (-not (Test-Path -LiteralPath $mcpSecretsPath -PathType Leaf)) {
    throw 'Create .local/mcp-secrets.json following docs/mcp-local-setup.md first.'
}
$mcpSecrets = Get-Content -LiteralPath $mcpSecretsPath -Raw | ConvertFrom-Json
$mcpVariableNames = @('CONTEXT7_API_KEY', 'RBAC_MCP_POSTGRES_URL', 'RBAC_MCP_REDIS_URL')
foreach ($mcpVariableName in $mcpVariableNames) {
    $mcpVariableValue = $mcpSecrets.$mcpVariableName
    if ($mcpVariableValue -isnot [string] -or [string]::IsNullOrWhiteSpace($mcpVariableValue)) {
        throw "Missing local MCP setting: $mcpVariableName"
    }
}
foreach ($mcpVariableName in $mcpVariableNames) {
    [Environment]::SetEnvironmentVariable($mcpVariableName, $mcpSecrets.$mcpVariableName, 'Process')
}
Remove-Variable mcpSecrets, mcpVariableValue

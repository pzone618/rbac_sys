param([Parameter(Mandatory=$true)][string]$RequestPath)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
Add-Type -AssemblyName System.Speech
$request = Get-Content -LiteralPath $RequestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    if ($request.action -eq 'voices') {
        $voices = @($synth.GetInstalledVoices() | ForEach-Object {
            @{ id = $_.VoiceInfo.Name; language = $_.VoiceInfo.Culture.Name; enabled = $_.Enabled; local = $true }
        })
        ConvertTo-Json -InputObject $voices -Compress
    } elseif ($request.action -eq 'synthesize') {
        if ($request.voice) { $synth.SelectVoice([string]$request.voice) }
        $synth.Rate = [int]$request.rate
        $synth.SetOutputToWaveFile([string]$request.output)
        $synth.Speak([string]$request.text)
        $synth.SetOutputToNull()
        '{"ok":true}'
    } else { throw 'Unknown action' }
} finally { $synth.Dispose() }

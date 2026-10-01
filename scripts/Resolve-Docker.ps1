function Invoke-StudyDocker {
    param([string[]]$Arguments, [int]$TimeoutSeconds = 20)
    $command = Get-Command docker.exe -CommandType Application -ErrorAction Stop
    foreach ($argument in $Arguments) {
        if ($argument.Contains('"') -or $argument.EndsWith('\')) { throw 'Unsupported Docker argument quoting.' }
    }
    $info = New-Object System.Diagnostics.ProcessStartInfo
    $info.FileName = $command.Source
    $info.Arguments = (($Arguments | ForEach-Object { '"' + $_ + '"' }) -join ' ')
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $info
    try {
        if (-not $process.Start()) { throw 'Docker process did not start.' }
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
            $process.Kill()
            $process.WaitForExit()
            return [pscustomobject]@{ ExitCode = -1; Stdout = ''; Stderr = 'Docker command timed out.' }
        }
        return [pscustomobject]@{ ExitCode = $process.ExitCode; Stdout = $stdout.GetAwaiter().GetResult(); Stderr = $stderr.GetAwaiter().GetResult() }
    } finally { $process.Dispose() }
}

function Wait-StudyDocker {
    param([int]$WaitSeconds = 120)
    if (-not (Get-Command docker.exe -CommandType Application -ErrorAction SilentlyContinue)) { throw 'Docker CLI was not found.' }
    $started = $false
    $timer = [Diagnostics.Stopwatch]::StartNew()
    $lastError = 'No local Linux engine has answered.'
    do {
        foreach ($context in @('default', 'desktop-linux')) {
            $inspection = Invoke-StudyDocker -Arguments @('context', 'inspect', $context) -TimeoutSeconds 5
            if ($inspection.ExitCode -ne 0) { continue }
            try { $metadata = @($inspection.Stdout | ConvertFrom-Json)[0] } catch { continue }
            $hostAddress = $metadata.Endpoints.docker.Host
            if ($hostAddress -notlike 'npipe:*') { continue }
            $reply = Invoke-StudyDocker -Arguments @('--context', $context, 'info', '--format', '{{json .}}') -TimeoutSeconds 5
            $lastError = $reply.Stderr.Trim()
            if ($reply.ExitCode -ne 0) { continue }
            try { $server = $reply.Stdout | ConvertFrom-Json } catch { continue }
            if ($server.ServerVersion -match '^\d+\.' -and $server.OSType -eq 'linux') {
                Write-Host ('DOCKER_LINUX_ENGINE_READY: context=' + $context + ', version=' + $server.ServerVersion)
                return @('--context', $context)
            }
            $lastError = 'A valid Linux Docker server response was not received. Check the Docker Desktop container mode.'
        }
        if (-not $started) {
            $started = $true
            $paths = @()
            if ($env:ProgramFiles) { $paths += Join-Path $env:ProgramFiles 'Docker\Docker\Docker Desktop.exe' }
            if ($env:LOCALAPPDATA) { $paths += Join-Path $env:LOCALAPPDATA 'Programs\DockerDesktop\Docker Desktop.exe' }
            $desktop = $paths | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
            if ($desktop) {
                Write-Host 'Starting Docker Desktop. Complete any first-run prompt in its window.'
                Start-Process -FilePath $desktop | Out-Null
            } else {
                Write-Host 'Docker Desktop was not found in the standard locations. Open it manually if installed elsewhere.'
            }
        }
        Write-Host 'Waiting for a local Linux Docker engine...'
        Start-Sleep -Seconds 3
    } while ($timer.Elapsed.TotalSeconds -lt $WaitSeconds)
    throw ('DOCKER_ENGINE_NOT_READY. Open Docker Desktop and inspect its status. No Mealie startup was attempted. Last diagnostic: ' + $lastError)
}

function Get-StudyPython {
    $candidate = Get-Command python -ErrorAction SilentlyContinue
    if ($candidate) {
        & $candidate.Source -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)"
        if ($LASTEXITCODE -eq 0) { return @{ Exe = $candidate.Source; Prefix = @() } }
    }
    $candidate = Get-Command py -ErrorAction SilentlyContinue
    if ($candidate) {
        & $candidate.Source -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)"
        if ($LASTEXITCODE -eq 0) { return @{ Exe = $candidate.Source; Prefix = @('-3') } }
    }
    throw 'Python 3.9 or newer was not found. Install Python and retry.'
}

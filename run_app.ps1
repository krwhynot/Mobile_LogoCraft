Set-Location -Path "R:\Projects\Python\Mobile_LogoCraft"
Write-Host "Starting Mobile LogoCraft..."
try {
    & .\.venv\Scripts\python.exe run.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Application exited with code $LASTEXITCODE" -ForegroundColor Red
    }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
